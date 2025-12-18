"""
Reviewers Celery Tasks - Асинхронные задачи для ревьюеров.

Этот модуль содержит Celery tasks для:
    - Отправки email уведомлений ревьюерам о новых работах
    - Отправки напоминаний о непроверенных работах
    - Генерации отчётов по статистике проверок

Автор: Pyland Team
Дата: 2025
"""

from __future__ import annotations

import logging
from typing import List

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_new_submission_notification(
    self,
    reviewer_emails: List[str],
    student_name: str,
    course_name: str,
    lesson_name: str,
    lesson_url: str,
    submission_id: str,
) -> dict:
    """
    Асинхронно отправляет уведомления ревьюерам о новой работе студента.

    Args:
        reviewer_emails: Список email адресов ревьюеров
        student_name: Имя студента
        course_name: Название курса
        lesson_name: Название урока
        lesson_url: Ссылка на работу студента
        submission_id: UUID работы

    Returns:
        dict: Статистика отправки {success: int, failed: int, total: int}

    Raises:
        Exception: При критической ошибке (с автоматическим повтором)
    """
    success_count = 0
    failed_count = 0

    subject = f"📝 Новая работа на проверку: {lesson_name}"

    # Текстовая версия для клиентов без HTML
    text_message = (
        f"Новая работа на проверку\n\n"
        f"Студент {student_name} отправил работу на проверку.\n\n"
        f"Курс: {course_name}\n"
        f"Урок: {lesson_name}\n"
        f"Ссылка на работу: {lesson_url}\n\n"
        f"Перейти к проверке: {settings.SITE_URL}/reviewers/submissions/"
    )

    for email in reviewer_emails:
        try:
            # Рендерим HTML для каждого ревьюера с его email
            html_message_personalized = render_to_string(
                "reviewers/email/new_submission.html",
                {
                    "student_name": student_name,
                    "course_name": course_name,
                    "lesson_name": lesson_name,
                    "lesson_url": lesson_url,
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
            email_msg.body = html_message_personalized

            result = email_msg.send(fail_silently=False)

            if result == 1:
                success_count += 1
                logger.info(f"Уведомление отправлено на {email} " f"для работы {submission_id}")
            else:
                failed_count += 1
                logger.warning(f"Отправка email вернула 0 для {email} " f"(работа {submission_id})")

        except Exception as e:
            failed_count += 1
            logger.error(
                f"Не удалось отправить email на {email} " f"для работы {submission_id}: {e}"
            )

    total = len(reviewer_emails)
    result = {
        "success": success_count,
        "failed": failed_count,
        "total": total,
        "submission_id": submission_id,
    }

    logger.info(
        f"Задача уведомлений завершена для работы {submission_id}: "
        f"{success_count}/{total} писем отправлено успешно"
    )

    return result


@shared_task(bind=True, max_retries=3)
def send_review_completed_notification(
    self,
    student_email: str,
    student_name: str,
    course_name: str,
    lesson_name: str,
    submission_id: str,
    status: str,
    status_text: str,
    status_emoji: str,
    rating: int = None,
    comments: str = "",
    improvements: List[str] = None,
    header_color: str = "#10b981",
    status_bg_color: str = "#ecfdf5",
    status_border_color: str = "#10b981",
    status_text_color: str = "#047857",
    status_title_color: str = "#065f46",
) -> dict:
    """
    Асинхронно отправляет уведомление студенту о проверке работы.

    Args:
        student_email: Email студента
        student_name: Имя студента
        course_name: Название курса
        lesson_name: Название урока
        submission_id: UUID работы
        status: Статус проверки (approved/needs_work)
        status_text: Текст статуса на русском
        status_emoji: Эмодзи для статуса
        rating: Оценка работы (1-5)
        comments: Комментарии ревьюера
        improvements: Список рекомендаций по улучшению
        header_color: Цвет заголовка
        status_bg_color: Цвет фона статуса
        status_border_color: Цвет рамки статуса
        status_text_color: Цвет текста статуса
        status_title_color: Цвет заголовка статуса

    Returns:
        dict: Результат отправки {success: bool, email: str}
    """
    try:
        if improvements is None:
            improvements = []

        # Рендерим HTML шаблон
        html_message = render_to_string(
            "reviewers/email/review_completed.html",
            {
                "student_name": student_name,
                "student_email": student_email,
                "course_name": course_name,
                "lesson_name": lesson_name,
                "status": status,
                "status_text": status_text,
                "status_emoji": status_emoji,
                "rating": rating,
                "comments": comments,
                "improvements": improvements,
                "submission_url": f"{settings.SITE_URL}/students/submissions/{submission_id}/",
                "header_color": header_color,
                "status_bg_color": status_bg_color,
                "status_border_color": status_border_color,
                "status_text_color": status_text_color,
                "status_title_color": status_title_color,
            },
        )

        # Текстовая версия
        subject = f"{status_emoji} Ваша работа проверена: {lesson_name}"
        text_message = (
            f"Здравствуйте, {student_name}!\n\n"
            f'Ваша работа по уроку "{lesson_name}" проверена.\n\n'
            f"Статус: {status_text}\n"
        )

        if comments:
            text_message += f"\nКомментарий ревьюера:\n{comments}\n"

        text_message += (
            f"\nПерейти к работе: {settings.SITE_URL}/students/submissions/{submission_id}/\n"
        )

        # Отправляем email
        email_msg = EmailMessage(
            subject=subject,
            body=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[student_email],
        )
        email_msg.content_subtype = "html"
        email_msg.body = html_message

        result = email_msg.send(fail_silently=False)

        if result == 1:
            logger.info(
                f"Уведомление о проверке отправлено студенту {student_email} "
                f"для работы {submission_id} (статус: {status})"
            )
            return {"success": True, "email": student_email}
        else:
            logger.warning(
                f"Отправка email студенту {student_email} вернула 0 " f"(работа {submission_id})"
            )
            return {"success": False, "email": student_email}

    except Exception as e:
        logger.error(
            f"Ошибка отправки уведомления студенту {student_email} "
            f"для работы {submission_id}: {e}"
        )
        # Повторяем попытку через 60 секунд
        raise self.retry(exc=e, countdown=60)
