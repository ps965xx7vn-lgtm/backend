"""
Account API - REST API для управления учетными записями.

Этот модуль содержит все эндпоинты для работы с аккаунтами пользователей.
Используется Django Ninja для автоматической генерации документации и валидации.

Особенности:
    - Полная типизация с помощью Pydantic схем
    - Обработка всех возможных ошибок
    - Логирование всех операций
    - JWT аутентификация для защищенных эндпоинтов
    - Транзакции для критичных операций

Архитектура:
    - Public endpoints: Регистрация и вход (POST /register, /login)
    - Protected endpoints: Требуют JWT токен (GET/PATCH/DELETE)
    - Settings endpoints: Управление настройками профиля

Автор: PySchool Team
Дата: 2025
"""

import logging
from typing import Dict

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import ValidationError, validate_password
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from ninja import Router
from ninja.errors import HttpError
from ninja_jwt.authentication import JWTAuth
from ninja_jwt.tokens import RefreshToken

from authentication.models import Student

from .schemas import (  # Stats schemas; Helper schemas; Settings schemas; Profile schemas; Auth schemas; Helper functions
    AccountStatusOut,
    ChangePasswordIn,
    EmailUpdateIn,
    LoginIn,
    LoginOut,
    MessageSchema,
    NotificationSettingsOut,
    NotificationSettingsUpdate,
    PrivacySettingsOut,
    PrivacySettingsUpdate,
    ProfileDetailOut,
    ProfileOut,
    ProfileUpdate,
    RefreshTokenIn,
    RegisterIn,
    RegisterOut,
    SuccessSchema,
    TokenOut,
    UsernameUpdateIn,
    serialize_profile,
    serialize_profile_detail,
)

# Настройка логирования
logger = logging.getLogger(__name__)

# Router с тегом для автоматической группировки в OpenAPI документации
router = Router(tags=["Account"])

# Модель пользователя
UserModel = get_user_model()

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def generate_tokens_for_user(user) -> Dict[str, str]:
    """
    Генерация JWT токенов для пользователя.

    Args:
        user: Объект пользователя Django

    Returns:
        dict: Словарь с access_token и refresh_token
    """
    refresh = RefreshToken.for_user(user)
    return {
        "access_token": str(refresh.access_token),
        "refresh_token": str(refresh),
    }


def validate_user_password(password: str, user=None) -> None:
    """
    Валидация пароля с помощью Django validators.

    Args:
        password: Пароль для проверки
        user: Объект пользователя (опционально)

    Raises:
        HttpError: Если пароль не прошел валидацию
    """
    try:
        validate_password(password, user)
    except ValidationError as e:
        logger.warning(f"API: Валидация пароля не пройдена: {e.messages}")
        raise HttpError(400, "; ".join(e.messages))


# ============================================================================
# AUTH ENDPOINTS
# ============================================================================


@router.post("/register", response={201: RegisterOut}, auth=None)
@transaction.atomic
def register(request, payload: RegisterIn) -> tuple[int, RegisterOut]:
    """
    Регистрация нового пользователя в системе.

    Создает учетную запись User и связанный профиль Profile.
    Автоматически генерирует JWT токены для авторизации.

    Args:
        request: HTTP запрос
        payload (RegisterIn): Данные для регистрации
            - email: Email адрес
            - password: Пароль (минимум 8 символов)
            - first_name: Имя (опционально)
            - phone: Телефон (опционально)

    Returns:
        tuple[int, RegisterOut]: Статус 201 и данные пользователя с токенами

    Raises:
        HttpError 400: Email уже занят или пароль не валиден
    """
    logger.info(f"API: Попытка регистрации пользователя: {payload.email}")

    # Проверка уникальности email
    if UserModel.objects.filter(email=payload.email).exists():
        logger.warning(f"API: Email уже зарегистрирован: {payload.email}")
        raise HttpError(400, "Email already registered")

    # Валидация пароля
    validate_user_password(payload.password)

    # Создание пользователя
    user = UserModel.objects.create_user(
        email=payload.email,
        username=payload.email.split("@")[0],  # Генерируем username из email
        password=payload.password,
        first_name=payload.first_name or "",
        is_active=True,
    )
    logger.info(f"API: Создан пользователь: {user.id} ({user.email})")

    # Создание студента
    student, created = Student.objects.get_or_create(user=user)
    if payload.phone:
        student.phone = payload.phone
        student.save(update_fields=["phone"])

    # Генерация токенов
    tokens = generate_tokens_for_user(user)

    # Сериализация студента
    profile_data = serialize_profile(user.student)

    logger.info(f"API: Регистрация успешна для: {user.email}")

    return 201, RegisterOut(
        profile=ProfileOut(**profile_data),
        tokens=TokenOut(**tokens),
    )


