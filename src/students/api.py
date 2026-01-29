"""
Students API - REST API для управления настройками и данными студентов.

Этот модуль содержит эндпоинты специфичные для студентов:
    - Настройки уведомлений и приватности
    - Управление аватаром
    - Статистика и статус аккаунта
    - Детальная информация профиля

Примечание:
    Auth endpoints (register, login, password) находятся в authentication/api.py
    Базовые profile endpoints (get, update) находятся в authentication/api.py

Автор: Pyland Team
Дата: 2025
"""

import logging

from django.contrib.auth import get_user_model
from django.db import transaction
from ninja import Router
from ninja.errors import HttpError
from ninja_jwt.authentication import JWTAuth

from .schemas import (  # Helper schemas; Settings schemas; Profile schemas
    AccountStatusOut,
    MessageSchema,
    NotificationSettingsOut,
    NotificationSettingsUpdate,
    PrivacySettingsOut,
    PrivacySettingsUpdate,
    ProfileDetailOut,
    ProfileOut,
)

logger = logging.getLogger(__name__)

router = Router(tags=["Students"])

User = get_user_model()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def serialize_profile(student) -> dict:
    """
    Сериализация профиля студента.

    Args:
        student: Student объект

    Returns:
        dict: Данные для ProfileOut схемы
    """
    user = student.user
    return {
        "id": str(student.id),
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name or "",
        "last_name": user.last_name or "",
        "phone": str(student.phone) if student.phone else None,
        "birthday": student.birthday.isoformat() if student.birthday else None,
        "gender": student.gender if student.gender else None,
        "country": str(student.country) if student.country else None,
        "city": student.city or None,
        "address": student.address or None,
        "bio": student.bio or None,
        "avatar": student.avatar.url if student.avatar else None,
        "role": user.role.name if user.role else None,
        "is_active": student.is_active,
        "created_at": student.created_at.isoformat(),
    }


def serialize_profile_detail(student) -> dict:
    """
    Детальная сериализация профиля со статистикой.

    Args:
        student: Student объект

    Returns:
        dict: Данные для ProfileDetailOut схемы
    """
    profile_data = serialize_profile(student)

    # TODO: Добавить реальную статистику из courses app
    profile_data.update(
        {
            "courses_enrolled": 0,
            "courses_completed": 0,
            "lessons_completed": 0,
            "total_study_time": 0,
            "achievements_count": 0,
        }
    )

    return profile_data


# ============================================================================
# SETTINGS ENDPOINTS - NOTIFICATIONS
# ============================================================================


@router.get("/settings/notifications", response=NotificationSettingsOut, auth=JWTAuth())
def get_notification_settings(request) -> NotificationSettingsOut:
    """
    Получение настроек уведомлений студента.

    Returns:
        NotificationSettingsOut: Настройки уведомлений
    """
    student = request.user.student
    logger.info(f"Get notification settings: {request.user.email}")

    return NotificationSettingsOut(
        email_notifications=student.email_notifications,
        course_updates=student.course_updates,
        lesson_reminders=student.lesson_reminders,
        achievement_alerts=student.achievement_alerts,
        weekly_summary=student.weekly_summary,
        marketing_emails=student.marketing_emails,
    )


@router.patch("/settings/notifications", response=NotificationSettingsOut, auth=JWTAuth())
def update_notification_settings(
    request, payload: NotificationSettingsUpdate
) -> NotificationSettingsOut:
    """
    Обновление настроек уведомлений студента.

    Args:
        payload: Настройки для обновления (все поля опциональны)

    Returns:
        NotificationSettingsOut: Обновлённые настройки

    Raises:
        HttpError 400: Нет данных для обновления
    """
    student = request.user.student
    data = payload.dict(exclude_none=True)

    logger.info(f"Update notification settings: {request.user.email}, fields: {list(data.keys())}")

    if not data:
        raise HttpError(400, "No data to update")

    # Обновление полей
    for field, value in data.items():
        setattr(student, field, value)

    student.save(update_fields=list(data.keys()))

    logger.info(f"Notification settings updated: {request.user.email}")

    return NotificationSettingsOut(
        email_notifications=student.email_notifications,
        course_updates=student.course_updates,
        lesson_reminders=student.lesson_reminders,
        achievement_alerts=student.achievement_alerts,
        weekly_summary=student.weekly_summary,
        marketing_emails=student.marketing_emails,
    )


