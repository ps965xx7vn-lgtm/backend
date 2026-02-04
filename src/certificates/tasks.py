"""
Celery задачи для модуля certificates.

Асинхронные задачи:
- send_certificate_email - асинхронная отправка сертификата на email студента
- send_certificate_email_sync - синхронная отправка (fallback без Celery)
"""

import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


def send_certificate_email_sync(
    student_email: str,
    student_name: str,
    course_name: str,
    certificate_number: str,
    verification_code: str,
    pdf_url: str,
    completion_date: str = "",
    lessons_completed: int = 0,
    total_lessons: int = 0,
    assignments_submitted: int = 0,
    assignments_approved: int = 0,
    reviews_received: int = 0,
    total_time_spent: float = 0.0,
) -> int | None:
    """
    Синхронная отправка email с сертификатом (fallback без Celery/Redis).

    Используется когда Celery недоступен или для немедленной отправки.
    Рендерит HTML шаблон и отправляет письмо синхронно.

    Args:
        student_email: Email студента
        student_name: Имя студента
        course_name: Название курса
        certificate_number: Номер сертификата (CERT-YYYYMMDD-XXXX)
        verification_code: Код верификации для проверки подлинности
        pdf_url: Абсолютный URL для скачивания PDF сертификата
        lessons_completed: Количество пройденных уроков
        total_lessons: Общее количество уроков
        assignments_submitted: Количество отправленных заданий
        assignments_approved: Количество одобренных заданий
        reviews_received: Количество полученных отзывов

    Returns:
        int: Количество успешно отправленных писем (обычно 1) или None при ошибке

    Example:
        >>> send_certificate_email_sync(
        ...     student_email='student@example.com',
        ...     student_name='Иван Петров',
        ...     course_name='Python для начинающих',
        ...     certificate_number='CERT-20260204-A3F9',
        ...     verification_code='3DAD82B85014',
        ...     pdf_url='https://site.com/media/cert.pdf',
        ...     lessons_completed=10,
        ...     total_lessons=10
        ... )
        1  # Письмо отправлено успешно
    """
    try:
        logger.info(f"Синхронная отправка сертификата {certificate_number} на {student_email}")

        # Подготовка контекста для шаблона
        context = {
            "student_name": student_name,
            "course_name": course_name,
            "certificate_number": certificate_number,
            "verification_code": verification_code,
            "pdf_url": pdf_url,
            "site_url": settings.SITE_URL,
            "site_name": "PyLand",
            "completion_date": completion_date,
            "lessons_completed": lessons_completed,
            "total_lessons": total_lessons,
            "assignments_submitted": assignments_submitted,
            "assignments_approved": assignments_approved,
            "reviews_received": reviews_received,
            "total_time_spent": total_time_spent,
        }

        # Рендерим HTML версию письма
        html_content = render_to_string("certificates/emails/certificate_issued.html", context)

        # Создаем текстовую версию (fallback)
        text_content = strip_tags(html_content)

        # Создаем email
        subject = f"🎓 Поздравляем! Вы получили сертификат о прохождении курса {course_name}"
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [student_email]

        email = EmailMultiAlternatives(
            subject=subject, body=text_content, from_email=from_email, to=to_email
        )
        email.attach_alternative(html_content, "text/html")

        # Отправляем email
        result = email.send(fail_silently=False)

        logger.info(
            f"✅ Сертификат {certificate_number} успешно отправлен синхронно на {student_email}"
        )

        return result

    except Exception as e:
        logger.error(
            f"Ошибка синхронной отправки сертификата {certificate_number} пользователю {student_email}: {str(e)}"
        )
        logger.error(
            f"Email settings - HOST: {settings.EMAIL_HOST}, PORT: {settings.EMAIL_PORT}, "
            f"USE_TLS: {settings.EMAIL_USE_TLS}, FROM: {settings.DEFAULT_FROM_EMAIL}"
        )
        raise e


@shared_task(bind=True, max_retries=3)
def send_certificate_email(
    self,
    student_email: str,
    student_name: str,
    course_name: str,
    certificate_number: str,
    verification_code: str,
    pdf_url: str,
    completion_date: str = "",
    lessons_completed: int = 0,
    total_lessons: int = 0,
    assignments_submitted: int = 0,
    assignments_approved: int = 0,
    reviews_received: int = 0,
    total_time_spent: float = 0.0,
):
    """
    Отправляет email студенту с сертификатом о прохождении курса.

    Args:
        student_email: Email студента
        student_name: Имя студента
        course_name: Название курса
        certificate_number: Номер сертификата (CERT-YYYYMMDD-XXXX)
        verification_code: Код верификации для проверки подлинности
        pdf_url: Абсолютный URL для скачивания PDF сертификата
        completion_date: Дата завершения курса
        lessons_completed: Количество пройденных уроков
        total_lessons: Общее количество уроков
        assignments_submitted: Количество отправленных заданий
        assignments_approved: Количество одобренных заданий
        reviews_received: Количество полученных отзывов

    Raises:
        Exception: При ошибке отправки email (с повтором через 60 секунд)
    """
    try:
        logger.info(f"Отправка сертификата {certificate_number} на {student_email}")

        # Подготовка контекста для шаблона
        context = {
            "student_name": student_name,
            "course_name": course_name,
            "certificate_number": certificate_number,
            "verification_code": verification_code,
            "pdf_url": pdf_url,
            "site_url": settings.SITE_URL,
            "site_name": "PyLand",
            "completion_date": completion_date,
            "lessons_completed": lessons_completed,
            "total_lessons": total_lessons,
            "assignments_submitted": assignments_submitted,
            "assignments_approved": assignments_approved,
            "reviews_received": reviews_received,
            "total_time_spent": total_time_spent,
        }

        # Рендерим HTML версию письма
        html_content = render_to_string("certificates/emails/certificate_issued.html", context)

        # Создаем текстовую версию (fallback)
        text_content = strip_tags(html_content)

        # Создаем email
        subject = f"🎓 Поздравляем! Вы получили сертификат о прохождении курса {course_name}"
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [student_email]

        email = EmailMultiAlternatives(
            subject=subject, body=text_content, from_email=from_email, to=to_email
        )
        email.attach_alternative(html_content, "text/html")

        # Отправляем email
        email.send(fail_silently=False)

        logger.info(f"✅ Сертификат {certificate_number} успешно отправлен на {student_email}")

        return {
            "status": "success",
            "email": student_email,
            "certificate_number": certificate_number,
        }

    except Exception as exc:
        logger.error(
            f"❌ Ошибка при отправке сертификата {certificate_number} на {student_email}: {exc}"
        )
        # Повторная попытка через 60 секунд (max 3 раза)
        raise self.retry(exc=exc, countdown=60) from exc