@router.post("/login", response=LoginOut, auth=None)
def login_view(request, payload: LoginIn) -> LoginOut:
    """
    Аутентификация пользователя в системе.

    Проверяет email и пароль, возвращает профиль и JWT токены.

    Args:
        request: HTTP запрос
        payload (LoginIn): Данные для входа
            - email: Email адрес
            - password: Пароль

    Returns:
        LoginOut: Профиль пользователя и токены

    Raises:
        HttpError 401: Неверные учетные данные
        HttpError 403: Аккаунт деактивирован
    """
    logger.info(f"API: Попытка входа для: {payload.email}")

    try:
        user = UserModel.objects.get(email=payload.email)
    except ObjectDoesNotExist:
        logger.warning(f"API: Пользователь не найден: {payload.email}")
        raise HttpError(401, "Invalid credentials")

    # Проверка пароля
    if not user.check_password(payload.password):
        logger.warning(f"API: Неверный пароль для: {payload.email}")
        raise HttpError(401, "Invalid credentials")

    # Проверка активности аккаунта
    if not user.is_active:
        logger.warning(f"API: Попытка входа в деактивированный аккаунт: {payload.email}")
        raise HttpError(403, "Account is deactivated")

    # Генерация токенов
    tokens = generate_tokens_for_user(user)

    # Сериализация профиля
    profile_data = serialize_profile(request.user.student)

    logger.info(f"API: Успешный вход для: {user.email}")

    return LoginOut(
        profile=ProfileOut(**profile_data),
        tokens=TokenOut(**tokens),
    )


@router.post("/password/change", response=SuccessSchema, auth=JWTAuth())
def change_password(request, payload: ChangePasswordIn) -> SuccessSchema:
    """
    Смена пароля текущего пользователя.

    Проверяет старый пароль и валидирует новый через Django validators.

    Args:
        request: HTTP запрос (с JWT аутентификацией)
        payload (ChangePasswordIn): Данные для смены пароля
            - old_password: Текущий пароль
            - new_password: Новый пароль (минимум 8 символов)

    Returns:
        SuccessSchema: Статус операции

    Raises:
        HttpError 400: Старый пароль неверен или новый пароль не валиден
    """
    user = request.user
    logger.info(f"API: Попытка смены пароля для: {user.email}")

    # Проверка старого пароля
    if not user.check_password(payload.old_password):
        logger.warning(f"API: Неверный старый пароль для: {user.email}")
        raise HttpError(400, "Old password is incorrect")

    # Валидация нового пароля
    validate_user_password(payload.new_password, user)

    # Смена пароля
    user.set_password(payload.new_password)
    user.save(update_fields=["password"])

    logger.info(f"API: Пароль успешно изменен для: {user.email}")

    return SuccessSchema(success=True)


# ============================================================================
# PROFILE ENDPOINTS
# ============================================================================


@router.get("/profile", response=ProfileOut, auth=JWTAuth())
def profile_get(request) -> ProfileOut:
    """
    Получение профиля текущего пользователя.

    Возвращает все данные профиля включая роли и курсы.

    Args:
        request: HTTP запрос (с JWT аутентификацией)

    Returns:
        ProfileOut: Данные профиля
    """
    logger.info(f"API: Запрос профиля для: {request.user.email}")

    profile_data = serialize_profile(request.user.student)
    return ProfileOut(**profile_data)