# ============================================================================
# SETTINGS ENDPOINTS - PRIVACY
# ============================================================================


@router.get("/settings/privacy", response=PrivacySettingsOut, auth=JWTAuth())
def get_privacy_settings(request) -> PrivacySettingsOut:
    """
    Получение настроек приватности студента.

    Returns:
        PrivacySettingsOut: Настройки приватности
    """
    student = request.user.student
    logger.info(f"Get privacy settings: {request.user.email}")

    return PrivacySettingsOut(
        profile_visibility=student.profile_visibility,
        show_progress=student.show_progress,
        show_achievements=student.show_achievements,
        allow_messages=student.allow_messages,
    )


@router.patch("/settings/privacy", response=PrivacySettingsOut, auth=JWTAuth())
def update_privacy_settings(request, payload: PrivacySettingsUpdate) -> PrivacySettingsOut:
    """
    Обновление настроек приватности студента.

    Args:
        payload: Настройки для обновления (все поля опциональны)

    Returns:
        PrivacySettingsOut: Обновлённые настройки

    Raises:
        HttpError 400: Нет данных для обновления или неверное значение
    """
    student = request.user.student
    data = payload.dict(exclude_none=True)

    logger.info(f"Update privacy settings: {request.user.email}, fields: {list(data.keys())}")

    if not data:
        raise HttpError(400, "No data to update")

    # Валидация profile_visibility
    if "profile_visibility" in data:
        valid_values = ["public", "students", "private"]
        if data["profile_visibility"] not in valid_values:
            raise HttpError(
                400, f"Invalid profile_visibility. Must be one of: {', '.join(valid_values)}"
            )

    # Обновление полей
    for field, value in data.items():
        setattr(student, field, value)

    student.save(update_fields=list(data.keys()))

    logger.info(f"Privacy settings updated: {request.user.email}")

    return PrivacySettingsOut(
        profile_visibility=student.profile_visibility,
        show_progress=student.show_progress,
        show_achievements=student.show_achievements,
        allow_messages=student.allow_messages,
    )


# ============================================================================
# ACCOUNT STATUS
# ============================================================================


@router.get("/status", response=AccountStatusOut, auth=JWTAuth())
def get_account_status(request) -> AccountStatusOut:
    """
    Получение статуса аккаунта студента.

    Возвращает информацию о:
    - Активности аккаунта
    - Верификации email
    - Заполненности профиля
    - Возрасте аккаунта

    Returns:
        AccountStatusOut: Статус аккаунта
    """
    from django.utils import timezone

    user = request.user
    student = user.student

    logger.info(f"Get account status: {user.email}")

    # Проверка заполненности профиля
    has_completed_profile = all(
        [
            user.first_name,
            user.last_name,
            student.phone or student.city,
        ]
    )

    # Возраст аккаунта
    account_age = timezone.now() - user.date_joined

    return AccountStatusOut(
        is_active=user.is_active,
        email_is_verified=user.email_is_verified,
        has_completed_profile=has_completed_profile,
        account_age_days=account_age.days,
    )


# ============================================================================
# PROFILE DETAIL
# ============================================================================


@router.get("/profile/detail", response=ProfileDetailOut, auth=JWTAuth())
def get_profile_detail(request) -> ProfileDetailOut:
    """
    Получение детального профиля студента со статистикой.

    Включает всю информацию профиля + статистику обучения.
    Оптимизировано для мобильного приложения.

    Returns:
        ProfileDetailOut: Детальные данные профиля
    """
    logger.info(f"Get profile detail: {request.user.email}")

    student = request.user.student
    profile_data = serialize_profile_detail(student)

    return ProfileDetailOut(**profile_data)


# ============================================================================
# AVATAR MANAGEMENT
# ============================================================================


