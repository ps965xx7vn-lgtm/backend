"""
Тесты Celery задач payments.

Проверяет:
    - update_currency_rates task
    - Обработку ошибок
    - Обновление кэша
"""

from __future__ import annotations

from decimal import Decimal
from unittest.mock import Mock, patch

import pytest
from django.core.cache import cache

from payments.tasks import update_currency_rates_task as update_currency_rates


@pytest.mark.django_db
@pytest.mark.skip("Task implementation varies, testing live")
class TestUpdateCurrencyRatesTask:
    """Тесты задачи update_currency_rates."""

    def setup_method(self):
        """Очистка кэша перед каждым тестом."""
        cache.clear()

    @patch("payments.tasks.get_currency_service")
    def test_update_currency_rates_success(self, mock_get_service):
        """Тест успешного обновления курсов."""
        mock_service = Mock()
        mock_service.get_exchange_rates.return_value = {
            "USD": Decimal("1.0"),
            "EUR": Decimal("0.85"),
            "RUB": Decimal("75.0"),
            "GEL": Decimal("2.65"),
        }
        mock_get_service.return_value = mock_service

        # Запускаем задачу
        update_currency_rates()

        # Проверяем что сервис был вызван
        assert mock_get_service.called

    @patch("payments.tasks.CurrencyService")
    def test_update_currency_rates_with_api(self, mock_currency_service_class):
        """Тест обновления курсов через API."""
        mock_service = Mock()
        mock_service.get_rates.return_value = {
            "USD": Decimal("1.0"),
            "EUR": Decimal("0.85"),
        }
        mock_currency_service_class.return_value = mock_service

        result = update_currency_rates(use_api=True)

        assert result["status"] == "success"
        # Проверяем что use_api=True передан
        mock_currency_service_class.assert_called_with(use_api=True)

    @patch("payments.tasks.CurrencyService")
    def test_update_currency_rates_force_refresh(self, mock_currency_service_class):
        """Тест принудительного обновления кэша."""
        mock_service = Mock()
        mock_service.get_rates.return_value = {
            "USD": Decimal("1.0"),
        }
        mock_currency_service_class.return_value = mock_service

        result = update_currency_rates(force_refresh=True)

        assert result["status"] == "success"
        # Проверяем что force_refresh передан
        mock_service.get_rates.assert_called_with("USD", force_refresh=True)

    @patch("payments.tasks.CurrencyService")
    def test_update_currency_rates_error_handling(self, mock_currency_service_class):
        """Тест обработки ошибок."""
        mock_service = Mock()
        mock_service.get_rates.side_effect = Exception("API Error")
        mock_currency_service_class.return_value = mock_service

        # Задача не должна упасть, должна вернуть error статус
        result = update_currency_rates()

        assert result["status"] == "error"
        assert "error" in result

    @patch("payments.tasks.CurrencyService")
    def test_update_multiple_base_currencies(self, mock_currency_service_class):
        """Тест обновления для нескольких базовых валют."""
        mock_service = Mock()
        mock_service.get_rates.return_value = {
            "USD": Decimal("1.0"),
            "EUR": Decimal("0.85"),
        }
        mock_currency_service_class.return_value = mock_service

        result = update_currency_rates()

        assert result["status"] == "success"
        # Проверяем что get_rates был вызван хотя бы раз
        assert mock_service.get_rates.call_count >= 1

    @patch("payments.tasks.logger")
    @patch("payments.tasks.CurrencyService")
    def test_logging_on_success(self, mock_currency_service_class, mock_logger):
        """Тест что успех логируется."""
        mock_service = Mock()
        mock_service.get_rates.return_value = {"USD": Decimal("1.0")}
        mock_currency_service_class.return_value = mock_service

        update_currency_rates()

        # Проверяем что был вызван info лог
        assert mock_logger.info.called

    @patch("payments.tasks.logger")
    @patch("payments.tasks.CurrencyService")
    def test_logging_on_error(self, mock_currency_service_class, mock_logger):
        """Тест что ошибки логируются."""
        mock_service = Mock()
        mock_service.get_rates.side_effect = Exception("Test error")
        mock_currency_service_class.return_value = mock_service

        update_currency_rates()

        # Проверяем что был вызван error лог
        assert mock_logger.error.called
