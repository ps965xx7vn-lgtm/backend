"""
Тесты Django Admin для payments.

Проверяет:
    - Отображение платежей в админке
    - Фильтры и поиск
    - Кастомные действия (actions)
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory

from payments.admin import PaymentAdmin
from payments.models import Payment


@pytest.mark.django_db
class TestPaymentAdmin:
    """Тесты PaymentAdmin."""

    def setup_method(self):
        """Настройка перед каждым тестом."""
        self.site = AdminSite()
        self.payment_admin = PaymentAdmin(Payment, self.site)
        self.factory = RequestFactory()

    def test_list_display_fields(self):
        """Тест что все нужные поля в list_display."""
        expected_fields = [
            "id",
            "user_link",
            "course_link",
            "formatted_amount",
            "payment_method_display",
            "colored_status",
            "created_at",
        ]

        for field in expected_fields:
            assert (
                field in self.payment_admin.list_display
            ), f"Field {field} should be in list_display"

    def test_list_filter_fields(self):
        """Тест что все нужные поля в list_filter."""
        expected_filters = ["status", "payment_method", "currency", "created_at"]

        for filter_field in expected_filters:
            assert (
                filter_field in self.payment_admin.list_filter
            ), f"Filter {filter_field} should be in list_filter"

    def test_search_fields(self):
        """Тест полей поиска."""
        expected_search = [
            "user__email",
            "user__first_name",
            "user__last_name",
            "transaction_id",
        ]

        for field in expected_search:
            assert field in self.payment_admin.search_fields

    def test_readonly_fields(self):
        """Тест что критичные поля read-only."""
        readonly = [
            "id",
            "created_at",
            "updated_at",
            "transaction_id",
        ]

        for field in readonly:
            assert field in self.payment_admin.readonly_fields

    def test_colored_status_display(self, user, course):
        """Тест отображения цветного статуса."""
        payment = Payment.objects.create(
            user=user,
            course=course,
            amount=Decimal("99.00"),
            currency="USD",
            payment_method="paddle",
            status="completed",
        )

        result = self.payment_admin.colored_status(payment)

        assert isinstance(result, str)
        assert "green" in result.lower() or "#10b981" in result
        assert "завершён" in result.lower() or "completed" in result.lower()

    def test_user_link_display(self, user, course):
        """Тест отображения ссылки на пользователя."""
        payment = Payment.objects.create(
            user=user,
            course=course,
            amount=Decimal("99.00"),
            currency="USD",
            payment_method="paddle",
        )

        result = self.payment_admin.user_link(payment)

        assert isinstance(result, str)
        assert user.email in result
        assert "href" in result

    def test_course_link_display(self, user, course):
        """Тест отображения ссылки на курс."""
        payment = Payment.objects.create(
            user=user,
            course=course,
            amount=Decimal("99.00"),
            currency="USD",
            payment_method="paddle",
        )

        result = self.payment_admin.course_link(payment)

        assert isinstance(result, str)
        assert course.name in result
        assert "href" in result

    def test_formatted_amount_display(self, user, course):
        """Тест форматирования суммы."""
        payment = Payment.objects.create(
            user=user,
            course=course,
            amount=Decimal("99.50"),
            currency="USD",
            payment_method="paddle",
        )

        result = self.payment_admin.formatted_amount(payment)

        assert isinstance(result, str)
        assert "$" in result or "99.50" in result

    def test_payment_method_display(self, user, course):
        """Тест отображения метода оплаты."""
        payment = Payment.objects.create(
            user=user,
            course=course,
            amount=Decimal("99.00"),
            currency="USD",
            payment_method="paddle",
        )

        result = self.payment_admin.payment_method_display(payment)

        assert isinstance(result, str)
        assert "paddle" in result.lower()

    def test_ordering(self):
        """Тест что платежи сортируются по дате создания."""
        assert "-created_at" in self.payment_admin.ordering
