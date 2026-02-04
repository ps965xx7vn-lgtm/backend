"""
Reviewers Signals - Сигналы для уведомлений и автоматизации.

Этот модуль содержит сигналы для:
    - Уведомлений студентов о проверке работы
    - Уведомлений ревьюеров о новых работах
    - Автоматического создания Reviewer при присвоении роли
    - Инвалидации кэша

Автор: Pyland Team
Дата: 2025
"""

from __future__ import annotations

import logging

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from authentication.models import Reviewer
from reviewers.models import LessonSubmission

from .cache_utils import invalidate_reviewer_cache
from .models import Review, StepProgress

logger = logging.getLogger(__name__)


def check_and_send_certificate(student_profile, course):
    """
    Проверяет, завершил ли студент курс полностью, и отправляет сертификат.

    Курс считается завершенным, если:
        1. Все уроки имеют approved submissions
        2. Все шаги (steps) в уроках отмечены как completed (is_completed=True)

    При успешном завершении:
        1. Создаётся сертификат (если ещё не создан)
        2. Генерируется PDF
        3. Отправляется email студенту

    Args:
        student_profile: Профиль студента (Student)
        course: Объект курса (Course)
    """
    from django.utils import timezone

    from certificates.models import Certificate
    from certificates.tasks import send_certificate_email

    try:
        # Получаем все уроки курса
        all_lessons = course.lessons.all()
        total_lessons = all_lessons.count()

        if total_lessons == 0:
            logger.info(f"Course {course.id} has no lessons, skipping certificate check")
            return

        # Проверяем, сколько уроков выполнены (approved)
        approved_submissions = LessonSubmission.objects.filter(
            student=student_profile,
            lesson__course=course,
            status="approved",
        ).values_list("lesson_id", flat=True)

        approved_count = len(set(approved_submissions))  # Уникальные уроки

        logger.info(
            f"Student {student_profile.user.email}: "
            f"{approved_count}/{total_lessons} lessons approved in course {course.name}"
        )

        # ВАЖНО: Проверяем, что все уроки одобрены
        if approved_count < total_lessons:
            logger.info(
                f"Student {student_profile.user.email} has not completed all lessons yet "
                f"({approved_count}/{total_lessons})"
            )
            return

        # НОВАЯ ПРОВЕРКА: Проверяем, что все шаги в уроках пройдены
        from reviewers.models import StepProgress

        total_steps = 0
        completed_steps = 0

        for lesson in all_lessons:
            lesson_steps = lesson.steps.all()
            total_steps += lesson_steps.count()

            # Проверяем прогресс по каждому шагу
            for step in lesson_steps:
                step_progress = StepProgress.objects.filter(
                    profile=student_profile, step=step, is_completed=True
                ).first()

                if step_progress:
                    completed_steps += 1

        logger.info(
            f"Student {student_profile.user.email}: "
            f"{completed_steps}/{total_steps} steps completed in course {course.name}"
        )

        # Если НЕ все шаги пройдены - не выдаём сертификат
        if completed_steps < total_steps:
            logger.warning(
                f"⚠️  Student {student_profile.user.email} has approved all lessons "
                f"but not completed all steps ({completed_steps}/{total_steps}). "
                f"Certificate will NOT be issued until all steps are completed."
            )
            return

        # Если все уроки выполнены И все шаги пройдены - выдаём сертификат
        if approved_count >= total_lessons and completed_steps >= total_steps:
            # Проверяем, не создан ли уже сертификат
            existing_certificate = Certificate.objects.filter(
                student=student_profile, course=course
            ).first()

            if existing_certificate:
                logger.info(
                    f"Certificate already exists for student {student_profile.user.email} "
                    f"and course {course.name} (#{existing_certificate.certificate_number})"
                )
                return

            # Собираем статистику курса
            all_submissions = LessonSubmission.objects.filter(
                student=student_profile, lesson__course=course
            )

            lessons_completed = (
                all_submissions.filter(status="approved")
                .values_list("lesson_id", flat=True)
                .distinct()
                .count()
            )
            total_lessons = course.lessons.count()
            assignments_submitted = all_submissions.count()
            assignments_approved = all_submissions.filter(status="approved").count()

            # Считаем количество отзывов (reviews)
            from reviewers.models import Review

            reviews_received = Review.objects.filter(
                lesson_submission__student=student_profile, lesson_submission__lesson__course=course
            ).count()

            # Создаём новый сертификат со статистикой
            certificate = Certificate.objects.create(
                student=student_profile,
                course=course,
                completion_date=timezone.now().date(),
                lessons_completed=lessons_completed,
                total_lessons=total_lessons,
                assignments_submitted=assignments_submitted,
                assignments_approved=assignments_approved,
                reviews_received=reviews_received,
            )

            logger.info(
                f"Certificate created: #{certificate.certificate_number} "
                f"for student {student_profile.user.email}, course {course.name}"
            )

            # Генерируем PDF сертификата
            from certificates.utils import generate_certificate_pdf

            pdf_path = generate_certificate_pdf(certificate)
            logger.info(f"Certificate PDF generated: {pdf_path}")

            # Формируем URL для скачивания PDF
            pdf_url = f"{settings.SITE_URL}{settings.MEDIA_URL}{pdf_path}"

            # Отправляем email с сертификатом
            # Пытаемся через Celery, если недоступен - синхронно
            from certificates.tasks import send_certificate_email, send_certificate_email_sync

            try:
                # Проверяем, есть ли активные Celery workers
                from celery import current_app

                inspect = current_app.control.inspect()
                active_workers = inspect.active()

                if not active_workers:
                    raise Exception("No active Celery workers available")

                # Celery доступен - отправляем асинхронно
                send_certificate_email.delay(
                    student_email=student_profile.user.email,
                    student_name=student_profile.user.get_full_name()
                    or student_profile.user.username,
                    course_name=course.name,
                    certificate_number=certificate.certificate_number,
                    verification_code=certificate.verification_code,
                    pdf_url=pdf_url,
                    completion_date=certificate.completion_date,
                    lessons_completed=lessons_completed,
                    total_lessons=total_lessons,
                    assignments_submitted=assignments_submitted,
                    assignments_approved=assignments_approved,
                    reviews_received=reviews_received,
                    total_time_spent=float(certificate.total_time_spent),
                )
                logger.info(
                    f"Certificate email task added to Celery queue for {student_profile.user.email}"
                )
            except Exception as celery_error:
                logger.warning(f"Celery недоступен, отправляем email синхронно: {celery_error}")
                # Fallback: отправляем синхронно
                try:
                    send_certificate_email_sync(
                        student_email=student_profile.user.email,
                        student_name=student_profile.user.get_full_name()
                        or student_profile.user.username,
                        course_name=course.name,
                        certificate_number=certificate.certificate_number,
                        verification_code=certificate.verification_code,
                        pdf_url=pdf_url,
                        completion_date=certificate.completion_date,
                        lessons_completed=lessons_completed,
                        total_lessons=total_lessons,
                        assignments_submitted=assignments_submitted,
                        assignments_approved=assignments_approved,
                        reviews_received=reviews_received,
                        total_time_spent=float(certificate.total_time_spent),
                    )
                    logger.info(
                        f"✅ Certificate email sent synchronously to {student_profile.user.email}"
                    )
                except Exception as sync_error:
                    logger.error(
                        f"❌ Failed to send certificate email even synchronously: {sync_error}"
                    )

    except Exception as e:
        logger.error(f"Error checking course completion for certificate: {e}")


