"""
Currency Service Module - Динамическое получение курсов валют.

Получает актуальные курсы валют из внешнего API и кэширует их.
Использует exchangerate-api.com для получения курсов (бесплатный тариф).

Features:
    - Автоматическое обновление курсов
    - Кэширование на 1 час
    - Fallback на статичные курсы при ошибке
    - Thread-safe singleton pattern
    - Логирование всех операций

Автор: Pyland Team
Дата: 2026
"""

from __future__ import annotations

import logging
import threading
from decimal import Decimal
from typing import Final, cast

import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


CACHE_KEY_PREFIX: Final[str] = "currency_rates"
CACHE_TIMEOUT: Final[int] = 3600  # 1 час в секундах
API_TIMEOUT: Final[int] = 5  # Таймаут запроса к API в секундах

# Статичные курсы как fallback (обновлены 26.03.2026)
FALLBACK_RATES: Final[dict[str, Decimal]] = {
    "USD": Decimal("1.00"),
    "EUR": Decimal("0.93"),
    "RUB": Decimal("90.00"),
    "GEL": Decimal("2.65"),
}


class CurrencyServiceError(Exception):
    """Базовое исключение для ошибок currency service."""

    pass


class CurrencyRateFetchError(CurrencyServiceError):
    """Возникает при ошибке получения курсов валют."""

    pass


class CurrencyService:
    """
    Сервис для получения актуальных курсов валют.

    Использует exchangerate-api.com для получения курсов.
    Кэширует результаты для минимизации количества запросов.
    """

    def __init__(self) -> None:
        """Инициализация currency service с настройками."""
        self.api_key = getattr(settings, "EXCHANGE_RATE_API_KEY", None)
        self.use_api = bool(self.api_key)

        if not self.use_api:
            logger.warning(
                "EXCHANGE_RATE_API_KEY не установлен в settings. "
                "Будут использоваться статичные курсы валют."
            )
        else:
            logger.info("Currency service инициализирован с API ключом")

    def get_exchange_rates(self, base_currency: str = "USD") -> dict[str, Decimal]:
        """
        Получить актуальные курсы валют.

        Сначала проверяет кэш. Если данных нет или они устарели,
        запрашивает новые курсы из API и кэширует их.

        Args:
            base_currency: Базовая валюта (по умолчанию USD)

        Returns:
            dict[str, Decimal]: Словарь с курсами валют

        Raises:
            CurrencyRateFetchError: При критических ошибках (без fallback)
        """
        cache_key = f"{CACHE_KEY_PREFIX}:{base_currency}"

        cached_rates = cache.get(cache_key)
        if cached_rates:
            logger.debug(f"Курсы валют получены из кэша для {base_currency}")
            return cast(dict[str, Decimal], cached_rates)

        if self.use_api:
            try:
                rates = self._fetch_from_api(base_currency)
                cache.set(cache_key, rates, CACHE_TIMEOUT)
                logger.info(
                    f"Курсы валют обновлены из API для {base_currency}. "
                    f"Кэширование на {CACHE_TIMEOUT} секунд."
                )
                return rates
            except Exception as e:
                logger.error(
                    f"Ошибка при получении курсов из API: {e}. Используются fallback курсы.",
                    exc_info=True,
                )
                return self._get_fallback_rates()
        else:
            logger.debug("API ключ отсутствует, используются статичные курсы")
            return self._get_fallback_rates()

    def _fetch_from_api(self, base_currency: str) -> dict[str, Decimal]:
        """
        Получить курсы из exchangerate-api.com.

        Args:
            base_currency: Базовая валюта

        Returns:
            dict[str, Decimal]: Курсы валют

        Raises:
            CurrencyRateFetchError: При ошибке запроса
        """
        url = f"https://v6.exchangerate-api.com/v6/{self.api_key}/latest/{base_currency}"

        try:
            response = requests.get(url, timeout=API_TIMEOUT)
            response.raise_for_status()

            data = response.json()

            if data.get("result") != "success":
                raise CurrencyRateFetchError(
                    f"API вернул ошибку: {data.get('error-type', 'unknown')}"
                )

            conversion_rates = data.get("conversion_rates", {})

            rates = {
                currency: Decimal(str(rate))
                for currency, rate in conversion_rates.items()
                if currency in ["USD", "EUR", "RUB", "GEL"]
            }

            if not rates:
                raise CurrencyRateFetchError("API не вернул необходимые валюты")

            logger.info(
                f"Получены курсы из API: {', '.join([f'{k}={v}' for k, v in rates.items()])}"
            )

            return rates

        except requests.RequestException as e:
            raise CurrencyRateFetchError(f"Ошибка HTTP запроса: {e}") from e
        except (ValueError, KeyError) as e:
            raise CurrencyRateFetchError(f"Ошибка парсинга ответа API: {e}") from e

    def _get_fallback_rates(self) -> dict[str, Decimal]:
        """
        Получить статичные fallback курсы.

        Returns:
            dict[str, Decimal]: Fallback курсы валют
        """
        logger.warning("Используются fallback курсы валют (могут быть устаревшими)")
        return FALLBACK_RATES.copy()

    def convert_currency(self, amount: Decimal, from_currency: str, to_currency: str) -> Decimal:
        """
        Конвертировать сумму из одной валюты в другую.

        Args:
            amount: Исходная сумма
            from_currency: Исходная валюта
            to_currency: Целевая валюта

        Returns:
            Decimal: Сконвертированная сумма
        """
        if from_currency == to_currency:
            return amount

        rates = self.get_exchange_rates(base_currency="USD")

        usd_amount = amount / rates[from_currency]
        result = usd_amount * rates[to_currency]

        return result.quantize(Decimal("0.01"))

    def invalidate_cache(self) -> None:
        """
        Принудительно очистить кэш курсов валют.

        Используется для ручного обновления курсов.
        """
        cache_key = f"{CACHE_KEY_PREFIX}:USD"
        cache.delete(cache_key)
        logger.info("Кэш курсов валют очищен")


# Singleton instance with thread-safe initialization
_currency_service: CurrencyService | None = None
_currency_service_lock = threading.Lock()


def get_currency_service() -> CurrencyService:
    """
    Получить thread-safe singleton instance CurrencyService.

    Использует double-checked locking pattern для потокобезопасности.

    Returns:
        CurrencyService: Экземпляр сервиса

    Example:
        >>> service = get_currency_service()
        >>> rates = service.get_exchange_rates()
        >>> converted = service.convert_currency(Decimal("100"), "USD", "EUR")
    """
    global _currency_service

    if _currency_service is None:
        with _currency_service_lock:
            if _currency_service is None:
                _currency_service = CurrencyService()
                logger.info("CurrencyService singleton initialized")

    return _currency_service


__all__ = [
    "CurrencyService",
    "get_currency_service",
    "CurrencyServiceError",
    "CurrencyRateFetchError",
    "FALLBACK_RATES",
]
