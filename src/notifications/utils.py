"""
Notifications Utils Module - Вспомогательные функции для работы с уведомлениями.

Этот модуль содержит utility функции для проверки прав на отправку уведомлений
и управления подписками пользователей.

Основные функции:
    - can_send_notification: Проверка, можно ли отправить уведомление студенту
    - get_recipients_for_newsletter: Получить список получателей для рассылки
    - sync_user_subscriptions: Синхронизация настроек Student с Subscription

Логика email_notifications (Master Switch):
    - Если email_notifications = False → НЕ СЛАТЬ НИЧЕГО
    - Если email_notifications = True → проверить конкретную настройку

Автор: Pyland Team
Дата: 2026
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from authentication.models import Student, User

logger = logging.getLogger(__name__)

# Маппинг типов уведомлений на поля Student модели
NOTIFICATION_TYPE_MAPPING = {
    "course_update": "course_updates",
    "lesson_reminder": "lesson_reminders",
    "achievement_alert": "achievement_alerts",
    "weekly_summary": "weekly_summary",
    "marketing_email": "marketing_emails",
}


def can_send_notification(student: Student, notification_type: str) -> bool:
    """
    Проверить, можно ли отправить уведомление студенту.

    Логика Master Switch:
    1. Если email_notifications = False → НЕ СЛАТЬ НИЧЕГО
    2. Если email_notifications = True → проверить конкретную настройку
    3. Если тип уведомления не найден → по умолчанию True

    Args:
        student: Объект студента
        notification_type: Тип уведомления (course_update, lesson_reminder, etc.)

    Returns:
        bool: True если можно отправить, False если нельзя

    Examples:
        >>> from authentication.models import Student
        >>> student = Student.objects.get(user__email='test@test.com')
        >>> can_send_notification(student, 'course_update')
        True
        >>> student.email_notifications = False
        >>> can_send_notification(student, 'course_update')
        False  # Master Switch выключен
    """
    # Главный переключатель (Master Switch)
    if not student.email_notifications:
        logger.debug(f"Master Switch OFF for student {student.id}. Not sending {notification_type}")
        return False

    # Проверка конкретной настройки
    field_name = NOTIFICATION_TYPE_MAPPING.get(notification_type)

    if field_name:
        is_enabled = getattr(student, field_name, True)
        logger.debug(f"Student {student.id}: {notification_type} = {is_enabled}")
        return is_enabled

    # Если тип не найден - разрешаем (для обратной совместимости)
    logger.warning(f"Unknown notification type: {notification_type}. Allowing by default.")
    return True


def can_send_any_notifications(student: Student) -> bool:
    """
    Проверить, может ли студент получать ХОТЬ КАКИЕ-ТО уведомления.

    Используется для оптимизации - не нужно проверять каждый тип отдельно.

    Args:
        student: Объект студента

    Returns:
        bool: True если Master Switch включен, False иначе
    """
    return student.email_notifications


def get_enabled_notification_types(student: Student) -> list[str]:
    """
    Получить список типов уведомлений, которые включены у студента.

    Args:
        student: Объект студента

    Returns:
        list[str]: Список названий полей (course_updates, lesson_reminders, etc.)

    Examples:
        >>> student = Student.objects.first()
        >>> get_enabled_notification_types(student)
        ['course_updates', 'lesson_reminders', 'achievement_alerts', 'weekly_summary']
    """
    if not student.email_notifications:
        return []

    enabled = []
    for field_name in NOTIFICATION_TYPE_MAPPING.values():
        if getattr(student, field_name, False):
            enabled.append(field_name)

    return enabled


def get_recipients_for_newsletter(
    target_audience: str = "all",
    course_id: int | None = None,
    only_marketing: bool = True,
) -> list[User]:
    """
    Получить список получателей для массовой рассылки.

    Args:
        target_audience: Целевая аудитория
            - 'all': Все студенты с активными уведомлениями
            - 'active': Только активные студенты (были онлайн за последние 30 дней)
            - 'course': Студенты конкретного курса
            - 'marketing': Только подписанные на маркетинг
        course_id: ID курса (обязателен если target_audience='course')
        only_marketing: Проверять подписку на marketing_emails

    Returns:
        list[User]: Список пользователей для рассылки

    Examples:
        >>> # Все студенты подписанные на маркетинг
        >>> users = get_recipients_for_newsletter('marketing')
        >>> # Студенты курса Python
        >>> users = get_recipients_for_newsletter('course', course_id=1)
    """
    from datetime import timedelta

    from django.contrib.auth import get_user_model
    from django.utils import timezone

    User = get_user_model()

    # Базовый queryset - только активные пользователи с включенным Master Switch
    queryset = User.objects.filter(
        is_active=True,
        student__email_notifications=True,  # Master Switch
    ).select_related("student")

    # Фильтр по marketing_emails
    if only_marketing:
        queryset = queryset.filter(student__marketing_emails=True)

    # Фильтры по целевой аудитории
    if target_audience == "active":
        # Были онлайн за последние 30 дней
        thirty_days_ago = timezone.now() - timedelta(days=30)
        queryset = queryset.filter(last_login__gte=thirty_days_ago)

    elif target_audience == "course" and course_id:
        # Студенты конкретного курса
        queryset = queryset.filter(student__courses__id=course_id)

    elif target_audience == "marketing":
        # Только подписанные на маркетинг (уже отфильтровано выше)
        pass

    # Убираем дубликаты
    queryset = queryset.distinct()

    logger.info(
        f"Newsletter recipients: {queryset.count()} users "
        f"(target={target_audience}, course={course_id})"
    )

    return list(queryset)


def sync_user_subscriptions(user: User) -> None:
    """
    Синхронизировать настройки Student с Subscription моделью.

    DEPRECATED: Эта функция оставлена для обратной совместимости.
    Рекомендуется использовать только Student модель для зарегистрированных пользователей.

    Subscription модель теперь используется ТОЛЬКО для анонимных подписок (blog newsletter).

    Args:
        user: Пользователь для синхронизации
    """
    logger.warning(
        "sync_user_subscriptions is DEPRECATED. Use Student model as single source of truth."
    )

    # Проверяем наличие профиля студента
    if not hasattr(user, "student"):
        logger.error(f"User {user.id} has no student profile")
        return

    # Для обратной совместимости - удаляем старые Subscription записи
    from .models import Subscription

    deleted_count = Subscription.objects.filter(user=user).delete()[0]
    if deleted_count > 0:
        logger.info(f"Deleted {deleted_count} old Subscription records for user {user.id}")


def get_unsubscribe_url(user: User, notification_type: str | None = None) -> str:
    """
    Сгенерировать URL для отписки от уведомлений.

    Args:
        user: Пользователь
        notification_type: Тип уведомления для отписки (None = отписка от всех)

    Returns:
        str: URL для отписки

    Examples:
        >>> user = User.objects.first()
        >>> get_unsubscribe_url(user, 'marketing_emails')
        'https://pyland.ge/notifications/unsubscribe/abc123/?type=marketing_emails'
    """
    from django.conf import settings
    from django.urls import reverse
    from django.utils.encoding import force_bytes
    from django.utils.http import urlsafe_base64_encode

    # Создаем токен из user ID (в production использовать signing)
    token = urlsafe_base64_encode(force_bytes(user.pk))

    # URL для отписки
    path = reverse("notifications:unsubscribe", kwargs={"token": token})

    if notification_type:
        path += f"?type={notification_type}"

    # Полный URL с доменом
    domain = getattr(settings, "SITE_DOMAIN", "localhost:8000")
    scheme = "https" if getattr(settings, "SECURE_SSL_REDIRECT", False) else "http"

    return f"{scheme}://{domain}{path}"
