"""
Pydantic схемы для Account API.

Этот модуль содержит все схемы для валидации входных/выходных данных API.
Используется Django Ninja с Pydantic для автоматической валидации и документации.

Архитектура:
    - Input схемы: *In - для входящих данных (POST, PATCH)
    - Output схемы: *Out - для исходящих данных (GET)
    - Settings схемы: *Settings* - для настроек пользователя

Автор: PySchool Team
Дата: 2025
"""

from enum import Enum
from typing import List, Optional

from ninja import Field, Schema

# ============================================================================
# ENUMS
# ============================================================================


class ProfileVisibility(str, Enum):
    """Уровни видимости профиля."""

    PUBLIC = "public"
    STUDENTS = "students"
    PRIVATE = "private"


class Gender(str, Enum):
    """Пол пользователя."""

    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


# ============================================================================
# BASE SCHEMAS
# ============================================================================


class MessageSchema(Schema):
    """Схема простого сообщения."""

    message: str = Field(..., description="Текст сообщения")


class SuccessSchema(Schema):
    """Схема успешного ответа."""

    success: bool = Field(..., description="Статус операции")


# ============================================================================
# AUTH INPUT SCHEMAS
# ============================================================================


class RegisterIn(Schema):
    """Схема регистрации нового пользователя."""

    email: str = Field(..., min_length=5, max_length=254, description="Email адрес пользователя")
    password: str = Field(
        ..., min_length=8, max_length=128, description="Пароль (минимум 8 символов)"
    )
    first_name: Optional[str] = Field(None, max_length=150, description="Имя пользователя")
    phone: Optional[str] = Field(None, max_length=20, description="Номер телефона")


class LoginIn(Schema):
    """Схема аутентификации пользователя."""

    email: str = Field(..., description="Email адрес пользователя")
    password: str = Field(..., description="Пароль пользователя")


class ChangePasswordIn(Schema):
    """Схема смены пароля."""

    old_password: str = Field(..., description="Текущий пароль")
    new_password: str = Field(
        ..., min_length=8, max_length=128, description="Новый пароль (минимум 8 символов)"
    )


class PasswordResetRequestIn(Schema):
    """Схема запроса сброса пароля."""

    email: str = Field(..., description="Email для сброса пароля")


class PasswordResetConfirmIn(Schema):
    """Схема подтверждения сброса пароля."""

    token: str = Field(..., description="Токен сброса пароля")
    new_password: str = Field(..., min_length=8, description="Новый пароль")
    confirm_password: str = Field(..., min_length=8, description="Подтверждение пароля")


# ============================================================================
# PROFILE INPUT SCHEMAS
# ============================================================================


class ProfileUpdate(Schema):
    """Схема обновления профиля."""

    first_name: Optional[str] = Field(None, max_length=150, description="Имя")
    last_name: Optional[str] = Field(None, max_length=150, description="Фамилия")
    phone: Optional[str] = Field(None, max_length=20, description="Номер телефона")
    birthday: Optional[str] = Field(None, description="Дата рождения (YYYY-MM-DD)")
    gender: Optional[Gender] = Field(None, description="Пол")
    country: Optional[str] = Field(None, max_length=2, description="Код страны (ISO 3166-1)")
    city: Optional[str] = Field(None, max_length=100, description="Город")
    address: Optional[str] = Field(None, max_length=500, description="Адрес")
    bio: Optional[str] = Field(None, max_length=1000, description="О себе")


class NotificationSettingsUpdate(Schema):
    """Схема обновления настроек уведомлений."""

    email_notifications: Optional[bool] = Field(None, description="Уведомления по email")
    course_updates: Optional[bool] = Field(None, description="Обновления курсов")
    lesson_reminders: Optional[bool] = Field(None, description="Напоминания о уроках")
    achievement_alerts: Optional[bool] = Field(None, description="Уведомления о достижениях")
    weekly_summary: Optional[bool] = Field(None, description="Еженедельная сводка")
    marketing_emails: Optional[bool] = Field(None, description="Маркетинговые письма")


class PrivacySettingsUpdate(Schema):
    """Схема обновления настроек приватности."""

    profile_visibility: Optional[ProfileVisibility] = Field(None, description="Видимость профиля")
    show_progress: Optional[bool] = Field(None, description="Показывать прогресс")
    show_achievements: Optional[bool] = Field(None, description="Показывать достижения")
    allow_messages: Optional[bool] = Field(None, description="Разрешить сообщения")


class AvatarUploadIn(Schema):
    """Схема загрузки аватара (для multipart/form-data)."""

    pass  # Файл передается через request.FILES


class EmailUpdateIn(Schema):
    """Схема обновления email."""

    new_email: str = Field(..., min_length=5, max_length=254, description="Новый email адрес")
    password: str = Field(..., description="Текущий пароль для подтверждения")


class UsernameUpdateIn(Schema):
    """Схема обновления username."""

    username: str = Field(..., min_length=3, max_length=150, description="Новый username")


