"""
Payments Schemas Module - Pydantic схемы для API платежей через Paddle Billing.

Содержит схемы для входных и выходных данных API:
- Создание Paddle checkout сессий
- Статус платежей
- История платежей
- Webhook события от Paddle

Автор: Pyland Team
Дата: 2026
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PaymentStatus(str, Enum):
    """Статусы платежа"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentMethod(str, Enum):
    """Методы оплаты"""

    PADDLE = "paddle"


class CurrencyCode(str, Enum):
    """Поддерживаемые валюты"""

    USD = "USD"
    EUR = "EUR"
    RUB = "RUB"
    GEL = "GEL"


class PaddleCheckoutInput(BaseModel):
    """
    Схема для создания Paddle checkout сессии.
    """

    course_id: UUID = Field(..., description="ID курса (UUID)")
    success_url: str | None = Field(None, description="URL для успешной оплаты")
    cancel_url: str | None = Field(None, description="URL при отмене")


# === OUTPUT SCHEMAS (ответы API) ===


class PaymentOutput(BaseModel):
    """
    Схема вывода данных о платеже.
    """

    id: UUID
    user_email: EmailStr
    course_id: UUID
    course_name: str
    amount: Decimal
    currency: str
    status: PaymentStatus
    payment_method: PaymentMethod
    transaction_id: str | None = None
    payment_url: str | None = None
    payment_date: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaymentCheckoutOutput(BaseModel):
    """
    Схема ответа при создании checkout сессии.

    Возвращает URL для перенаправления пользователя на страницу оплаты.
    """

    payment_id: UUID
    checkout_url: str
    transaction_id: str
    status: str
    amount: str
    currency: str


class PaymentStatusOutput(BaseModel):
    """
    Схема статуса платежа (минимальная информация).
    """

    id: UUID
    status: PaymentStatus
    transaction_id: str | None
    payment_date: datetime | None

    model_config = ConfigDict(from_attributes=True)


class PaymentHistoryOutput(BaseModel):
    """
    Схема для списка платежей пользователя.
    """

    payments: list[PaymentOutput]
    total_count: int
    page: int
    page_size: int


# === WEBHOOK SCHEMAS ===


class PaddleWebhookInput(BaseModel):
    """
    Схема для обработки Paddle webhook событий.
    """

    event_type: str
    event_id: str
    occurred_at: str
    data: dict[str, Any]


class WebhookResponseOutput(BaseModel):
    """
    Схема ответа на webhook.
    """

    success: bool
    message: str
    event_type: str | None = None


# === ERROR SCHEMAS ===


class PaymentErrorOutput(BaseModel):
    """
    Схема ошибки при работе с платежами.
    """

    error: str
    details: str | None = None
    payment_id: UUID | None = None


__all__ = [
    "PaymentStatus",
    "PaymentMethod",
    "CurrencyCode",
    "PaddleCheckoutInput",
    "PaymentOutput",
    "PaymentCheckoutOutput",
    "PaymentStatusOutput",
    "PaymentHistoryOutput",
    "PaddleWebhookInput",
    "WebhookResponseOutput",
    "PaymentErrorOutput",
]
