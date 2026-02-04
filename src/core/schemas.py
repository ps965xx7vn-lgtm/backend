"""
Core API Schemas Module

Pydantic схемы для валидации и сериализации данных Core API.

Схемы:
- FeedbackSchema: схема для создания обратной связи
- SubscriptionSchema: схема для подписки на рассылку
- ContactInfoSchema: схема с контактной информацией
- StatsSchema: схема для статистики платформы
"""

import re

from pydantic import BaseModel, EmailStr, Field, validator


class FeedbackSchema(BaseModel):
    """
    Схема для создания обратной связи через API.

    Attributes:
        first_name: Имя отправителя (1-100 символов)
        phone_number: Телефон в международном формате (+1234567890)
        email: Email адрес
        message: Текст сообщения (минимум 10 символов)
        agree_terms: Согласие с условиями (по умолчанию False)

    Example:
        >>> feedback = FeedbackSchema(
        >>>     first_name="Иван",
        >>>     phone_number="+79991234567",
        >>>     email="ivan@example.com",
        >>>     message="Хочу узнать о курсах",
        >>>     agree_terms=True
        >>> )
    """

    first_name: str = Field(..., min_length=1, max_length=100, description="Имя отправителя")
    phone_number: str = Field(
        ..., min_length=10, max_length=20, description="Телефон в формате +1234567890"
    )
    email: EmailStr = Field(..., description="Email адрес для обратной связи")
    message: str = Field(..., min_length=10, max_length=5000, description="Текст сообщения")
    agree_terms: bool = Field(default=False, description="Согласие с условиями использования")

    @validator("first_name")
    def validate_first_name(cls, v):
        """Проверка что имя не содержит цифры."""
        if any(char.isdigit() for char in v):
            raise ValueError("Имя не должно содержать цифры")
        return v.strip()

    @validator("phone_number")
    def validate_phone_number(cls, v):
        """Проверка формата телефона."""
        if not v.startswith("+"):
            raise ValueError("Номер должен начинаться с +")

        if not re.match(r"^\+\d{9,15}$", v):
            raise ValueError("Неверный формат телефона. Используйте +1234567890")

        return v

    @validator("agree_terms")
    def validate_terms_agreement(cls, v):
        """Проверка что пользователь согласился с условиями."""
        if not v:
            raise ValueError("Необходимо согласиться с условиями использования")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "Иван",
                "phone_number": "+79991234567",
                "email": "ivan@example.com",
                "message": "Интересуюсь вашими курсами по Python",
                "agree_terms": True,
            }
        }


class SubscriptionSchema(BaseModel):
    """
    Схема для подписки на email рассылку.

    Attributes:
        email: Email адрес для подписки

    Example:
        >>> subscription = SubscriptionSchema(email="user@example.com")
    """

    email: EmailStr = Field(..., description="Email адрес для подписки на новости")

    class Config:
        json_schema_extra = {"example": {"email": "user@example.com"}}


class ContactInfoSchema(BaseModel):
    """
    Схема с контактной информацией компании.

    Используется для API эндпоинта /api/core/contact-info/

    Attributes:
        email: Основной email для связи
        phone: Телефон поддержки
        address: Физический адрес офиса
        social_links: Ссылки на социальные сети
        working_hours: Часы работы поддержки
    """

    email: str
    phone: str
    address: str | None = None
    social_links: dict = Field(default_factory=dict)
    working_hours: str | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "email": "info@pyland.ru",
                "phone": "+7 (999) 123-45-67",
                "address": "Москва, ул. Примерная, д. 1",
                "social_links": {
                    "telegram": "https://t.me/pyland",
                    "youtube": "https://youtube.com/@pyland",
                },
                "working_hours": "Пн-Пт: 10:00-18:00 МСК",
            }
        }


class StatsSchema(BaseModel):
    """
    Схема для статистики платформы.

    Используется для отображения общей статистики на главной странице.

    Attributes:
        total_students: Общее количество студентов
        total_courses: Количество доступных курсов
        total_lessons: Общее количество уроков
        total_hours: Общая продолжительность контента (в часах)
        completion_rate: Средний процент завершения курсов
    """

    total_students: int = Field(default=0, description="Количество студентов")
    total_courses: int = Field(default=0, description="Количество курсов")
    total_lessons: int = Field(default=0, description="Количество уроков")
    total_hours: float = Field(default=0.0, description="Часов контента")
    completion_rate: float = Field(
        default=0.0, ge=0.0, le=100.0, description="Средний % завершения курсов"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "total_students": 0,  # Not displayed publicly
                "total_courses": 15,
                "total_lessons": 230,
                "total_hours": 145.5,
                "completion_rate": 0.0,  # Not displayed publicly
            }
        }


class FeedbackResponseSchema(BaseModel):
    """
    Схема ответа после успешной отправки обратной связи.

    Attributes:
        success: Флаг успешности операции
        message: Сообщение для пользователя
        feedback_id: ID созданной записи в БД (optional)
    """

    success: bool
    message: str
    feedback_id: int | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Спасибо! Мы получили ваше сообщение и свяжемся с вами в ближайшее время.",
                "feedback_id": 42,
            }
        }


class SubscriptionResponseSchema(BaseModel):
    """
    Схема ответа после подписки на рассылку.

    Attributes:
        success: Флаг успешности операции
        message: Сообщение для пользователя
        already_subscribed: Был ли пользователь уже подписан
    """

    success: bool
    message: str
    already_subscribed: bool = False

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Вы успешно подписаны на рассылку!",
                "already_subscribed": False,
            }
        }