class DeviceTokenIn(Schema):
    """Схема регистрации токена устройства для push-уведомлений."""

    device_token: str = Field(..., description="FCM/APNS токен устройства")
    device_type: str = Field(..., description="Тип устройства (ios/android)")
    device_name: Optional[str] = Field(None, description="Название устройства")


# ============================================================================
# OUTPUT SCHEMAS
# ============================================================================


class TokenOut(Schema):
    """Схема JWT токенов."""

    access_token: str = Field(..., description="JWT access токен")
    refresh_token: str = Field(..., description="JWT refresh токен")


class ProfileOut(Schema):
    """Схема вывода профиля пользователя."""

    id: str = Field(..., description="Уникальный идентификатор профиля")
    username: Optional[str] = Field(None, description="Имя пользователя")
    email: str = Field(..., description="Email адрес")
    first_name: Optional[str] = Field(None, description="Имя")
    last_name: Optional[str] = Field(None, description="Фамилия")
    phone: Optional[str] = Field(None, description="Номер телефона")
    birthday: Optional[str] = Field(None, description="Дата рождения")
    gender: Optional[str] = Field(None, description="Пол")
    country: Optional[str] = Field(None, description="Страна")
    city: Optional[str] = Field(None, description="Город")
    address: Optional[str] = Field(None, description="Адрес")
    bio: Optional[str] = Field(None, description="О себе")
    avatar_url: Optional[str] = Field(None, description="URL аватара")
    role: Optional[str] = Field(None, description="Роль пользователя")
    courses: List[str] = Field(default_factory=list, description="Курсы пользователя")
    created_at: Optional[str] = Field(None, description="Дата создания профиля")


class RegisterOut(Schema):
    """Схема ответа при регистрации."""

    profile: ProfileOut = Field(..., description="Профиль пользователя")
    tokens: TokenOut = Field(..., description="JWT токены")


class LoginOut(Schema):
    """Схема ответа при входе."""

    profile: ProfileOut = Field(..., description="Профиль пользователя")
    tokens: TokenOut = Field(..., description="JWT токены")


class NotificationSettingsOut(Schema):
    """Схема вывода настроек уведомлений."""

    email_notifications: bool = Field(..., description="Уведомления по email")
    course_updates: bool = Field(..., description="Обновления курсов")
    lesson_reminders: bool = Field(..., description="Напоминания о уроках")
    achievement_alerts: bool = Field(..., description="Уведомления о достижениях")
    weekly_summary: bool = Field(..., description="Еженедельная сводка")
    marketing_emails: bool = Field(..., description="Маркетинговые письма")


class PrivacySettingsOut(Schema):
    """Схема вывода настроек приватности."""

    profile_visibility: str = Field(..., description="Видимость профиля")
    show_progress: bool = Field(..., description="Показывать прогресс")
    show_achievements: bool = Field(..., description="Показывать достижения")
    allow_messages: bool = Field(..., description="Разрешить сообщения")


class RoleOut(Schema):
    """Схема вывода роли."""

    name: str = Field(..., description="Название роли")
    description: str = Field(..., description="Описание роли")


class CourseOut(Schema):
    """Схема вывода курса (краткая)."""

    id: int = Field(..., description="ID курса")
    name: str = Field(..., description="Название курса")
    slug: str = Field(..., description="URL slug курса")


class ProfileStatsOut(Schema):
    """Схема статистики профиля."""

    completed_lessons: int = Field(..., ge=0, description="Завершенных уроков")
    total_lessons: int = Field(..., ge=0, description="Всего уроков")
    active_courses: int = Field(..., ge=0, description="Активных курсов")
    certificates_earned: int = Field(..., ge=0, description="Получено сертификатов")
    study_streak_days: int = Field(..., ge=0, description="Дней подряд занимается")
    total_study_time_minutes: int = Field(..., ge=0, description="Общее время обучения (минуты)")


class ProfileDetailOut(Schema):
    """Детальная схема профиля с дополнительной информацией."""

    # Базовая информация
    id: str = Field(..., description="Уникальный идентификатор профиля")
    username: Optional[str] = Field(None, description="Имя пользователя")
    email: str = Field(..., description="Email адрес")
    email_is_verified: bool = Field(..., description="Email подтвержден")

    # Персональные данные
    first_name: Optional[str] = Field(None, description="Имя")
    last_name: Optional[str] = Field(None, description="Фамилия")
    phone: Optional[str] = Field(None, description="Номер телефона")
    birthday: Optional[str] = Field(None, description="Дата рождения")
    gender: Optional[str] = Field(None, description="Пол")
    country: Optional[str] = Field(None, description="Страна")
    city: Optional[str] = Field(None, description="Город")
    address: Optional[str] = Field(None, description="Адрес")
    bio: Optional[str] = Field(None, description="О себе")
    avatar_url: Optional[str] = Field(None, description="URL аватара")

    # Роли и курсы (детальные)
    role: Optional[RoleOut] = Field(None, description="Роль пользователя с описанием")
    courses: List[CourseOut] = Field(
        default_factory=list, description="Курсы пользователя с деталями"
    )

    # Настройки
    notification_settings: NotificationSettingsOut = Field(..., description="Настройки уведомлений")
    privacy_settings: PrivacySettingsOut = Field(..., description="Настройки приватности")

    # Статистика
    stats: ProfileStatsOut = Field(..., description="Статистика обучения")

    # Метаданные
    created_at: Optional[str] = Field(None, description="Дата создания профиля")
    updated_at: Optional[str] = Field(None, description="Дата последнего обновления")
    last_login: Optional[str] = Field(None, description="Последний вход")


