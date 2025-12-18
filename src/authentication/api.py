"""
Authentication API - REST API для аутентификации.

Этот модуль содержит все эндпоинты для работы с аутентификацией пользователей.
Используется Django Ninja для автоматической генерации документации и валидации.

Особенности:
    - Полная типизация с помощью Pydantic схем
    - JWT аутентификация через ninja-jwt
    - Обработка всех возможных ошибок
    - Логирование всех операций
    - Валидация паролей через Django validators
    - Транзакционная безопасность

Endpoints:
    POST   /api/auth/register          - Регистрация
    POST   /api/auth/login             - Вход
    POST   /api/auth/logout            - Выход
    POST   /api/auth/password/change   - Смена пароля
    POST   /api/auth/password/reset    - Запрос сброса пароля
    POST   /api/auth/password/reset/confirm - Подтверждение сброса
    POST   /api/auth/email/verify      - Верификация email
    POST   /api/auth/email/resend      - Повторная отправка
    GET    /api/auth/profile           - Получение профиля
    PATCH  /api/auth/profile           - Обновление профиля
    PATCH  /api/auth/profile/email     - Обновление email

Автор: PySchool Team
Дата: 2025
"""

import logging
from typing import TYPE_CHECKING

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.password_validation import ValidationError as DjangoValidationError
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from ninja import Router
from ninja.errors import HttpError
from ninja_jwt.authentication import JWTAuth
from ninja_jwt.tokens import RefreshToken

from .schemas import (
    ChangePasswordIn,
    EmailUpdateIn,
    EmailVerifyIn,
    ErrorSchema,
    LoginIn,
    LoginOut,
    MessageSchema,
    PasswordResetConfirmIn,
    PasswordResetRequestIn,
    ProfileDetailOut,
    ProfileUpdateIn,
    RegisterIn,
    RegisterOut,
    SuccessSchema,
)

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser

# Настройка
User = get_user_model()
logger = logging.getLogger(__name__)

# Router
auth_router = Router(tags=["Authentication"])


# ============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================================


def generate_tokens_for_user(user: AbstractUser) -> dict:
    """Генерация JWT токенов для пользователя."""
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }


def validate_user_password(password: str, user: AbstractUser = None) -> None:
    """Валидация пароля с помощью Django validators."""
    try:
        validate_password(password, user=user)
    except DjangoValidationError as e:
        raise HttpError(400, "; ".join(e.messages)) from e


def serialize_user(user: AbstractUser) -> dict:
    """Сериализация пользователя в dict."""
    return {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_active": user.is_active,
        "date_joined": user.date_joined,
        "role": user.role.name if hasattr(user, "role") and user.role else None,
    }


def serialize_profile(user: AbstractUser) -> dict:
    """Сериализация профиля в dict в зависимости от роли пользователя."""
    # Базовые поля для всех ролей
    base_profile = {
        "phone": None,
        "country": None,
        "city": None,
        "bio": None,
        "avatar": None,
        "birthday": None,
        "gender": None,
    }

    # Получаем роль пользователя
    role_name = user.role_name if hasattr(user, "role_name") else None

    # Сериализация в зависимости от роли
    if role_name == "student" and hasattr(user, "student"):
        profile = user.student
        return {
            "phone": str(profile.phone) if profile.phone else None,
            "country": profile.country.code if profile.country else None,
            "city": profile.city or None,
            "bio": profile.bio or None,
            "avatar": profile.avatar.url if profile.avatar else None,
            "birthday": str(profile.birthday) if profile.birthday else None,
            "gender": profile.gender or None,
        }
    elif role_name == "reviewer" and hasattr(user, "reviewer"):
        profile = user.reviewer
        return {
            "bio": profile.bio or None,
            "expertise_areas": [area.name for area in profile.expertise_areas.all()],
            "is_active": profile.is_active,
            "total_reviews": profile.total_reviews,
            "average_review_time": float(profile.average_review_time),
        }
    elif role_name == "mentor" and hasattr(user, "mentor"):
        profile = user.mentor
        return {
            "bio": profile.bio or None,
            "expertise_areas": [area.name for area in profile.expertise_areas.all()],
            "is_active": profile.is_active,
        }
    elif role_name == "manager" and hasattr(user, "manager"):
        profile = user.manager
        return {
            "bio": profile.bio or None,
            "is_active": profile.is_active,
        }
    elif role_name == "admin" and hasattr(user, "admin"):
        profile = user.admin
        return {
            "bio": profile.bio or None,
            "is_active": profile.is_active,
        }
    elif role_name == "support" and hasattr(user, "support"):
        profile = user.support
        return {
            "bio": profile.bio or None,
            "is_active": profile.is_active,
        }

    return base_profile


