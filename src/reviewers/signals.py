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

from django.db.models.signals import post_save
from django.dispatch import receiver

from authentication.models import Reviewer
from reviewers.models import LessonSubmission

from .cache_utils import invalidate_reviewer_cache
from .models import Review

logger = logging.getLogger(__name__)


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
                rating=None,  # Оценка не используется
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
                        "rating": None,
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


# Подключение сигналов происходит автоматически при импорте модуля
# Импорт должен быть в apps.py через ready()
