"""
Pydantic схемы для Authentication API.

Этот модуль содержит все схемы для валидации входных/выходных данных API.
Используется Django Ninja с Pydantic для автоматической валидации и документации.

Архитектура:
    - Input схемы: *In - для входящих данных (POST, PATCH)
    - Output схемы: *Out - для исходящих данных (GET)
    - Base схемы: Общие схемы для всех эндпоинтов

Автор: PySchool Team
Дата: 2025
"""

from datetime import date, datetime
from enum import Enum
from typing import Optional

from ninja import Field, Schema
from pydantic import EmailStr, field_validator, model_validator

# ============================================================================
# ENUMS
# ============================================================================


class Gender(str, Enum):
    """Пол пользователя."""

    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


# ============================================================================
# BASE SCHEMAS
# ============================================================================


class ErrorSchema(Schema):
    """Схема ответа при ошибке."""

    detail: str = Field(..., description="Описание ошибки")
    code: Optional[str] = Field(None, description="Код ошибки")


class MessageSchema(Schema):
    """Схема простого сообщения."""

    message: str = Field(..., description="Текст сообщения")


class SuccessSchema(Schema):
    """Схема успешного ответа."""

    success: bool = Field(True, description="Статус операции")
    message: Optional[str] = Field(None, description="Дополнительное сообщение")


# ============================================================================
# USER & PROFILE SCHEMAS
# ============================================================================


class UserOut(Schema):
    """Схема вывода пользователя."""

    id: int = Field(..., description="ID пользователя")
    email: str = Field(..., description="Email пользователя")
    first_name: str = Field(..., description="Имя")
    last_name: str = Field(..., description="Фамилия")
    is_active: bool = Field(..., description="Активен ли пользователь")
    date_joined: datetime = Field(..., description="Дата регистрации")
    role: Optional[str] = Field(None, description="Роль пользователя")


class ProfileOut(Schema):
    """Схема вывода профиля."""

    phone: Optional[str] = Field(None, description="Телефон")
    country: Optional[str] = Field(None, description="Страна")
    city: Optional[str] = Field(None, description="Город")
    bio: Optional[str] = Field(None, description="О себе")
    avatar: Optional[str] = Field(None, description="URL аватара")
    birthday: Optional[str] = Field(None, description="Дата рождения")
    gender: Optional[str] = Field(None, description="Пол")


# ============================================================================
# REGISTRATION & LOGIN SCHEMAS
# ============================================================================


class RegisterIn(Schema):
    """Схема регистрации нового пользователя."""

    email: EmailStr = Field(..., description="Email адрес")
    password: str = Field(..., min_length=8, max_length=128, description="Пароль")
    confirm_password: str = Field(
        ..., min_length=8, max_length=128, description="Подтверждение пароля"
    )
    first_name: str = Field(..., min_length=1, max_length=150, description="Имя")
    last_name: str = Field(..., min_length=1, max_length=150, description="Фамилия")
    role: Optional[str] = Field(
        default="student", description="Роль: student, mentor, reviewer, manager, admin, support"
    )

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        """Нормализация email (lowercase)."""
        return v.lower().strip()

    @model_validator(mode="after")
    def check_passwords_match(self) -> "RegisterIn":
        """Проверка совпадения паролей."""
        if self.password != self.confirm_password:
            raise ValueError("Пароли не совпадают")
        return self

    @field_validator("first_name", "last_name")
    @classmethod
    def capitalize_name(cls, v: str) -> str:
        """Приведение имени к Title Case."""
        return v.strip().title()


class RegisterOut(Schema):
    """Схема ответа после регистрации."""

    user: UserOut = Field(..., description="Данные пользователя")
    tokens: dict = Field(..., description="JWT токены (access и refresh)")


class LoginIn(Schema):
    """Схема входа в систему."""

    email: str = Field(..., description="Email адрес")
    password: str = Field(..., description="Пароль")

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        """Нормализация email (lowercase)."""
        return v.lower().strip()


class LoginOut(Schema):
    """Схема ответа после входа."""

    user: UserOut = Field(..., description="Данные пользователя")
    tokens: dict = Field(..., description="JWT токены (access и refresh)")


# ============================================================================
# СХЕМЫ ДЛЯ ПАРОЛЯ
# ============================================================================


class ChangePasswordIn(Schema):
    """Схема смены пароля."""

    old_password: str = Field(..., description="Старый пароль")
    new_password: str = Field(..., min_length=8, max_length=128, description="Новый пароль")
    confirm_new_password: str = Field(
        ..., min_length=8, max_length=128, description="Подтверждение нового пароля"
    )

    @model_validator(mode="after")
    def check_passwords_match(self) -> "ChangePasswordIn":
        """Проверка совпадения паролей."""
        if self.new_password != self.confirm_new_password:
            raise ValueError("Новые пароли не совпадают")
        return self


class PasswordResetRequestIn(Schema):
    """Схема запроса сброса пароля."""

    email: str = Field(..., description="Email адрес")

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        """Нормализация email (lowercase)."""
        return v.lower().strip()


class PasswordResetConfirmIn(Schema):
    """Схема подтверждения сброса пароля."""

    token: str = Field(..., description="Токен сброса")
    new_password: str = Field(..., min_length=8, max_length=128, description="Новый пароль")


# ============================================================================
# EMAIL SCHEMAS
# ============================================================================


class EmailVerifyIn(Schema):
    """Схема верификации email."""

    token: str = Field(..., description="Токен верификации")


class EmailUpdateIn(Schema):
    """Схема обновления email."""

    new_email: str = Field(..., min_length=5, max_length=254, description="Новый email")
    password: str = Field(..., description="Текущий пароль для подтверждения")

    @field_validator("new_email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        """Нормализация email (lowercase)."""
        return v.lower().strip()


# ============================================================================
# СХЕМЫ ДЛЯ ОБНОВЛЕНИЯ ПРОФИЛЯ
# ============================================================================


class ProfileUpdateIn(Schema):
    """Схема обновления профиля (частичное обновление)."""

    first_name: Optional[str] = Field(None, min_length=1, max_length=150, description="Имя")
    last_name: Optional[str] = Field(None, min_length=1, max_length=150, description="Фамилия")
    phone: Optional[str] = Field(None, max_length=20, description="Телефон")
    country: Optional[str] = Field(None, max_length=2, description="Код страны (ISO)")
    city: Optional[str] = Field(None, max_length=100, description="Город")
    bio: Optional[str] = Field(None, max_length=500, description="О себе")
    birthday: Optional[date] = Field(None, description="Дата рождения")
    gender: Optional[Gender] = Field(None, description="Пол")

    @field_validator("first_name", "last_name")
    @classmethod
    def capitalize_name(cls, v: Optional[str]) -> Optional[str]:
        """Приведение имени к Title Case."""
        return v.strip().title() if v else None

    @field_validator("country")
    @classmethod
    def uppercase_country(cls, v: Optional[str]) -> Optional[str]:
        """Приведение кода страны к верхнему регистру."""
        return v.upper() if v else None


class ProfileDetailOut(Schema):
    """Детальная схема профиля (с данными пользователя)."""

    user: UserOut = Field(..., description="Данные пользователя")
    profile: ProfileOut = Field(..., description="Данные профиля")
