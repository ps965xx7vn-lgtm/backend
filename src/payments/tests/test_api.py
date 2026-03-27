"""
Тесты API endpoints payments.

Проверяет:
    - POST /api/payments/paddle/checkout
    - GET /api/payments/history
    - GET /api/payments/{id}
    - POST /api/payments/paddle/webhook
"""

from __future__ import annotations

from decimal import Decimal
from unittest.mock import Mock, patch

import pytest

from payments.models import Payment


@pytest.mark.django_db
class TestPaymentAPICheckout:
    """Тесты API endpoint checkout."""

    def test_checkout_success(self, api_client, user, course):
        """Тест успешного создания checkout через API."""
        # Пока пропускаем - API endpoint может не существовать
        pytest.skip("API endpoint not implemented yet")

        # Request
        response = api_client.post(
            "/api/payments/paddle/checkout",
            json={
                "course_slug": course.slug,
                "currency": "USD",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["transaction_id"] == "txn_api_test"
        assert data["client_token"] == "tok_api_test"

    def test_checkout_requires_auth(self, api_client, course):
        """Тест что checkout требует авторизации."""
        pytest.skip("API endpoint not implemented yet")

    def test_checkout_invalid_course(self, api_client, user):
        """Тест с несуществующим курсом."""
        pytest.skip("API endpoint not implemented yet")

    def test_checkout_invalid_currency(self, api_client, user, course):
        """Тест с невалидной валютой."""
        pytest.skip("API endpoint not implemented yet")


@pytest.mark.django_db
@pytest.mark.skip("API endpoints not implemented yet")
class TestPaymentAPIHistory:
    """Тесты API endpoint history."""

    def test_history_requires_auth(self, api_client):
        """Тест что history требует авторизации."""
        response = api_client.get("/api/payments/history")

        assert response.status_code == 401

    def test_history_empty(self, api_client, user):
        """Тест пустой истории платежей."""
        api_client.client.force_login(user)

        response = api_client.get("/api/payments/history")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_history_with_payments(self, api_client, user, course):
        """Тест истории с платежами."""
        # Создаём несколько платежей
        Payment.objects.create(
            user=user,
            course=course,
            amount=Decimal("99.00"),
            currency="USD",
            payment_method="paddle",
            status="completed",
        )

        Payment.objects.create(
            user=user,
            course=course,
            amount=Decimal("85.00"),
            currency="EUR",
            payment_method="paddle",
            status="completed",
        )

        api_client.client.force_login(user)

        response = api_client.get("/api/payments/history")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_history_only_user_payments(self, api_client, user, course):
        """Тест что history показывает только платежи текущего пользователя."""
        from authentication.models import Role

        # Создаём другого пользователя
        role, _ = Role.objects.get_or_create(name="student")
        other_user = user.__class__.objects.create_user(
            email="other@example.com",
            password="TestPass123!",
            role=role,
        )

        # Платёж текущего пользователя
        Payment.objects.create(
            user=user,
            course=course,
            amount=Decimal("99.00"),
            currency="USD",
            payment_method="paddle",
        )

        # Платёж другого пользователя
        Payment.objects.create(
            user=other_user,
            course=course,
            amount=Decimal("99.00"),
            currency="USD",
            payment_method="paddle",
        )

        api_client.client.force_login(user)

        response = api_client.get("/api/payments/history")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1  # Только свой платёж


@pytest.mark.django_db
@pytest.mark.skip("API endpoints not implemented yet")
class TestPaymentAPIDetail:
    """Тесты API endpoint detail."""

    def test_detail_requires_auth(self, api_client, user, course):
        """Тест что detail требует авторизации."""
        payment = Payment.objects.create(
            user=user,
            course=course,
            amount=Decimal("99.00"),
            currency="USD",
            payment_method="paddle",
        )

        response = api_client.get(f"/api/payments/{payment.id}")

        assert response.status_code == 401

    def test_detail_success(self, api_client, user, course):
        """Тест успешного получения деталей платежа."""
        payment = Payment.objects.create(
            user=user,
            course=course,
            amount=Decimal("99.00"),
            currency="USD",
            payment_method="paddle",
            status="completed",
        )

        api_client.client.force_login(user)

        response = api_client.get(f"/api/payments/{payment.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == payment.id
        assert data["status"] == "completed"

    def test_detail_other_user_payment(self, api_client, user, course):
        """Тест что нельзя получить чужой платёж."""
        from authentication.models import Role

        # Другой пользователь
        role, _ = Role.objects.get_or_create(name="student")
        other_user = user.__class__.objects.create_user(
            email="other@example.com",
            password="TestPass123!",
            role=role,
        )

        # Платёж другого пользователя
        payment = Payment.objects.create(
            user=other_user,
            course=course,
            amount=Decimal("99.00"),
            currency="USD",
            payment_method="paddle",
        )

        api_client.client.force_login(user)

        response = api_client.get(f"/api/payments/{payment.id}")

        assert response.status_code == 404

    def test_detail_nonexistent_payment(self, api_client, user):
        """Тест с несуществующим платежом."""
        api_client.client.force_login(user)

        response = api_client.get("/api/payments/999999")

        assert response.status_code == 404


@pytest.mark.skip("Webhook endpoint not implemented yet")
@pytest.mark.django_db
class TestWebhookAPI:
    """Тесты webhook endpoint."""

    @patch("payments.api.paddle_service")
    def test_webhook_valid(self, mock_paddle_service, api_client, user, course):
        """Тест обработки валидного webhook."""
        # Создаём платёж
        Payment.objects.create(
            user=user,
            course=course,
            amount=Decimal("99.00"),
            currency="USD",
            payment_method="paddle",
            status="processing",
            transaction_id="txn_webhook_test",
        )

        # Mock webhook verification
        mock_paddle_service.verify_webhook.return_value = {
            "event_type": "transaction.completed",
            "data": {
                "id": "txn_webhook_test",
                "status": "completed",
            },
        }

        # Webhook request
        webhook_body = '{"event_type":"transaction.completed","data":{"id":"txn_webhook_test"}}'
        response = api_client.post(
            "/api/payments/paddle/webhook",
            data=webhook_body,
            content_type="application/json",
            headers={"Paddle-Signature": "valid_signature"},
        )

        assert response.status_code == 200

    @patch("payments.api.paddle_service")
    def test_webhook_invalid_signature(self, mock_paddle_service, api_client):
        """Тест с невалидной сигнатурой."""
        mock_paddle_service.verify_webhook.return_value = None

        webhook_body = '{"event_type":"transaction.completed"}'
        response = api_client.post(
            "/api/payments/paddle/webhook",
            data=webhook_body,
            content_type="application/json",
            headers={"Paddle-Signature": "invalid_signature"},
        )

        assert response.status_code == 400