def invalidate_student_caches(student_profile, course=None):
    """
    Инвалидирует все кэши студента.

    Args:
        student_profile: Профиль студента (Student)
        course: Курс (опционально) - если указан, инвалидирует только его кэш
    """
    from students.cache_utils import safe_cache_delete

    # Инвалидируем основные кэши дашборда
    safe_cache_delete(f"dashboard_stats_{student_profile.id}")
    safe_cache_delete(f"user_courses_stats_{student_profile.id}")

    if course:
        # Инвалидируем кэш конкретного курса
        safe_cache_delete(f"course_progress_{course.id}_{student_profile.id}")
        for lesson in course.lessons.all():
            safe_cache_delete(f"lesson_progress_{lesson.id}_{student_profile.id}")
    else:
        # Инвалидируем все курсы студента
        for course in student_profile.courses.all():
            safe_cache_delete(f"course_progress_{course.id}_{student_profile.id}")
            for lesson in course.lessons.all():
                safe_cache_delete(f"lesson_progress_{lesson.id}_{student_profile.id}")

    logger.info(f"Invalidated cache keys for student {student_profile.id}")


@receiver(post_save, sender=Review)
def notify_student_on_review(sender, instance: Review, created: bool, **kwargs):
    """
    Отправляет уведомление студенту когда его работа проверена.

    Отправляет email студенту с информацией:
    - Статус проверки (approved/needs_work)
    - Оценка (если есть)
    - Комментарии ревьюера
    - Рекомендации по улучшению

    Срабатывает: После создания Review (created=True)
    Примечание: При повторной проверке старый Review удаляется и создается заново,
    поэтому created всегда будет True и email отправится студенту.
    """
    if not created:
        # Это не должно происходить, т.к. старый Review удаляется при resubmit
        logger.warning(
            f"Review {instance.id} обновлен (не создан). "
            f"Возможно, это ошибка в логике - Review должен удаляться при resubmit."
        )
        return

    try:
        submission = instance.lesson_submission
        student = submission.student

        # Проверяем, включены ли уведомления у студента
        if not student.course_updates:
            logger.info(
                f"У студента {student.user.email} отключены уведомления, "
                f"пропускаем уведомление о проверке работы {submission.id}"
            )
            return

        # Определяем цвета и текст в зависимости от статуса
        if instance.status == "approved":
            status_text = "Работа принята"
            status_emoji = "✅"
            header_color = "#10b981"  # green
            status_bg_color = "#ecfdf5"
            status_border_color = "#10b981"
            status_text_color = "#047857"
            status_title_color = "#065f46"
        elif instance.status == "needs_work":
            status_text = "Требуются доработки"
            status_emoji = "📝"
            header_color = "#f59e0b"  # amber
            status_bg_color = "#fffbeb"
            status_border_color = "#f59e0b"
            status_text_color = "#92400e"
            status_title_color = "#78350f"
        else:
            status_text = "Статус неизвестен"
            status_emoji = "❓"
            header_color = "#64748b"  # gray
            status_bg_color = "#f8fafc"
            status_border_color = "#64748b"
            status_text_color = "#475569"
            status_title_color = "#1e293b"

        # Получаем рекомендации по улучшению
        improvements = []
        if hasattr(instance, "improvements"):
            improvements = [
                improvement.improvement_text for improvement in instance.improvements.all()
            ]

        # Запускаем асинхронную задачу отправки email
        from reviewers.tasks import send_review_completed_notification

        student_name = student.user.get_full_name() or student.user.email

        # Пытаемся отправить уведомление через Celery
        try:
            send_review_completed_notification.delay(
                student_email=student.user.email,
                student_name=student_name,
                course_name=submission.lesson.course.name,
                lesson_name=submission.lesson.name,
                submission_id=str(submission.id),
                status=instance.status,
                status_text=status_text,
                status_emoji=status_emoji,
                comments=instance.comments,
                improvements=improvements,
                header_color=header_color,
                status_bg_color=status_bg_color,
                status_border_color=status_border_color,
                status_text_color=status_text_color,
                status_title_color=status_title_color,
            )

            logger.info(
                f"Задача уведомления студента {student.user.email} о проверке "
                f"поставлена в очередь (работа {submission.id}, статус: {instance.status})"
            )
        except Exception as celery_error:
            logger.warning(
                f"Не удалось поставить задачу уведомления в очередь Celery: {celery_error}. "
                f"Отправляем email синхронно."
            )

            # Fallback: отправляем синхронно
            try:
                from django.conf import settings
                from django.core.mail import EmailMessage
                from django.template.loader import render_to_string

                html_message = render_to_string(
                    "reviewers/email/review_completed.html",
                    {
                        "student_name": student_name,
                        "student_email": student.user.email,
                        "course_name": submission.lesson.course.name,
                        "lesson_name": submission.lesson.name,
                        "status": instance.status,
                        "status_text": status_text,
                        "status_emoji": status_emoji,
                        "comments": instance.comments,
                        "improvements": improvements,
                        "submission_url": f"{settings.SITE_URL}/students/submissions/{submission.id}/",
                        "header_color": header_color,
                        "status_bg_color": status_bg_color,
                        "status_border_color": status_border_color,
                        "status_text_color": status_text_color,
                        "status_title_color": status_title_color,
                    },
                )

                subject = f"{status_emoji} Ваша работа проверена: {submission.lesson.name}"
                text_message = (
                    f"Здравствуйте, {student_name}!\n\n"
                    f'Ваша работа по уроку "{submission.lesson.name}" проверена.\n\n'
                    f"Статус: {status_text}\n"
                )

                if instance.comments:
                    text_message += f"\nКомментарий ревьюера:\n{instance.comments}\n"

                text_message += f"\nПерейти к работе: {settings.SITE_URL}/students/submissions/{submission.id}/\n"

                email_msg = EmailMessage(
                    subject=subject,
                    body=text_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[student.user.email],
                )
                email_msg.content_subtype = "html"
                email_msg.body = html_message

                email_msg.send(fail_silently=False)
                logger.info(
                    f"Email о проверке успешно отправлен студенту {student.user.email} синхронно "
                    f"(работа {submission.id}, статус: {instance.status})"
                )
            except Exception as email_error:
                logger.error(
                    f"Не удалось отправить email студенту {student.user.email} даже синхронно: {email_error}"
                )

        # ВАЖНО: Инвалидируем кэш студента после изменения статуса submission
        invalidate_student_caches(student, course=submission.lesson.course)
        logger.info(f"Cache invalidated for student {student.user.email} after review")

        # Проверяем, завершил ли студент весь курс (все работы приняты)
        if instance.status == "approved":
            check_and_send_certificate(student, submission.lesson.course)

    except Exception as e:
        logger.error(f"Ошибка уведомления студента о проверке: {e}")


