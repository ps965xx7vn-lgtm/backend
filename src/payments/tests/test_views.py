"""
Тесты представлений payments.

Проверяет:
    - checkout_view GET/POST
    - payment_success_view
    - payment_cancel_view
    - Требование авторизации
    - Редиректы
"""

from __future__ import annotations

from decimal import Decimal
from unittest.mock import Mock, patch

import pytest
from django.test import override_settings
from django.urls import reverse

from payments.models import Payment


@pytest.mark.django_db
class TestCheckoutView:
    """Тесты представления checkout."""

    def test_checkout_get_requires_login(self, client, course):
        """Тест что GET требует авторизации."""
        url = reverse("payments:checkout", args=[course.slug])

        response = client.get(url)

        assert response.status_code == 302
        assert "signin" in response.url or "login" in response.url

    def test_checkout_get_authenticated(self, client_logged_in, course):
        """Тест GET запроса авторизованным пользователем."""
        url = reverse("payments:checkout", args=[course.slug])

        response = client_logged_in.get(url)

        assert response.status_code == 200
        assert "checkout" in response.templates[0].name.lower()
        assert "course" in response.context

    def test_checkout_get_nonexistent_course(self, client_logged_in):
        """Тест GET с несуществующим курсом."""
        url = reverse("payments:checkout", args=["nonexistent-course"])

        response = client_logged_in.get(url)

        assert response.status_code == 404

    @override_settings(
        STORAGES={
            "staticfiles": {
                "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
            }
        }
    )
    @patch("payments.views.get_paddle_service")
    def test_checkout_post_success(self, mock_get_paddle_service, client_logged_in, user, course):
        """Тест успешного POST запроса."""
        # Mock Paddle service
        mock_service = mock_get_paddle_service.return_value
        mock_service.create_transaction.return_value = {
            "transaction_id": "txn_test123",
            "status": "ready",
            "checkout_url": None,
            "client_token": "tok_test123",
            "customer_id": "cust_test",
            "amount": "99.00",
            "currency": "USD",
            "product_id": "prod_test",
            "price_id": "price_test",
        }

        url = reverse("payments:checkout", args=[course.slug])

        form_data = {
            "payment_method": "paddle",
            "currency": "USD",
            "accept_all": "on",
        }

        response = client_logged_in.post(url, data=form_data)

        # Проверяем создание платежа
        payment = Payment.objects.filter(user=user, course=course).first()
        assert payment is not None
        assert payment.status == "processing"

        # Проверяем редирект или показ страницы checkout
        assert response.status_code in [200, 302]

    def test_checkout_post_invalid_form(self, client_logged_in, course):
        """Тест POST с невалидной формой."""
        url = reverse("payments:checkout", args=[course.slug])

        form_data = {
            "payment_method": "paddle",
            "currency": "USD",
            # Не принимаем условия
            "accept_all": False,
        }

        response = client_logged_in.post(url, data=form_data)

        assert response.status_code == 200
        assert "form" in response.context
        assert response.context["form"].errors

    def test_checkout_post_requires_login(self, client, course):
        """Тест что POST требует авторизации."""
        url = reverse("payments:checkout", args=[course.slug])

        form_data = {
            "payment_method": "paddle",
            "currency": "USD",
            "accept_all": "on",
        }

        response = client.post(url, data=form_data)

        assert response.status_code == 302
        assert "signin" in response.url or "login" in response.url


@pytest.mark.django_db
class TestPaymentSuccessView:
    """Тесты представления success."""

    def test_payment_success_requires_login(self, client, user, course):
        """Тест что success требует авторизации."""
        # Create payment first
        payment = Payment.objects.create(
            user=user,
            course=course,
            amount=Decimal("99.00"),
            currency="USD",
            payment_method="paddle",
            status="completed",
        )
        url = reverse("payments:payment_success", args=[payment.id])

        response = client.get(url)

        assert response.status_code == 302
        assert "signin" in response.url or "login" in response.url

    def test_payment_success_authenticated(self, client_logged_in, user, course):
        """Тест GET success авторизованным пользователем."""
        # Create payment
        payment = Payment.objects.create(
            user=user,
            course=course,
            amount=Decimal("99.00"),
            currency="USD",
            payment_method="paddle",
            status="completed",
        )
        url = reverse("payments:payment_success", args=[payment.id])

        response = client_logged_in.get(url)

        assert response.status_code == 200

    def test_payment_success_with_transaction_id(self, client_logged_in, user, course):
        """Тест success с transaction_id в GET параметрах."""
        # Создаём платёж
        payment = Payment.objects.create(
            user=user,
            course=course,
            amount=Decimal("99.00"),
            currency="USD",
            payment_method="paddle",
            status="completed",
            transaction_id="txn_test123",
        )

        url = reverse("payments:payment_success", args=[payment.id])
        response = client_logged_in.get(url, {"_ptxn": payment.transaction_id})

        assert response.status_code == 200