@router.post("/avatar/upload", response=ProfileOut, auth=JWTAuth())
@transaction.atomic
def upload_avatar(request) -> ProfileOut:
    """
    Загрузка аватара студента.

    Принимает изображение через multipart/form-data.
    Поддерживаемые форматы: JPEG, PNG, GIF, WebP
    Максимальный размер: 5MB

    Args:
        request.FILES['avatar']: Файл изображения

    Returns:
        ProfileOut: Обновлённый профиль с новым аватаром

    Raises:
        HttpError 400: Файл не предоставлен или неверный формат/размер
    """
    student = request.user.student

    logger.info(f"Avatar upload: {request.user.email}")

    if "avatar" not in request.FILES:
        raise HttpError(400, "No avatar file provided")

    avatar_file = request.FILES["avatar"]

    # Проверка типа файла
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if avatar_file.content_type not in allowed_types:
        logger.warning(f"Invalid avatar file type: {avatar_file.content_type}")
        raise HttpError(400, f"Invalid file type. Allowed: {', '.join(allowed_types)}")

    # Проверка размера (макс 5MB)
    max_size = 5 * 1024 * 1024  # 5MB
    if avatar_file.size > max_size:
        logger.warning(f"Avatar file too large: {avatar_file.size} bytes")
        raise HttpError(400, "File too large. Maximum size: 5MB")

    # Удаление старого аватара
    if student.avatar:
        student.avatar.delete(save=False)

    # Сохранение нового аватара
    student.avatar = avatar_file
    student.save(update_fields=["avatar"])

    logger.info(f"Avatar uploaded: {request.user.email}")

    profile_data = serialize_profile(student)
    return ProfileOut(**profile_data)


@router.delete("/avatar", response=MessageSchema, auth=JWTAuth())
@transaction.atomic
def delete_avatar(request) -> MessageSchema:
    """
    Удаление аватара студента.

    Returns:
        MessageSchema: Подтверждение удаления

    Raises:
        HttpError 404: Аватар не найден
    """
    student = request.user.student

    logger.info(f"Avatar delete: {request.user.email}")

    if student.avatar:
        student.avatar.delete(save=True)
        logger.info(f"Avatar deleted: {request.user.email}")
        return MessageSchema(message="Avatar deleted successfully")
    else:
        raise HttpError(404, "No avatar found")


# ============================================================================
# ACCOUNT MANAGEMENT
# ============================================================================


@router.delete("/account", response=MessageSchema, auth=JWTAuth())
@transaction.atomic
def deactivate_account(request) -> MessageSchema:
    """
    Деактивация аккаунта студента.

    Устанавливает is_active=False, блокируя вход в систему.
    Данные сохраняются для возможного восстановления.

    Returns:
        MessageSchema: Подтверждение деактивации
    """
    user = request.user
    logger.warning(f"Account deactivation: {user.email}")

    user.is_active = False
    user.save(update_fields=["is_active"])

    logger.info(f"Account deactivated: {user.email}")

    return MessageSchema(message="Account deactivated successfully")


@router.post("/complete-step/{step_id}/", response=MessageSchema, auth=JWTAuth())
@transaction.atomic
def complete_step(request, step_id: str) -> MessageSchema:
    """
    Отметить шаг как выполненный.

    Args:
        step_id: UUID шага

    Returns:
        MessageSchema: Подтверждение выполнения
    """
    from uuid import UUID

    from django.utils import timezone

    from courses.models import Step
    from reviewers.models import StepProgress
    from students.cache_utils import safe_cache_delete

    try:
        step_uuid = UUID(step_id)
        step = Step.objects.get(id=step_uuid)
    except (ValueError, Step.DoesNotExist):
        raise HttpError(404, "Step not found")

    # Получаем или создаём запись прогресса
    progress, created = StepProgress.objects.get_or_create(
        profile=request.user.student,
        step=step,
        defaults={"is_completed": True, "completed_at": timezone.now()},
    )

    if not created and not progress.is_completed:
        progress.is_completed = True
        progress.completed_at = timezone.now()
        progress.save(update_fields=["is_completed", "completed_at"])

    # Инвалидируем кэш прогресса
    lesson = step.lesson
    course = lesson.course
    profile = request.user.student

    lesson.invalidate_progress_cache(profile)
    course.invalidate_progress_cache(profile)

    # Инвалидируем кэш страниц
    safe_cache_delete(f"user_courses_stats_{profile.id}")
    safe_cache_delete(f"dashboard_stats_{profile.id}")
    safe_cache_delete(f"course_detail_{course.id}_{profile.id}")

    logger.info(f"Step completed: {step.name} by {request.user.email}")

    return MessageSchema(message="Step marked as completed")