@receiver(post_save, sender=LessonSubmission)
def notify_reviewers_on_submission(sender, instance: LessonSubmission, created: bool, **kwargs):
    """
    Запускает асинхронную отправку уведомлений ревьюерам о новой работе студента.

    Уведомления отправляются только ревьюерам которые:
    - Активны (is_active=True)
    - Привязаны к курсу работы
    - Включили уведомления (notify_new_submissions=True)

    Отправка происходит асинхронно через Celery task.

    Срабатывает: При создании новой LessonSubmission
    """
    if not created:
        return

    try:
        course = instance.lesson.course
        student = instance.student

        # Находим активных ревьюеров этого курса с включенными уведомлениями
        reviewers = Reviewer.objects.filter(
            courses=course, is_active=True, notify_new_submissions=True
        ).select_related("user")

        if not reviewers.exists():
            logger.info(f"Нет ревьюеров с включенными уведомлениями для курса {course.name}")
            return

        # Собираем email адреса ревьюеров
        reviewer_emails = [r.user.email for r in reviewers]
        student_name = student.user.get_full_name() or student.user.email

        # Запускаем асинхронную задачу отправки email
        from reviewers.tasks import send_new_submission_notification

        try:
            send_new_submission_notification.delay(
                reviewer_emails=reviewer_emails,
                student_name=student_name,
                course_name=course.name,
                lesson_name=instance.lesson.name,
                lesson_url=instance.lesson_url,
                submission_id=str(instance.id),
            )

            logger.info(
                f"Создана новая работа: {instance.id} от {student.user.email} "
                f"для урока '{instance.lesson.name}' (курс: {course.name}). "
                f"Задача уведомлений поставлена в очередь для {reviewers.count()} ревьюеров"
            )
        except Exception as celery_error:
            logger.warning(
                f"Не удалось поставить задачу уведомления ревьюеров в очередь Celery: {celery_error}. "
                f"Отправляем email синхронно."
            )

            # Fallback: отправляем синхронно
            try:
                from django.conf import settings
                from django.core.mail import EmailMessage
                from django.template.loader import render_to_string

                subject = f"📝 Новая работа на проверку: {instance.lesson.name}"

                text_message = (
                    f"Новая работа на проверку\n\n"
                    f"Студент {student_name} отправил работу на проверку.\n\n"
                    f"Курс: {course.name}\n"
                    f"Урок: {instance.lesson.name}\n"
                    f"Ссылка на работу: {instance.lesson_url}\n\n"
                    f"Перейти к проверке: {settings.SITE_URL}/reviewers/submissions/"
                )

                success_count = 0
                for email in reviewer_emails:
                    try:
                        # Рендерим HTML для каждого ревьюера с его email
                        html_message = render_to_string(
                            "reviewers/email/new_submission.html",
                            {
                                "student_name": student_name,
                                "course_name": course.name,
                                "lesson_name": instance.lesson.name,
                                "lesson_url": instance.lesson_url,
                                "site_url": settings.SITE_URL,
                                "reviewer_email": email,
                            },
                        )

                        email_msg = EmailMessage(
                            subject=subject,
                            body=text_message,
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            to=[email],
                        )
                        email_msg.content_subtype = "html"
                        email_msg.body = html_message
                        email_msg.send(fail_silently=False)
                        success_count += 1
                    except Exception as email_error:
                        logger.error(f"Не удалось отправить email на {email}: {email_error}")

                logger.info(
                    f"Email уведомления отправлены синхронно: {success_count}/{len(reviewer_emails)} успешно "
                    f"(работа {instance.id})"
                )
            except Exception as email_error:
                logger.error(
                    f"Не удалось отправить email уведомления ревьюерам даже синхронно: {email_error}"
                )

    except Exception as e:
        logger.error(f"Ошибка в notify_reviewers_on_submission: {e}")