# ============================================================================
# REGISTRATION & LOGIN
# ============================================================================


@auth_router.post("/register", response={201: RegisterOut, 400: ErrorSchema}, auth=None)
@transaction.atomic
def register(request, data: RegisterIn):
    """
    Регистрация нового пользователя.

    Создаёт User с указанной ролью (student по умолчанию) и связанный профиль.
    Поддерживаемые роли: student, mentor, reviewer, manager, admin, support.
    Автоматически создается профиль в зависимости от роли через сигнал.
    Автоматически генерирует JWT токены для немедленного входа.
    """
    from authentication.models import Role

    logger.info(f"Registration attempt: {data.email} with role: {data.role}")

    # Проверка уникальности email
    if User.objects.filter(email=data.email).exists():
        logger.warning(f"Email already registered: {data.email}")
        raise HttpError(400, "Email already registered")

    # Валидация пароля
    validate_user_password(data.password)

    # Получение роли
    try:
        role = Role.objects.get(name=data.role)
    except Role.DoesNotExist:
        logger.warning(f"Invalid role: {data.role}, using default 'student'")
        role = Role.objects.get(name="student")

    # Создание пользователя
    user = User.objects.create_user(
        email=data.email,
        password=data.password,
        first_name=data.first_name,
        last_name=data.last_name,
        role=role,
        is_active=True,
    )

    # Для admin роли установить is_staff=True для доступа в Django Admin
    if role.name == "admin":
        user.is_staff = True
        user.save()

    logger.info(f"User created: {user.id} ({user.email}) with role '{role.get_name_display()}'")

    # Генерация токенов
    tokens = generate_tokens_for_user(user)

    return 201, {
        "user": serialize_user(user),
        "tokens": tokens,
    }


@auth_router.post("/login", response={200: LoginOut, 401: ErrorSchema}, auth=None)
def login(request, data: LoginIn):
    """
    Вход в систему.

    Аутентифицирует пользователя и возвращает JWT токены.
    """
    logger.info(f"Login attempt: {data.email}")

    # Аутентификация
    user = authenticate(request, email=data.email, password=data.password)

    if user is None:
        logger.warning(f"Failed login attempt: {data.email}")
        raise HttpError(401, "Invalid email or password")

    if not user.is_active:
        logger.warning(f"Inactive user login attempt: {data.email}")
        raise HttpError(401, "User account is disabled")

    logger.info(f"Login successful: {user.email}")

    # Генерация токенов
    tokens = generate_tokens_for_user(user)

    return {
        "user": serialize_user(user),
        "tokens": tokens,
    }


@auth_router.post("/logout", response={200: MessageSchema}, auth=JWTAuth())
def logout(request):
    """
    Выход из системы.

    TODO: Добавить токен в blacklist.
    """
    logger.info(f"Logout: {request.user.email}")
    return {"message": "Successfully logged out"}


# ============================================================================
# УПРАВЛЕНИЕ ПАРОЛЕМ
# ============================================================================


@auth_router.post(
    "/password/change", response={200: SuccessSchema, 400: ErrorSchema}, auth=JWTAuth()
)
def change_password(request, data: ChangePasswordIn):
    """Смена пароля для аутентифицированного пользователя."""
    user = request.user
    logger.info(f"Password change request: {user.email}")

    # Проверка старого пароля
    if not user.check_password(data.old_password):
        logger.warning(f"Wrong old password: {user.email}")
        raise HttpError(400, "Old password is incorrect")

    # Валидация нового пароля
    validate_user_password(data.new_password, user=user)

    # Смена пароля
    user.set_password(data.new_password)
    user.save()

    logger.info(f"Password changed successfully: {user.email}")

    return {"success": True, "message": "Password changed successfully"}


