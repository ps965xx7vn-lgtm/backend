"""
Factory Boy фабрики для тестовых объектов payments.

Используются для быстрого создания тестовых данных платежей.
"""

from __future__ import annotations

from decimal import Decimal

import factory
from django.contrib.auth import get_user_model
from django.utils import timezone
from factory.django import DjangoModelFactory

from payments.models import Payment

User = get_user_model()


class PaymentFactory(DjangoModelFactory):
    """Фабрика для создания платежей."""

    class Meta:
        model = Payment

    user = factory.SubFactory("authentication.tests.factories.UserFactory")
    course = factory.SubFactory("courses.tests.factories.CourseFactory")
    amount = Decimal("99.00")
    currency = "USD"
    payment_method = "paddle"
    status = "pending"
    transaction_id = factory.Sequence(lambda n: f"txn_test{n:06d}")
    payment_url = factory.LazyAttribute(
        lambda obj: f"https://paddle.com/checkout/{obj.transaction_id}"
    )
    extra_data = factory.LazyFunction(dict)
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)


class CompletedPaymentFactory(PaymentFactory):
    """Фабрика для завершённых платежей."""

    status = "completed"


class FailedPaymentFactory(PaymentFactory):
    """Фабрика для неудачных платежей."""

    status = "failed"


class ProcessingPaymentFactory(PaymentFactory):
    """Фабрика для обрабатываемых платежей."""

    status = "processing"


class CancelledPaymentFactory(PaymentFactory):
    """Фабрика для отменённых платежей."""

    status = "cancelled"


class RefundedPaymentFactory(PaymentFactory):
    """Фабрика для возвращённых платежей."""

    status = "refunded"