@receiver(post_save, sender=Review)
def invalidate_reviewer_cache_on_review(sender, instance: Review, **kwargs):
    """
    Инвалидирует кэш статистики ревьюера после создания проверки.

    Срабатывает: После сохранения Review
    """
    try:
        if instance.reviewer:
            invalidate_reviewer_cache(str(instance.reviewer.id))
            logger.info(f"Инвалидирован кэш для ревьюера {instance.reviewer.id} после проверки")
    except Exception as e:
        logger.error(f"Ошибка инвалидации кэша ревьюера: {e}")


@receiver(post_save, sender=StepProgress)
def invalidate_student_cache_on_progress(sender, instance: StepProgress, **kwargs):
    """
    Инвалидирует кэш студента при изменении прогресса по шагам.

    Срабатывает: После сохранения StepProgress (создание или обновление)
    """
    try:
        course = instance.step.lesson.course
        invalidate_student_caches(instance.profile, course=course)
        logger.info(
            f"Cache invalidated for student {instance.profile.id} "
            f"after step progress update (step: {instance.step.name})"
        )
    except Exception as e:
        logger.error(f"Ошибка инвалидации кэша студента при обновлении прогресса: {e}")


# Подключение сигналов происходит автоматически при импорте модуля
# Импорт должен быть в apps.py через ready()