@router.patch("/profile", response=ProfileOut, auth=JWTAuth())
@transaction.atomic
def profile_patch(request, data: ProfileUpdate) -> ProfileOut:
    """
    Частичное обновление профиля пользователя.

    Позволяет обновить любые поля профиля (только переданные поля).
    Поля User (first_name, last_name) сохраняются в модели User.
    Остальные поля сохраняются в модели Profile.

    Args:
        request: HTTP запрос (с JWT аутентификацией)
        data (ProfileUpdate): Данные для обновления
            - first_name: Имя (опционально)
            - last_name: Фамилия (опционально)
            - phone: Телефон (опционально)
            - birthday: Дата рождения (опционально)
            - gender: Пол (опционально)
            - country: Код страны (опционально)
            - city: Город (опционально)
            - address: Адрес (опционально)
            - bio: О себе (опционально)

    Returns:
        ProfileOut: Обновленные данные профиля
    """
    profile: Student = request.user.student
    user = request.user
    payload = data.dict(exclude_none=True)

    logger.info(f"API: Обновление профиля для: {user.email}, поля: {list(payload.keys())}")

    if not payload:
        raise HttpError(400, "No data to update")

    # Поля User
    user_fields = ["first_name", "last_name"]
    user_updated_fields = []

    for field in user_fields:
        if field in payload:
            setattr(user, field, payload.pop(field))
            user_updated_fields.append(field)

    if user_updated_fields:
        user.save(update_fields=user_updated_fields)

    # Поля Profile
    if payload:
        for field, value in payload.items():
            setattr(profile, field, value)
        profile.save(update_fields=list(payload.keys()))

    logger.info(f"API: Профиль успешно обновлен для: {user.email}")

    profile_data = serialize_profile(profile)
    return ProfileOut(**profile_data)


# ============================================================================
# SETTINGS ENDPOINTS - NOTIFICATIONS
# ============================================================================


@router.get("/settings/notifications", response=NotificationSettingsOut, auth=JWTAuth())
def get_notification_settings(request) -> NotificationSettingsOut:
    """
    Получение настроек уведомлений пользователя.

    Args:
        request: HTTP запрос (с JWT аутентификацией)

    Returns:
        NotificationSettingsOut: Настройки уведомлений
    """
    profile = request.user.student
    logger.info(f"API: Запрос настроек уведомлений для: {request.user.email}")

    return NotificationSettingsOut(
        email_notifications=profile.email_notifications,
        course_updates=profile.course_updates,
        lesson_reminders=profile.lesson_reminders,
        achievement_alerts=profile.achievement_alerts,
        weekly_summary=profile.weekly_summary,
        marketing_emails=profile.marketing_emails,
    )


@router.patch("/settings/notifications", response=NotificationSettingsOut, auth=JWTAuth())
def update_notification_settings(
    request, data: NotificationSettingsUpdate
) -> NotificationSettingsOut:
    """
    Обновление настроек уведомлений пользователя.

    Позволяет изменить любые настройки уведомлений (только переданные поля).

    Args:
        request: HTTP запрос (с JWT аутентификацией)
        data (NotificationSettingsUpdate): Настройки для обновления
            - email_notifications: Уведомления по email (опционально)
            - course_updates: Обновления курсов (опционально)
            - lesson_reminders: Напоминания о уроках (опционально)
            - achievement_alerts: Уведомления о достижениях (опционально)
            - weekly_summary: Еженедельная сводка (опционально)
            - marketing_emails: Маркетинговые письма (опционально)

    Returns:
        NotificationSettingsOut: Обновленные настройки

    Raises:
        HttpError 400: Нет данных для обновления
    """
    profile = request.user.student
    payload = data.dict(exclude_none=True)

    logger.info(
        f"API: Обновление настроек уведомлений для: {request.user.email}, поля: {list(payload.keys())}"
    )

    if not payload:
        logger.warning(f"API: Попытка обновления без данных для: {request.user.email}")
        raise HttpError(400, "No data to update")

    # Обновление полей
    for field, value in payload.items():
        setattr(profile, field, value)

    profile.save(update_fields=list(payload.keys()))

    logger.info(f"API: Настройки уведомлений обновлены для: {request.user.email}")

    return NotificationSettingsOut(
        email_notifications=profile.email_notifications,
        course_updates=profile.course_updates,
        lesson_reminders=profile.lesson_reminders,
        achievement_alerts=profile.achievement_alerts,
        weekly_summary=profile.weekly_summary,
        marketing_emails=profile.marketing_emails,
    )