class AccountStatusOut(Schema):
    """Схема статуса аккаунта."""

    is_active: bool = Field(..., description="Аккаунт активен")
    email_is_verified: bool = Field(..., description="Email подтвержден")
    has_completed_profile: bool = Field(..., description="Профиль заполнен")
    account_age_days: int = Field(..., ge=0, description="Возраст аккаунта (дни)")


class RefreshTokenIn(Schema):
    """Схема обновления токена."""

    refresh_token: str = Field(..., description="Refresh токен")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def serialize_profile(profile) -> dict:
    """
    Сериализация профиля в словарь.

    Args:
        profile: Объект Student

    Returns:
        dict: Словарь с данными профиля
    """
    return {
        "id": str(profile.id),
        "username": profile.user.username,
        "email": profile.user.email,
        "first_name": profile.user.first_name or "",
        "last_name": profile.user.last_name or "",
        "phone": str(profile.phone) if profile.phone else None,
        "birthday": str(profile.birthday) if profile.birthday else None,
        "gender": profile.gender or None,
        "country": profile.country.code if profile.country else None,
        "city": profile.city or "",
        "address": profile.address or "",
        "bio": profile.bio or None,
        "avatar_url": profile.avatar.url if profile.avatar else None,
        "role": profile.role.name if profile.role else None,
        "courses": (
            [course.name for course in profile.courses.all()] if hasattr(profile, "courses") else []
        ),
        "created_at": str(profile.created_at) if hasattr(profile, "created_at") else None,
    }


def serialize_role(role) -> dict:
    """
    Сериализация роли в словарь.

    Args:
        role: Объект Role

    Returns:
        dict: Словарь с данными роли
    """
    return {
        "name": role.name,
        "description": role.description or "",
    }


def serialize_course_brief(course) -> dict:
    """
    Сериализация курса в краткий словарь.

    Args:
        course: Объект Course

    Returns:
        dict: Словарь с краткими данными курса
    """
    return {
        "id": course.id,
        "name": course.name,
        "slug": course.slug,
    }


def calculate_profile_stats(profile) -> dict:
    """
    Подсчет статистики профиля.

    Args:
        profile: Объект Student

    Returns:
        dict: Словарь со статистикой
    """
    # TODO: Реализовать после добавления моделей прогресса
    return {
        "completed_lessons": 0,
        "total_lessons": 0,
        "active_courses": profile.courses.count() if hasattr(profile, "courses") else 0,
        "certificates_earned": 0,
        "study_streak_days": 0,
        "total_study_time_minutes": 0,
    }


def serialize_profile_detail(profile) -> dict:
    """
    Детальная сериализация профиля со всеми данными.

    Args:
        profile: Объект Student

    Returns:
        dict: Словарь с полными данными профиля
    """
    return {
        # Базовая информация
        "id": str(profile.id),
        "username": profile.user.username,
        "email": profile.user.email,
        "email_is_verified": profile.user.email_is_verified,
        # Персональные данные
        "first_name": profile.user.first_name or "",
        "last_name": profile.user.last_name or "",
        "phone": str(profile.phone) if profile.phone else None,
        "birthday": str(profile.birthday) if profile.birthday else None,
        "gender": profile.gender or None,
        "country": profile.country.code if profile.country else None,
        "city": profile.city or "",
        "address": profile.address or "",
        "bio": profile.bio or None,
        "avatar_url": profile.avatar.url if profile.avatar else None,
        # Роли и курсы
        "role": serialize_role(profile.role) if profile.role else None,
        "courses": (
            [serialize_course_brief(course) for course in profile.courses.all()]
            if hasattr(profile, "courses")
            else []
        ),
        # Настройки
        "notification_settings": {
            "email_notifications": profile.email_notifications,
            "course_updates": profile.course_updates,
            "lesson_reminders": profile.lesson_reminders,
            "achievement_alerts": profile.achievement_alerts,
            "weekly_summary": profile.weekly_summary,
            "marketing_emails": profile.marketing_emails,
        },
        "privacy_settings": {
            "profile_visibility": profile.profile_visibility,
            "show_progress": profile.show_progress,
            "show_achievements": profile.show_achievements,
            "allow_messages": profile.allow_messages,
        },
        # Статистика
        "stats": calculate_profile_stats(profile),
        # Метаданные
        "created_at": str(profile.created_at) if hasattr(profile, "created_at") else None,
        "updated_at": str(profile.updated_at) if hasattr(profile, "updated_at") else None,
        "last_login": str(profile.user.last_login) if profile.user.last_login else None,
    }
