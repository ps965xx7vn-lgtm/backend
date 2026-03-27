"""
Тесты PaddleService.

Проверяет:
    - Создание transactions
    - Создание customers
    - Создание products и prices
    - Обработку webhook событий
"""

from __future__ import annotations

from decimal import Decimal
from unittest.mock import Mock, patch

import pytest

from payments.paddle_service import PaddleService


@pytest.mark.django_db
class TestPaddleService:
    """Тесты сервиса Paddle."""

    def test_singleton_pattern(self):
        """Тест что PaddleService - это singleton."""
        service1 = PaddleService()
        service2 = PaddleService()

        assert service1 is service2

    def test_initialization(self):
        """Тест инициализации сервиса."""
        service = PaddleService()

        assert service.client is not None
        assert service.environment is not None

    @patch("payments.paddle_service.Client")
    def test_create_transaction_success(self, mock_client_class, user, course):
        """Тест успешного создания транзакции."""
        # Setup mock
        mock_client = Mock()
        mock_transaction = Mock()
        mock_transaction.id = "txn_123"
        mock_transaction.checkout.url = "https://checkout.paddle.com/test"

        mock_client.transactions.create.return_value = mock_transaction
        mock_client_class.return_value = mock_client

        service = PaddleService()
        service.client = mock_client

        # Test
        result = service.create_transaction(
            customer_id="ctm_123",
            price_id="pri_123",
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel",
        )

        assert result["transaction_id"] == "txn_123"
        assert "checkout_url" in result

    @patch("payments.paddle_service.Client")
    def test_get_or_create_customer_new(self, mock_client_class):
        """Тест создания нового customer."""
        mock_client = Mock()
        mock_customer = Mock()
        mock_customer.id = "ctm_new123"

        mock_client.customers.list.return_value = Mock(data=[])
        mock_client.customers.create.return_value = mock_customer
        mock_client_class.return_value = mock_client

        service = PaddleService()
        service.client = mock_client

        customer_id = service._get_or_create_customer("new@example.com")

        assert customer_id == "ctm_new123"
        mock_client.customers.create.assert_called_once()

    @patch("payments.paddle_service.Client")
    def test_get_or_create_customer_existing(self, mock_client_class):
        """Тест получения существующего customer."""
        mock_client = Mock()
        mock_existing = Mock()
        mock_existing.id = "ctm_existing123"
        mock_existing.email = "existing@example.com"

        mock_client.customers.list.return_value = Mock(data=[mock_existing])
        mock_client_class.return_value = mock_client

        service = PaddleService()
        service.client = mock_client

        customer_id = service._get_or_create_customer("existing@example.com")

        assert customer_id == "ctm_existing123"
        mock_client.customers.create.assert_not_called()

    @patch("payments.paddle_service.Client")
    def test_get_or_create_product_new(self, mock_client_class, course):
        """Тест создания нового product."""
        mock_client = Mock()
        mock_product = Mock()
        mock_product.id = "pro_new123"

        mock_client.products.list.return_value = Mock(data=[])
        mock_client.products.create.return_value = mock_product
        mock_client_class.return_value = mock_client

        service = PaddleService()
        service.client = mock_client

        product_id = service._get_or_create_product(course.id, course.name)

        assert product_id == "pro_new123"
        mock_client.products.create.assert_called_once()

    @patch("payments.paddle_service.Client")
    def test_get_or_create_product_existing(self, mock_client_class, course):
        """Тест получения существующего product."""
        mock_client = Mock()
        mock_existing = Mock()
        mock_existing.id = "pro_existing123"
        mock_existing.name = course.name
        mock_existing.custom_data = {"course_id": str(course.id)}

        mock_client.products.list.return_value = Mock(data=[mock_existing])
        mock_client_class.return_value = mock_client

        service = PaddleService()
        service.client = mock_client

        product_id = service._get_or_create_product(course.id, course.name)

        assert product_id == "pro_existing123"
        mock_client.products.create.assert_not_called()

    @patch("payments.paddle_service.Client")
    def test_create_price(self, mock_client_class):
        """Тест создания price."""
        mock_client = Mock()
        mock_price = Mock()
        mock_price.id = "pri_123"

        mock_client.prices.create.return_value = mock_price
        mock_client_class.return_value = mock_client

        service = PaddleService()
        service.client = mock_client

        price_id = service._create_price("pro_123", Decimal("99.00"), "USD")

        assert price_id == "pri_123"
        mock_client.prices.create.assert_called_once()

    def test_extract_status(self):
        """Тест извлечения статуса из Paddle enum."""
        service = PaddleService()

        # Mock Paddle status enum
        mock_status = Mock()
        mock_status.value = "completed"

        result = service._extract_status(mock_status)

        assert result == "completed"

    def test_extract_status_string(self):
        """Тест что строковый статус возвращается как есть."""
        service = PaddleService()

        result = service._extract_status("completed")

        assert result == "completed"

    @patch("payments.paddle_service.Verifier")
    def test_verify_webhook_success(self, mock_verifier_class):
        """Тест успешной верификации webhook."""
        mock_verifier = Mock()
        mock_verifier.verify.return_value = Mock(
            is_verified=True, data={"event_type": "transaction.completed"}
        )
        mock_verifier_class.return_value = mock_verifier

        service = PaddleService()

        body = b'{"event_type":"transaction.completed"}'
        signature = "valid_signature"

        result = service.verify_webhook(body, signature)

        assert result is not None
        assert result["event_type"] == "transaction.completed"

    @patch("payments.paddle_service.Verifier")
    def test_verify_webhook_invalid(self, mock_verifier_class):
        """Тест невалидной webhook сигнатуры."""
        mock_verifier = Mock()
        mock_verifier.verify.side_effect = Exception("Invalid signature")
        mock_verifier_class.return_value = mock_verifier

        service = PaddleService()

        body = b'{"event_type":"transaction.completed"}'
        signature = "invalid_signature"

        result = service.verify_webhook(body, signature)

        assert result is None

    def test_validate_transaction_params_valid(self):
        """Тест валидации валидных параметров транзакции."""
        service = PaddleService()

        # Не должно выбросить исключение
        service._validate_transaction_params(
            customer_id="ctm_123",
            price_id="pri_123",
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel",
        )

    def test_validate_transaction_params_invalid_customer(self):
        """Тест валидации с невалидным customer_id."""
        service = PaddleService()

        with pytest.raises(ValueError, match="customer_id"):
            service._validate_transaction_params(
                customer_id="",
                price_id="pri_123",
                success_url="https://example.com/success",
                cancel_url="https://example.com/cancel",
            )

    def test_validate_transaction_params_invalid_url(self):
        """Тест валидации с невалидным URL."""
        service = PaddleService()

        with pytest.raises(ValueError, match="URL"):
            service._validate_transaction_params(
                customer_id="ctm_123",
                price_id="pri_123",
                success_url="not-a-url",
                cancel_url="https://example.com/cancel",
            )