# ============================================================================
# SETTINGS ENDPOINTS - PRIVACY
# ============================================================================


@router.get("/settings/privacy", response=PrivacySettingsOut, auth=JWTAuth())
def get_privacy_settings(request) -> PrivacySettingsOut:
    """
    Получение настроек приватности пользователя.

    Args:
        request: HTTP запрос (с JWT аутентификацией)

    Returns:
        PrivacySettingsOut: Настройки приватности
    """
    profile = request.user.student
    logger.info(f"API: Запрос настроек приватности для: {request.user.email}")

    return PrivacySettingsOut(
        profile_visibility=profile.profile_visibility,
        show_progress=profile.show_progress,
        show_achievements=profile.show_achievements,
        allow_messages=profile.allow_messages,
    )


@router.patch("/settings/privacy", response=PrivacySettingsOut, auth=JWTAuth())
def update_privacy_settings(request, data: PrivacySettingsUpdate) -> PrivacySettingsOut:
    """
    Обновление настроек приватности пользователя.

    Позволяет изменить любые настройки приватности (только переданные поля).

    Args:
        request: HTTP запрос (с JWT аутентификацией)
        data (PrivacySettingsUpdate): Настройки для обновления
            - profile_visibility: Видимость профиля (public/students/private)
            - show_progress: Показывать прогресс (опционально)
            - show_achievements: Показывать достижения (опционально)
            - allow_messages: Разрешить сообщения (опционально)

    Returns:
        PrivacySettingsOut: Обновленные настройки

    Raises:
        HttpError 400: Нет данных для обновления или неверное значение
    """
    profile = request.user.student
    payload = data.dict(exclude_none=True)

    logger.info(
        f"API: Обновление настроек приватности для: {request.user.email}, поля: {list(payload.keys())}"
    )

    if not payload:
        logger.warning(f"API: Попытка обновления без данных для: {request.user.email}")
        raise HttpError(400, "No data to update")

    # Валидация profile_visibility
    if "profile_visibility" in payload:
        valid_values = ["public", "students", "private"]
        if payload["profile_visibility"] not in valid_values:
            logger.warning(
                f"API: Неверное значение profile_visibility: {payload['profile_visibility']}"
            )
            raise HttpError(
                400, f"Invalid profile_visibility. Must be one of: {', '.join(valid_values)}"
            )

    # Обновление полей
    for field, value in payload.items():
        setattr(profile, field, value)

    profile.save(update_fields=list(payload.keys()))

    logger.info(f"API: Настройки приватности обновлены для: {request.user.email}")

    return PrivacySettingsOut(
        profile_visibility=profile.profile_visibility,
        show_progress=profile.show_progress,
        show_achievements=profile.show_achievements,
        allow_messages=profile.allow_messages,
    )


# ============================================================================
# ACCOUNT MANAGEMENT ENDPOINTS
# ============================================================================


@router.delete("/account", response=MessageSchema, auth=JWTAuth())
@transaction.atomic
def delete_account(request) -> MessageSchema:
    """
    Деактивация аккаунта пользователя.

    Устанавливает флаг is_active=False, что блокирует вход в систему.
    Данные пользователя сохраняются для возможного восстановления.

    Args:
        request: HTTP запрос (с JWT аутентификацией)

    Returns:
        MessageSchema: Сообщение об успешной деактивации
    """
    user = request.user
    logger.warning(f"API: Деактивация аккаунта для: {user.email}")

    user.is_active = False
    user.save(update_fields=["is_active"])

    logger.info(f"API: Аккаунт деактивирован для: {user.email}")

    return MessageSchema(message="Account deactivated successfully")