@pytest.mark.django_db
class TestPaymentCancelView:
    """Тесты представления cancel."""

    def test_payment_cancel_requires_login(self, client, user, course):
        """Тест что cancel требует авторизации."""
        # Create payment
        payment = Payment.objects.create(
            user=user,
            course=course,
            amount=Decimal("99.00"),
            currency="USD",
            payment_method="paddle",
            status="pending",
        )
        url = reverse("payments:payment_cancel", args=[payment.id])

        response = client.get(url)

        assert response.status_code == 302
        assert "signin" in response.url or "login" in response.url

    def test_payment_cancel_authenticated(self, client_logged_in, user, course):
        """Тест GET cancel авторизованным пользователем."""
        # Create payment
        payment = Payment.objects.create(
            user=user,
            course=course,
            amount=Decimal("99.00"),
            currency="USD",
            payment_method="paddle",
            status="pending",
        )
        url = reverse("payments:payment_cancel", args=[payment.id])

        response = client_logged_in.get(url)

        assert response.status_code == 200

    def test_payment_cancel_updates_status(self, client_logged_in, user, course):
        """Тест что cancel обновляет статус платежа."""
        # Создаём платёж
        payment = Payment.objects.create(
            user=user,
            course=course,
            amount=Decimal("99.00"),
            currency="USD",
            payment_method="paddle",
            status="processing",
            transaction_id="txn_test123",
        )

        url = reverse("payments:payment_cancel", args=[payment.id])
        response = client_logged_in.get(url)

        assert response.status_code == 200

        # Check payment status was updated
        payment.refresh_from_db()
        assert payment.status == "cancelled"


@pytest.mark.django_db
class TestPaddleRetainHandler:
    """Тесты обработчика Paddle Retain (_ptxn)."""

    def test_retain_handler_with_ptxn(self, client_logged_in, user, course):
        """Тест обработки _ptxn параметра."""
        # Создаём платёж с transaction_id
        payment = Payment.objects.create(
            user=user,
            course=course,
            amount=Decimal("99.00"),
            currency="USD",
            payment_method="paddle",
            status="completed",
            transaction_id="txn_test123",
        )

        url = reverse("payments:payment_success", args=[payment.id])
        response = client_logged_in.get(url, {"_ptxn": payment.transaction_id})

        assert response.status_code == 200

    def test_retain_handler_without_ptxn(self, client_logged_in, user, course):
        """Тест без _ptxn параметра."""
        # Create payment
        payment = Payment.objects.create(
            user=user,
            course=course,
            amount=Decimal("99.00"),
            currency="USD",
            payment_method="paddle",
            status="completed",
        )
        url = reverse("payments:payment_success", args=[payment.id])
        response = client_logged_in.get(url)

        assert response.status_code == 200


@pytest.mark.django_db
class TestPaymentFlow:
    """Интеграционные тесты процесса оплаты."""

    @patch("payments.views.get_paddle_service")
    def test_full_checkout_flow(self, mock_get_paddle_service, client_logged_in, user, course):
        """Тест полного процесса checkout → success."""
        # Mock Paddle service
        mock_service = mock_get_paddle_service.return_value
        mock_service.create_transaction.return_value = {
            "transaction_id": "txn_flow_test",
            "status": "ready",
            "checkout_url": None,
            "client_token": "tok_flow_test",
            "customer_id": "cust_flow",
            "amount": "99.00",
            "currency": "USD",
            "product_id": "prod_flow",
            "price_id": "price_flow",
        }

        # Шаг 1: GET checkout
        checkout_url = reverse("payments:checkout", args=[course.slug])
        response = client_logged_in.get(checkout_url)
        assert response.status_code == 200

        # Шаг 2: POST checkout
        form_data = {
            "payment_method": "paddle",
            "currency": "USD",
            "accept_all": "on",
        }

        response = client_logged_in.post(checkout_url, data=form_data)
        assert response.status_code in [200, 302]

        # Проверяем что платёж создан
        payment = Payment.objects.filter(user=user, course=course).first()
        assert payment is not None

        # Шаг 3: Success page (имитация возврата от Paddle)
        payment.status = "completed"
        payment.save()

        success_url = reverse("payments:payment_success", args=[payment.id])
        response = client_logged_in.get(success_url, {"_ptxn": payment.transaction_id})
        assert response.status_code == 200
