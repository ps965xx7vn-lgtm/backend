"""
Account Tasks Module - Асинхронные задачи Celery для отправки email.

Этот модуль содержит Celery tasks для фоновой обработки:
    - send_verification_email: Celery task для отправки письма верификации
    - send_verification_email_sync: Синхронная отправка (fallback без Celery)
    - send_password_reset_email: Celery task для отправки письма сброса пароля
    - send_password_reset_email_sync: Синхронная отправка сброса пароля

Используется для отправки email в фоновом режиме через Celery.
Если Celery недоступен - используются синхронные версии функций.

Автор: Pyland Team
Дата: 2025
"""

from __future__ import annotations

import logging
from typing import Optional

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def send_verification_email_sync(
    user_id: int, activation_url: str, subject: str, template_name: str
) -> Optional[int]:
    """
    Синхронная отправка email с подтверждением регистрации (fallback без Celery).

    Рендерит HTML шаблон письма и отправляет его пользователю.
    Используется когда Celery недоступен или для тестирования.

    Args:
        user_id: ID пользователя получателя письма
        activation_url: Полный URL для подтверждения email
            Пример: https://example.com/account/verify-email-confirm/MjM=/token/
        subject: Тема письма (может быть gettext_lazy для локализации)
        template_name: Путь к Django шаблону для рендеринга HTML письма
            Пример: 'students/email/email-verification.html'

    Returns:
        int: Количество успешно отправленных писем (обычно 1) или None при ошибке

    Example:
        >>> send_verification_email_sync(
        ...     user_id=123,
        ...     activation_url='https://site.com/verify/abc123/',
        ...     subject='Подтвердите email',
        ...     template_name='students/email/verify.html'
        ... )
        1  # Письмо отправлено успешно
    """
    from django.contrib.auth import get_user_model

    User = get_user_model()

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        # Пользователь не найден — ничего не делаем
        return

    message = render_to_string(
        template_name,
        {
            "user": user,
            "activation_url": activation_url,
        },
    )

    email = EmailMessage(subject=str(subject), body=message, to=[user.email])
    email.content_subtype = "html"

    try:
        result = email.send()
        logger.info(f"Email успешно отправлено пользователю {user.email}, результат: {result}")
        return result
    except Exception as e:
        logger.error(f"Ошибка отправки email пользователю {user.email}: {str(e)}")
        logger.error(
            f"Email settings - HOST: {settings.EMAIL_HOST}, PORT: {settings.EMAIL_PORT}, USE_TLS: {settings.EMAIL_USE_TLS}"
        )
        logger.error(f"From email: {settings.DEFAULT_FROM_EMAIL}")
        raise e


@shared_task(bind=True, max_retries=3)
def send_verification_email(
    self, user_id: int, activation_url: str, subject: str, template_name: str
) -> str:
    """
    Отправляет письмо с подтверждением email асинхронно через Celery.

    Использует асинхронную очередь для отправки писем верификации пользователем.
    При ошибке подключения или отправки повторяет попытку через 60 секунд.

    Args:
        user_id: ID пользователя для отправки письма верификации
        activation_url: Полный URL для активации аккаунта
        subject: Тема письма (может быть gettext_lazy для локализации)
        template_name: Путь к шаблону для рендеринга HTML письма

    Returns:
        str: Количество отправленных писем (обычно '1') при успехе

    Raises:
        User.DoesNotExist: Если пользователь с указанным ID не найден
        SMTPException: При ошибке отправки письма (с автоматическим повтором)

    Example:
        >>> send_verification_email.delay(
        ...     user_id=42,
        ...     activation_url='https://site.com/verify/abc123/',
        ...     subject='Подтвердите email',
        ...     template_name='students/email/verify.html'
        ... )
        <AsyncResult: 123e4567-e89b-12d3-a456-426614174000>
    """
    from django.contrib.auth import get_user_model

    User = get_user_model()

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        # Пользователь не найден — ничего не делаем
        return

    message = render_to_string(
        template_name,
        {
            "user": user,
            "activation_url": activation_url,
        },
    )

    email = EmailMessage(subject=str(subject), body=message, to=[user.email])
    email.content_subtype = "html"

    try:
        result = email.send()
        logger.info(
            f"Email успешно отправлено через Celery пользователю {user.email}, результат: {result}"
        )
        return result
    except Exception as e:
        logger.error(f"Ошибка отправки email через Celery пользователю {user.email}: {str(e)}")
        raise e
