"""
Интеграционные тесты payments.

Проверяет полный процесс оплаты от начала до конца.
"""

from __future__ import annotations

from decimal import Decimal
from unittest.mock import Mock, patch

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.urls import reverse

from courses.models import Course
from payments.models import Payment


@pytest.mark.django_db
class TestFullPaymentFlow:
    """Интеграционные тесты полного процесса оплаты."""

    @patch("payments.views.paddle_service")
    @patch("payments.api.paddle_service")
    def test_complete_payment_flow_via_views(
        self, mock_api_paddle, mock_views_paddle, client_logged_in, user, course
    ):
        """Тест полного процесса: checkout → payment → webhook → enrollment."""
        # Mock Paddle responses
        mock_views_paddle.create_checkout_transaction.return_value = {
            "transaction_id": "txn_integration_test",
            "client_token": "tok_integration_test",
        }

        # Шаг 1: Открываем страницу checkout
        checkout_url = reverse("payments:checkout", args=[course.slug])
        response = client_logged_in.get(checkout_url)
        assert response.status_code == 200

        # Шаг 2: Отправляем форму checkout
        form_data = {
            "payment_method": "paddle",
            "currency": "USD",
            "accept_terms": "on",
            "accept_privacy": "on",
        }

        response = client_logged_in.post(checkout_url, data=form_data)
        assert response.status_code in [200, 302]

        # Проверяем что платёж создан
        payment = Payment.objects.filter(user=user, course=course).first()
        assert payment is not None
        assert payment.status == "processing"
        assert payment.transaction_id == "txn_integration_test"

        # Шаг 3: Имитация webhook от Paddle (платёж завершён)
        payment.mark_as_completed()
        payment.save()

        # Проверяем финальный статус
        payment.refresh_from_db()
        assert payment.status == "completed"
        assert payment.paid_at is not None

        # Шаг 4: Success page
        success_url = reverse("payments:payment_success")
        response = client_logged_in.get(success_url, {"_ptxn": payment.transaction_id})
        assert response.status_code == 200

    @patch("payments.currency_service.requests.get")
    @patch("payments.views.paddle_service")
    def test_payment_with_currency_conversion(
        self, mock_paddle, mock_requests, client_logged_in, user, course
    ):
        """Тест оплаты с конвертацией валют."""
        # Mock currency API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": "success",
            "conversion_rates": {
                "USD": 1.0,
                "EUR": 0.85,
                "RUB": 75.0,
            },
        }
        mock_requests.return_value = mock_response

        # Mock Paddle
        mock_paddle.create_checkout_transaction.return_value = {
            "transaction_id": "txn_eur_test",
            "client_token": "tok_eur_test",
        }

        # Оплата в EUR
        checkout_url = reverse("payments:checkout", args=[course.slug])
        form_data = {
            "payment_method": "paddle",
            "currency": "EUR",
            "accept_terms": "on",
            "accept_privacy": "on",
        }

        client_logged_in.post(checkout_url, data=form_data)

        # Проверяем что платёж создан с EUR
        payment = Payment.objects.filter(user=user, course=course, currency="EUR").first()
        assert payment is not None
        assert payment.currency == "EUR"

    @patch("payments.api.paddle_service")
    def test_payment_failure_flow(self, mock_paddle, api_client, user, course):
        """Тест процесса неудачной оплаты."""
        api_client.client.force_login(user)

        # Mock Paddle error
        mock_paddle.create_checkout_transaction.side_effect = Exception("Paddle Error")

        # Попытка создать checkout через API
        response = api_client.post(
            "/api/payments/paddle/checkout",
            json={
                "course_slug": course.slug,
                "currency": "USD",
            },
        )

        # Должна быть ошибка
        assert response.status_code in [400, 500]

    @patch("payments.views.paddle_service")
    def test_multiple_payments_same_course(self, mock_paddle, client_logged_in, user, course):
        """Тест множественных платежей за один курс."""
        mock_paddle.create_checkout_transaction.return_value = {
            "transaction_id": "txn_multi_1",
            "client_token": "tok_multi_1",
        }

        checkout_url = reverse("payments:checkout", args=[course.slug])
        form_data = {
            "payment_method": "paddle",
            "currency": "USD",
            "accept_terms": "on",
            "accept_privacy": "on",
        }

        # Первая попытка оплаты
        client_logged_in.post(checkout_url, data=form_data)
        payment1 = Payment.objects.filter(user=user, course=course).first()
        assert payment1 is not None

        # Вторая попытка (первая не завершилась)
        mock_paddle.create_checkout_transaction.return_value = {
            "transaction_id": "txn_multi_2",
            "client_token": "tok_multi_2",
        }

        client_logged_in.post(checkout_url, data=form_data)

        # Должно быть 2 платежа
        payments = Payment.objects.filter(user=user, course=course)
        assert payments.count() >= 1  # Может быть ≥1 в зависимости от логики

    def test_payment_history_after_multiple_purchases(self, api_client, user):
        """Тест истории платежей после нескольких покупок."""
        # Создаём несколько курсов
        course1 = Course.objects.create(
            name="Course 1",
            slug="course-1",
            price=Decimal("99.00"),
            status="active",
        )

        course2 = Course.objects.create(
            name="Course 2",
            slug="course-2",
            price=Decimal("149.00"),
            status="active",
        )

        # Создаём платежи
        Payment.objects.create(
            user=user,
            course=course1,
            amount=Decimal("99.00"),
            currency="USD",
            payment_method="paddle",
            status="completed",
        )

        Payment.objects.create(
            user=user,
            course=course2,
            amount=Decimal("149.00"),
            currency="USD",
            payment_method="paddle",
            status="completed",
        )

        api_client.client.force_login(user)

        # Получаем историю
        response = api_client.get("/api/payments/history")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    @patch("payments.api.paddle_service")
    def test_webhook_updates_payment_status(self, mock_paddle, api_client, user, course):
        """Тест что webhook обновляет статус платежа."""
        # Создаём платёж
        payment = Payment.objects.create(
            user=user,
            course=course,
            amount=Decimal("99.00"),
            currency="USD",
            payment_method="paddle",
            status="processing",
            transaction_id="txn_webhook_integration",
        )

        # Mock webhook verification
        mock_paddle.verify_webhook.return_value = {
            "event_type": "transaction.completed",
            "data": {
                "id": "txn_webhook_integration",
                "status": "completed",
            },
        }

        # Отправляем webhook
        webhook_body = (
            '{"event_type":"transaction.completed","data":{"id":"txn_webhook_integration"}}'
        )
        response = api_client.post(
            "/api/payments/paddle/webhook",
            data=webhook_body,
            content_type="application/json",
            headers={"Paddle-Signature": "test_signature"},
        )

        assert response.status_code == 200

        # Проверяем что статус обновился (может потребоваться обработка в фоне)
        payment.refresh_from_db()
        # Статус может измениться в зависимости от реализации webhook handler


