"""
Certificates Signals Module - Сигналы для автоматической выдачи сертификатов.

Этот модуль содержит Django signals для автоматического создания сертификатов
при завершении студентом курса.

Сигналы:
    - check_course_completion: Проверяет прогресс после завершения шага
    - issue_certificate: Выдает сертификат если курс завершен на 100%

Логика:
    1. Студент завершает шаг (StepProgress.is_completed = True)
    2. Signal проверяет прогресс курса
    3. Если прогресс >= 100% и сертификата еще нет
    4. Создает Certificate автоматически
    5. Генерирует PDF (async через Celery)
    6. Отправляет email уведомление

Автор: Pyland Team
Дата: 2026
"""

from __future__ import annotations

import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(post_save, sender="reviewers.StepProgress")
def check_course_completion_on_step_complete(sender, instance, created, **kwargs):
    """
    Проверить завершение курса после завершения шага.

    Срабатывает при:
    - Создании нового StepProgress с is_completed=True
    - Изменении StepProgress.is_completed с False на True

    Логика:
    1. Проверить, что шаг завершен (is_completed=True)
    2. Получить курс через lesson
    3. Проверить прогресс курса >= 100%
    4. Проверить, нет ли уже сертификата
    5. Если все ОК - создать сертификат
    """
    from .models import Certificate
    from .utils import (
        can_receive_certificate,
        generate_certificate_pdf,
        send_certificate_notification,
    )

    # Проверка 1: Шаг должен быть завершен
    if not instance.is_completed:
        return

    # Проверка 2: Получить студента и курс
    try:
        student = instance.profile
        lesson = instance.step.lesson
        course = lesson.course
    except Exception as e:
        logger.error(f"Error getting course from StepProgress {instance.id}: {e}")
        return

    # Проверка 3: Проверить, может ли студент получить сертификат
    can_receive, reason = can_receive_certificate(student, course)

    if not can_receive:
        logger.debug(
            f"Student {student.user.email} cannot receive certificate for "
            f"course {course.id}: {reason}"
        )
        return

    # Проверка 4: Проверить, нет ли уже сертификата
    existing_certificate = Certificate.objects.filter(student=student, course=course).first()

    if existing_certificate:
        logger.debug(
            f"Certificate already exists for student {student.user.email} and course {course.id}"
        )
        return

    # Создать сертификат
    try:
        certificate = Certificate.create_for_student(student, course)

        logger.info(
            f"Certificate {certificate.certificate_number} created for "
            f"student {student.user.email} after completing course {course.id}"
        )

        # Генерировать PDF (можно async через Celery)
        try:
            generate_certificate_pdf(certificate)
            logger.info(f"PDF generated for certificate {certificate.certificate_number}")
        except Exception as e:
            logger.error(
                f"Failed to generate PDF for certificate {certificate.certificate_number}: {e}"
            )

        # Отправить уведомление
        try:
            send_certificate_notification(certificate)
            logger.info(f"Notification sent for certificate {certificate.certificate_number}")
        except Exception as e:
            logger.error(
                f"Failed to send notification for certificate {certificate.certificate_number}: {e}"
            )

    except Exception as e:
        logger.error(
            f"Failed to create certificate for student {student.user.email} "
            f"and course {course.id}: {e}"
        )


@receiver(post_save, sender="reviewers.LessonSubmission")
def check_course_completion_on_submission_approved(sender, instance, created, **kwargs):
    """
    Проверить завершение курса после одобрения задания.

    Дополнительная точка проверки - когда все задания одобрены,
    курс может быть завершен даже если не все шаги отмечены как completed.
    """
    from .models import Certificate
    from .utils import (
        can_receive_certificate,
        generate_certificate_pdf,
        send_certificate_notification,
    )

    # Проверка: Задание должно быть одобрено
    if instance.status != "approved":
        return

    # Получить студента и курс
    try:
        student = instance.student
        lesson = instance.lesson
        course = lesson.course
    except Exception as e:
        logger.error(f"Error getting course from LessonSubmission {instance.id}: {e}")
        return

    # Проверить, может ли студент получить сертификат
    can_receive, reason = can_receive_certificate(student, course)

    if not can_receive:
        return

    # Проверить, нет ли уже сертификата
    if Certificate.objects.filter(student=student, course=course).exists():
        return

    # Создать сертификат
    try:
        certificate = Certificate.create_for_student(student, course)

        logger.info(
            f"Certificate {certificate.certificate_number} created for "
            f"student {student.user.email} after submission approval"
        )

        # Генерировать PDF и отправить уведомление
        try:
            generate_certificate_pdf(certificate)
            send_certificate_notification(certificate)
        except Exception as e:
            logger.error(f"Error in certificate post-processing: {e}")

    except Exception as e:
        logger.error(f"Failed to create certificate: {e}")
