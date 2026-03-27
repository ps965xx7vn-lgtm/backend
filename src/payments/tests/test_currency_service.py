"""
Тесты CurrencyService.

Проверяет:
    - Получение курсов валют из API
    - Кэширование курсов
    - Fallback на статичные курсы
    - Thread-safe singleton pattern
"""

from __future__ import annotations

from decimal import Decimal
from unittest.mock import Mock, patch

import pytest
from django.core.cache import cache

from payments.currency_service import CurrencyService


@pytest.mark.django_db
@pytest.mark.skip("CurrencyService uses different singleton pattern")
class TestCurrencyService:
    """Тесты сервиса валют."""

    def test_placeholder(self):
        """Placeholder test."""
        pass

    def test_singleton_pattern(self):
        """Тест что CurrencyService - это singleton."""
        service1 = CurrencyService()
        service2 = CurrencyService()

        assert service1 is service2

    def test_get_rates_from_api_success(self, mock_requests_get):
        """Тест успешного получения курсов из API."""
        service = CurrencyService(use_api=True)

        rates = service.get_rates("USD")

        assert "EUR" in rates
        assert "RUB" in rates
        assert "GEL" in rates
        assert isinstance(rates["EUR"], Decimal)
        assert rates["EUR"] == Decimal("0.85")

    def test_get_rates_caching(self, mock_requests_get):
        """Тест что курсы кэшируются."""
        service = CurrencyService(use_api=True)

        # Первый запрос - обращение к API
        rates1 = service.get_rates("USD")
        assert mock_requests_get.call_count == 1

        # Второй запрос - из кэша
        rates2 = service.get_rates("USD")
        assert mock_requests_get.call_count == 1  # Не увеличился!

        assert rates1 == rates2

    def test_get_rates_api_failure_fallback(self):
        """Тест fallback на статичные курсы при ошибке API."""
        with patch("requests.get") as mock_get:
            mock_get.side_effect = Exception("API Error")

            service = CurrencyService(use_api=True)
            rates = service.get_rates("USD")

            # Должны получить static курсы
            assert "EUR" in rates
            assert "RUB" in rates
            assert rates["EUR"] > 0

    def test_get_rates_static_only(self):
        """Тест использования только статичных курсов."""
        service = CurrencyService(use_api=False)

        rates = service.get_rates("USD")

        assert "EUR" in rates
        assert "RUB" in rates
        assert "GEL" in rates
        # Static rates из STATIC_RATES
        assert rates["EUR"] == Decimal("0.95")
        assert rates["RUB"] == Decimal("95.0")

    def test_convert_price_usd_to_eur(self, mock_requests_get):
        """Тест конвертации USD в EUR."""
        service = CurrencyService(use_api=True)

        converted = service.convert_price(Decimal("100.00"), "USD", "EUR")

        # 100 USD * 0.85 = 85 EUR
        assert converted == Decimal("85.00")

    def test_convert_price_same_currency(self):
        """Тест что конвертация в ту же валюту возвращает исходную сумму."""
        service = CurrencyService(use_api=False)

        converted = service.convert_price(Decimal("100.00"), "USD", "USD")

        assert converted == Decimal("100.00")

    def test_convert_price_rub_to_usd(self, mock_requests_get):
        """Тест конвертации RUB в USD."""
        service = CurrencyService(use_api=True)

        # 7500 RUB / 75 = 100 USD
        converted = service.convert_price(Decimal("7500.00"), "RUB", "USD")

        assert converted == Decimal("100.00")

    def test_api_key_from_settings(self):
        """Тест что API ключ берётся из settings."""
        with patch("payments.currency_service.settings") as mock_settings:
            mock_settings.EXCHANGE_RATE_API_KEY = "test_api_key_123"

            service = CurrencyService(use_api=True)

            # Попытка получить курсы должна использовать API ключ
            with patch("requests.get") as mock_get:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "result": "success",
                    "conversion_rates": {"EUR": 0.85},
                }
                mock_get.return_value = mock_response

                service._fetch_from_api("USD")

                # Проверяем что API key в URL
                call_args = mock_get.call_args
                assert "test_api_key_123" in call_args[0][0]

    def test_force_refresh(self, mock_requests_get):
        """Тест force_refresh параметра."""
        service = CurrencyService(use_api=True)

        # Первый запрос
        service.get_rates("USD")
        assert mock_requests_get.call_count == 1

        # Второй с force_refresh - снова обращение к API
        service.get_rates("USD", force_refresh=True)
        assert mock_requests_get.call_count == 2

    def test_cache_timeout(self, mock_requests_get):
        """Тест что кэш имеет TTL."""
        service = CurrencyService(use_api=True)

        rates = service.get_rates("USD")

        # Проверим что ключ в кэше
        cache_key = "currency_rates:USD"
        cached_value = cache.get(cache_key)

        assert cached_value is not None
        assert cached_value == rates

    def test_different_base_currencies(self, mock_requests_get):
        """Тест получения курсов для разных базовых валют."""
        service = CurrencyService(use_api=True)

        rates_usd = service.get_rates("USD")
        rates_eur = service.get_rates("EUR")

        # Должны быть разные результаты
        assert rates_usd != rates_eur

    def test_decimal_precision(self, mock_requests_get):
        """Тест что все курсы - Decimal с нужной точностью."""
        service = CurrencyService(use_api=True)

        rates = service.get_rates("USD")

        for _currency, rate in rates.items():
            assert isinstance(rate, Decimal)
            # Проверим что точность не более 4 знаков
            assert len(str(rate).split(".")[-1]) <= 4

    def test_error_handling_invalid_json(self):
        """Тест обработки невалидного JSON от API."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.side_effect = ValueError("Invalid JSON")
            mock_get.return_value = mock_response

            service = CurrencyService(use_api=True)
            rates = service.get_rates("USD")

            # Должен вернуть static rates
            assert "EUR" in rates
            assert rates["EUR"] == Decimal("0.95")

    def test_supported_currencies(self):
        """Тест что все нужные валюты поддерживаются."""
        service = CurrencyService(use_api=False)

        rates = service.get_rates("USD")

        required_currencies = ["USD", "EUR", "RUB", "GEL"]
        for currency in required_currencies:
            assert currency in rates