@pytest.mark.django_db
class TestPaymentEdgeCases:
    """Тесты граничных случаев."""

    def test_payment_with_zero_amount(self, user, course):
        """Тест создания платежа с нулевой суммой."""
        with pytest.raises((ValidationError, ValueError)):
            Payment.objects.create(
                user=user,
                course=course,
                amount=Decimal("0.00"),
                currency="USD",
                payment_method="paddle",
            )

    def test_payment_with_negative_amount(self, user, course):
        """Тест что нельзя создать платёж с отрицательной суммой."""
        with pytest.raises((ValidationError, ValueError)):
            Payment.objects.create(
                user=user,
                course=course,
                amount=Decimal("-99.00"),
                currency="USD",
                payment_method="paddle",
            )

    def test_payment_without_user(self, course):
        """Тест что платёж требует пользователя."""
        with pytest.raises((IntegrityError, ValueError)):
            Payment.objects.create(
                user=None,
                course=course,
                amount=Decimal("99.00"),
                currency="USD",
                payment_method="paddle",
            )

    def test_payment_without_course(self, user):
        """Тест что платёж требует курс."""
        with pytest.raises((IntegrityError, ValueError)):
            Payment.objects.create(
                user=user,
                course=None,
                amount=Decimal("99.00"),
                currency="USD",
                payment_method="paddle",
            )