@auth_router.post("/password/reset", response={200: MessageSchema}, auth=None)
def password_reset_request(request, data: PasswordResetRequestIn):
    """Запрос сброса пароля (отправка email)."""
    logger.info(f"Password reset request: {data.email}")

    try:
        user = User.objects.get(email=data.email, is_active=True)
        # TODO: Отправить email с токеном сброса
        logger.info(f"Password reset email sent: {user.email}")
    except User.DoesNotExist:
        # Не раскрываем существование email
        logger.info(f"Password reset request for non-existent email: {data.email}")

    return {"message": "If email exists, password reset instructions have been sent"}


@auth_router.post(
    "/password/reset/confirm", response={200: SuccessSchema, 400: ErrorSchema}, auth=None
)
def password_reset_confirm(request, data: PasswordResetConfirmIn):
    """Подтверждение сброса пароля по токену."""
    # TODO: Валидация токена и сброс пароля
    logger.info("Password reset confirm attempt")
    raise HttpError(400, "Not implemented yet")


# ============================================================================
# УПРАВЛЕНИЕ EMAIL
# ============================================================================


@auth_router.post("/email/verify", response={200: SuccessSchema, 400: ErrorSchema}, auth=None)
def email_verify(request, data: EmailVerifyIn):
    """Верификация email по токену."""
    # TODO: Валидация токена и верификация email
    logger.info("Email verification attempt")
    raise HttpError(400, "Not implemented yet")


@auth_router.post("/email/resend", response={200: MessageSchema}, auth=JWTAuth())
def email_resend_verification(request):
    """Повторная отправка письма для верификации email."""
    user = request.user
    logger.info(f"Resend verification email: {user.email}")

    # TODO: Отправить email

    return {"message": "Verification email sent"}


# ============================================================================
# УПРАВЛЕНИЕ ПРОФИЛЕМ
# ============================================================================


@auth_router.get("/profile", response={200: ProfileDetailOut}, auth=JWTAuth())
def get_profile(request):
    """Получение профиля текущего пользователя."""
    user = request.user
    logger.info(f"Get profile: {user.email}")

    return {
        "user": serialize_user(user),
        "profile": serialize_profile(user),
    }


@auth_router.patch("/profile", response={200: ProfileDetailOut, 400: ErrorSchema}, auth=JWTAuth())
@transaction.atomic
def update_profile(request, data: ProfileUpdateIn):
    """Обновление профиля (частичное обновление)."""
    user = request.user
    logger.info(f"Update profile: {user.email}")

    # Обновление User полей
    if data.first_name is not None:
        user.first_name = data.first_name
    if data.last_name is not None:
        user.last_name = data.last_name
    user.save()

    # Обновление Profile полей
    if hasattr(user, "student"):
        profile = user.student

        if data.phone is not None:
            profile.phone = data.phone
        if data.country is not None:
            profile.country = data.country
        if data.city is not None:
            profile.city = data.city
        if data.bio is not None:
            profile.bio = data.bio
        if data.birthday is not None:
            profile.birthday = data.birthday
        if data.gender is not None:
            profile.gender = data.gender.value

        profile.save()

    logger.info(f"Profile updated successfully: {user.email}")

    return {
        "user": serialize_user(user),
        "profile": serialize_profile(user),
    }


@auth_router.patch(
    "/profile/email", response={200: SuccessSchema, 400: ErrorSchema}, auth=JWTAuth()
)
@transaction.atomic
def update_email(request, data: EmailUpdateIn):
    """Обновление email с подтверждением паролем."""
    user = request.user
    logger.info(f"Email update request: {user.email} -> {data.new_email}")

    # Проверка пароля
    if not user.check_password(data.password):
        logger.warning(f"Wrong password for email update: {user.email}")
        raise HttpError(400, "Password is incorrect")

    # Проверка уникальности нового email
    if User.objects.filter(email=data.new_email).exclude(id=user.id).exists():
        logger.warning(f"Email already taken: {data.new_email}")
        raise HttpError(400, "Email already taken")

    # Обновление email
    user.email = data.new_email
    user.save()

    logger.info(f"Email updated successfully: {user.email}")

    return {"success": True, "message": "Email updated successfully"}