# ============================================================================
# PROFILE DETAIL ENDPOINT
# ============================================================================


@router.get("/profile/detail", response=ProfileDetailOut, auth=JWTAuth())
def profile_detail_get(request) -> ProfileDetailOut:
    """
    Получение детального профиля с полной информацией.

    Включает статистику, настройки, роли и курсы с дополнительными деталями.
    Оптимизировано для мобильного приложения - все данные в одном запросе.

    Args:
        request: HTTP запрос (с JWT аутентификацией)

    Returns:
        ProfileDetailOut: Детальные данные профиля со всей информацией
    """
    logger.info(f"API: Запрос детального профиля для: {request.user.email}")

    profile = request.user.student
    profile_data = serialize_profile_detail(profile)

    return ProfileDetailOut(**profile_data)


# ============================================================================
# ACCOUNT INFO ENDPOINTS
# ============================================================================


@router.get("/status", response=AccountStatusOut, auth=JWTAuth())
def get_account_status(request) -> AccountStatusOut:
    """
    Получение статуса аккаунта.

    Возвращает информацию о состоянии аккаунта:
    - Активен ли аккаунт
    - Подтвержден ли email
    - Заполнен ли профиль
    - Возраст аккаунта

    Args:
        request: HTTP запрос (с JWT аутентификацией)

    Returns:
        AccountStatusOut: Статус аккаунта
    """
    from django.utils import timezone

    user = request.user
    profile = user.student

    logger.info(f"API: Запрос статуса аккаунта для: {user.email}")

    # Проверка заполненности профиля
    has_completed_profile = all(
        [
            profile.user.first_name,
            profile.user.last_name,
            profile.phone or profile.city,
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


@router.patch("/email", response=ProfileOut, auth=JWTAuth())
@transaction.atomic
def update_email(request, data: EmailUpdateIn) -> ProfileOut:
    """
    Обновление email адреса пользователя.

    Требует подтверждения текущим паролем.
    После обновления email помечается как неподтвержденный.

    Args:
        request: HTTP запрос (с JWT аутентификацией)
        data (EmailUpdateIn): Новый email и пароль для подтверждения

    Returns:
        ProfileOut: Обновленные данные профиля

    Raises:
        HttpError 400: Неверный пароль
        HttpError 409: Email уже используется
    """
    user = request.user

    logger.info(f"API: Попытка обновления email для: {user.email} -> {data.new_email}")

    # Проверка пароля
    if not user.check_password(data.password):
        logger.warning(f"API: Неверный пароль при обновлении email для: {user.email}")
        raise HttpError(400, "Invalid password")

    # Проверка уникальности email
    if UserModel.objects.filter(email=data.new_email).exclude(id=user.id).exists():
        logger.warning(f"API: Email уже используется: {data.new_email}")
        raise HttpError(409, "Email already in use")

    # Обновление email
    user.email = data.new_email
    user.email_is_verified = False
    user.save(update_fields=["email", "email_is_verified"])

    logger.info(f"API: Email успешно обновлен для: {user.id}")

    profile_data = serialize_profile(user.student)
    return ProfileOut(**profile_data)


@router.patch("/username", response=ProfileOut, auth=JWTAuth())
def update_username(request, data: UsernameUpdateIn) -> ProfileOut:
    """
    Обновление username пользователя.

    Args:
        request: HTTP запрос (с JWT аутентификацией)
        data (UsernameUpdateIn): Новый username

    Returns:
        ProfileOut: Обновленные данные профиля

    Raises:
        HttpError 409: Username уже используется
    """
    user = request.user

    logger.info(f"API: Обновление username для: {user.email} -> {data.username}")

    # Проверка уникальности username
    if UserModel.objects.filter(username=data.username).exclude(id=user.id).exists():
        logger.warning(f"API: Username уже используется: {data.username}")
        raise HttpError(409, "Username already in use")

    user.username = data.username
    user.save(update_fields=["username"])

    logger.info(f"API: Username успешно обновлен для: {user.email}")

    profile_data = serialize_profile(user.student)
    return ProfileOut(**profile_data)


# ============================================================================
# TOKEN MANAGEMENT ENDPOINTS
# ============================================================================


@router.post("/token/refresh", response=TokenOut, auth=None)
def refresh_token(request, data: RefreshTokenIn) -> TokenOut:
    """
    Обновление access токена с помощью refresh токена.

    Позволяет получить новый access токен без повторной аутентификации.

    Args:
        request: HTTP запрос
        data (RefreshTokenIn): Refresh токен

    Returns:
        TokenOut: Новые токены

    Raises:
        HttpError 401: Невалидный или истекший токен
    """
    from ninja_jwt.tokens import RefreshToken as JWTRefreshToken

    logger.info("API: Запрос обновления токена")

    try:
        refresh = JWTRefreshToken(data.refresh_token)

        return TokenOut(
            access_token=str(refresh.access_token),
            refresh_token=str(refresh),
        )
    except Exception as e:
        logger.warning(f"API: Ошибка обновления токена: {e}")
        raise HttpError(401, "Invalid or expired refresh token")


@router.post("/token/verify", response=SuccessSchema, auth=JWTAuth())
def verify_token(request) -> SuccessSchema:
    """
    Проверка валидности access токена.

    Простой эндпоинт для проверки что токен действителен.
    Используется для проверки авторизации перед выполнением операций.

    Args:
        request: HTTP запрос (с JWT аутентификацией)

    Returns:
        SuccessSchema: Подтверждение валидности токена
    """
    logger.info(f"API: Проверка токена для: {request.user.email}")
    return SuccessSchema(success=True)


# ============================================================================
# AVATAR MANAGEMENT ENDPOINT
# ============================================================================


@router.post("/avatar/upload", response=ProfileOut, auth=JWTAuth())
@transaction.atomic
def upload_avatar(request) -> ProfileOut:
    """
    Загрузка аватара пользователя.

    Принимает изображение через multipart/form-data.
    Автоматически обрабатывает и сохраняет файл.

    Args:
        request: HTTP запрос (с JWT аутентификацией)
        - request.FILES['avatar']: Файл изображения

    Returns:
        ProfileOut: Обновленные данные профиля с новым аватаром

    Raises:
        HttpError 400: Файл не предоставлен или неверный формат
    """
    profile = request.user.student

    logger.info(f"API: Загрузка аватара для: {request.user.email}")

    if "avatar" not in request.FILES:
        raise HttpError(400, "No avatar file provided")

    avatar_file = request.FILES["avatar"]

    # Проверка типа файла
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if avatar_file.content_type not in allowed_types:
        logger.warning(f"API: Неверный тип файла аватара: {avatar_file.content_type}")
        raise HttpError(400, f"Invalid file type. Allowed: {', '.join(allowed_types)}")

    # Проверка размера (макс 5MB)
    max_size = 5 * 1024 * 1024  # 5MB
    if avatar_file.size > max_size:
        logger.warning(f"API: Файл аватара слишком большой: {avatar_file.size} bytes")
        raise HttpError(400, "File too large. Maximum size: 5MB")

    # Удаление старого аватара если есть
    if profile.avatar:
        profile.avatar.delete(save=False)

    # Сохранение нового аватара
    profile.avatar = avatar_file
    profile.save(update_fields=["avatar"])

    logger.info(f"API: Аватар успешно загружен для: {request.user.email}")

    profile_data = serialize_profile(profile)
    return ProfileOut(**profile_data)


@router.delete("/avatar", response=MessageSchema, auth=JWTAuth())
@transaction.atomic
def delete_avatar(request) -> MessageSchema:
    """
    Удаление аватара пользователя.

    Args:
        request: HTTP запрос (с JWT аутентификацией)

    Returns:
        MessageSchema: Подтверждение удаления
    """
    profile = request.user.student

    logger.info(f"API: Удаление аватара для: {request.user.email}")

    if profile.avatar:
        profile.avatar.delete(save=True)
        logger.info(f"API: Аватар удален для: {request.user.email}")
        return MessageSchema(message="Avatar deleted successfully")
    else:
        raise HttpError(404, "No avatar found")
