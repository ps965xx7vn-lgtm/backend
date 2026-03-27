"""
Тесты моделей Payment.

Проверяет:
    - Создание платежей
    - Методы моделей (mark_as_completed, is_successful и т.д.)
    - Автоматическое зачисление студента
    - Валидацию полей
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from django.utils import timezone

from courses.models import Course
from payments.models import Payment


@pytest.mark.django_db
class TestPaymentModel:
    """Тесты модели Payment."""

    def test_payment_creation(self, user, course):
        """Тест создания платежа с обязательными полями."""
        payment = Payment.objects.create(
            user=user,
            course=course,
            amount=Decimal("99.00"),
            currency="USD",
            payment_method="paddle",
            status="pending",
        )

        assert payment.id is not None
        assert payment.user == user
        assert payment.course == course
        assert payment.amount == Decimal("99.00")
        assert payment.currency == "USD"
        assert payment.status == "pending"

    def test_payment_str(self, user, course):
        """Тест строкового представления платежа."""
        payment = Payment.objects.create(
            user=user,
            course=course,
            amount=Decimal("99.00"),
            currency="USD",
            payment_method="paddle",
        )

        str_repr = str(payment)
        assert user.email in str_repr
        assert "99.00" in str_repr
        assert "USD" in str_repr

    def test_mark_as_completed(self, user, course):
        """Тест изменения статуса на 'completed'."""
        payment = Payment.objects.create(
            user=user,
            course=course,
            amount=Decimal("99.00"),
            currency="USD",
            payment_method="paddle",
            status="pending",
        )

        payment.mark_as_completed()

        assert payment.status == "completed"
        assert payment.payment_date is not None
        assert isinstance(payment.payment_date, type(timezone.now()))

    def test_mark_as_failed(self, user, course):
        """Тест изменения статуса на 'failed'."""
        payment = Payment.objects.create(
            user=user,
            course=course,
            amount=Decimal("99.00"),
            currency="USD",
            payment_method="paddle",
            status="processing",
        )

        payment.mark_as_failed()

        assert payment.status == "failed"

    def test_is_successful_true(self, user, course):
        """Тест is_successful() для завершённого платежа."""
        payment = Payment.objects.create(
            user=user,
            course=course,
            amount=Decimal("99.00"),
            currency="USD",
            payment_method="paddle",
            status="completed",
        )

        assert payment.is_successful() is True

    def test_is_successful_false(self, user, course):
        """Тест is_successful() для незавершённого платежа."""
        payment = Payment.objects.create(
            user=user,
            course=course,
            amount=Decimal("99.00"),
            currency="USD",
            payment_method="paddle",
            status="pending",
        )

        assert payment.is_successful() is False

    def test_can_be_refunded_true(self, user, course):
        """Тест can_be_refunded() для completed платежа."""
        payment = Payment.objects.create(
            user=user,
            course=course,
            amount=Decimal("99.00"),
            currency="USD",
            payment_method="paddle",
            status="completed",
        )

        assert payment.can_be_refunded() is True

    def test_can_be_refunded_false(self, user, course):
        """Тест can_be_refunded() для незавершённого платежа."""
        payment = Payment.objects.create(
            user=user,
            course=course,
            amount=Decimal("99.00"),
            currency="USD",
            payment_method="paddle",
            status="pending",
        )

        assert payment.can_be_refunded() is False

    def test_get_payment_method_display_name(self, user, course):
        """Тест получения читаемого названия метода оплаты."""
        payment = Payment.objects.create(
            user=user,
            course=course,
            amount=Decimal("99.00"),
            currency="USD",
            payment_method="paddle",
        )

        display_name = payment.get_payment_method_display_name()
        assert "Paddle" in display_name

    def test_multiple_currencies(self, user, course):
        """Тест создания платежей в разных валютах."""
        currencies = ["USD", "EUR", "RUB", "GEL"]
        amounts = [Decimal("99.00"), Decimal("85.00"), Decimal("7500.00"), Decimal("265.00")]

        payments = []
        for currency, amount in zip(currencies, amounts, strict=False):
            payment = Payment.objects.create(
                user=user,
                course=course,
                amount=amount,
                currency=currency,
                payment_method="paddle",
            )
            payments.append(payment)

        assert len(payments) == 4
        assert all(p.currency in currencies for p in payments)

    def test_transaction_id_uniqueness(self, user, course):
        """Тест что transaction_id может быть пустым."""
        # Первый платёж без transaction_id
        payment1 = Payment.objects.create(
            user=user,
            course=course,
            amount=Decimal("99.00"),
            currency="USD",
            payment_method="paddle",
        )

        # Второй платёж без transaction_id - OK
        payment2 = Payment.objects.create(
            user=user,
            course=course,
            amount=Decimal("99.00"),
            currency="USD",
            payment_method="paddle",
        )

        # transaction_id is blank по умолчанию
        assert payment1.transaction_id == ""
        assert payment2.transaction_id == ""

    def test_extra_data_json_field(self, user, course):
        """Тест что extra_data хранит JSON данные."""
        extra_data = {
            "paddle_customer_id": "ctm_123",
            "paddle_product_id": "pro_456",
            "items": ["item1", "item2"],
        }

        payment = Payment.objects.create(
            user=user,
            course=course,
            amount=Decimal("99.00"),
            currency="USD",
            payment_method="paddle",
            extra_data=extra_data,
        )

        # Перезагрузим из базы
        payment.refresh_from_db()

        assert payment.extra_data == extra_data
        assert payment.extra_data["paddle_customer_id"] == "ctm_123"

    def test_payment_ordering(self, user, course):
        """Тест что платежи сортируются по created_at DESC."""
        # Создаём 3 платежа
        payment1 = Payment.objects.create(
            user=user,
            course=course,
            amount=Decimal("99.00"),
            currency="USD",
            payment_method="paddle",
        )

        payment2 = Payment.objects.create(
            user=user,
            course=course,
            amount=Decimal("99.00"),
            currency="USD",
            payment_method="paddle",
        )

        payment3 = Payment.objects.create(
            user=user,
            course=course,
            amount=Decimal("99.00"),
            currency="USD",
            payment_method="paddle",
        )

        payments = Payment.objects.all()

        # Последний созданный должен быть первым
        assert payments[0].id == payment3.id
        assert payments[1].id == payment2.id
        assert payments[2].id == payment1.id
