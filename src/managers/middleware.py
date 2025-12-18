"""
Manager Middleware Module - Middleware для защиты административных эндпоинтов.

Этот модуль предоставляет middleware компоненты для обеспечения безопасности
и контроля доступа к административному API.

Middleware классы:
    - ManagerRateLimitMiddleware: Ограничение частоты запросов
    - ManagerSecurityHeadersMiddleware: HTTP заголовки безопасности

Особенности:
    - Применяется только к /api/managers/ эндпоинтам
    - Разные лимиты для анонимов, авторизованных и staff
    - Логирование всех блокировок
    - Кеширование счетчиков запросов в Redis
    - Type hints для всех методов

Rate Limiting:
    - Анонимные пользователи: 50 запросов/час
    - Авторизованные пользователи: 200 запросов/час
    - Staff пользователи: без ограничений

Security Headers:
    - X-Content-Type-Options: nosniff
    - X-Frame-Options: DENY (для admin панели)
    - X-XSS-Protection: 1; mode=block
    - Referrer-Policy: strict-origin-when-cross-origin

Примечание:
    Для активации добавьте в settings.py MIDDLEWARE:
    'manager.middleware.ManagerRateLimitMiddleware',
    'manager.middleware.ManagerSecurityHeadersMiddleware',

Автор: Pyland Team
Дата: 2025
"""

from __future__ import annotations

import logging
from typing import Callable

from django.core.cache import cache
from django.http import HttpRequest, HttpResponse, JsonResponse

logger = logging.getLogger(__name__)

# ============================================================================
# RATE LIMITING MIDDLEWARE - Ограничение частоты запросов
# ============================================================================


class ManagerRateLimitMiddleware:
    """
    Middleware для ограничения частоты запросов к Manager API.

    Защищает административные эндпоинты от злоупотреблений путем
    ограничения количества запросов в час для разных типов пользователей.

    Лимиты:
        - Анонимные: 50 запросов/час
        - Авторизованные: 200 запросов/час
        - Staff: без ограничений

    Счетчики хранятся в Redis с автоматическим истечением через час.

    Attributes:
        get_response: Следующий middleware или view в цепочке
        rate_limits: Словарь с конфигурацией лимитов

    Example:
        # В settings.py
        MIDDLEWARE = [
            ...
            'manager.middleware.ManagerRateLimitMiddleware',
            ...
        ]

        # При превышении лимита вернется:
        {
            "error": "Rate limit exceeded",
            "detail": "Maximum 50 requests per hour allowed",
            "retry_after": 3600
        }
    """

    def __init__(self, get_response: Callable):
        """
        Инициализирует middleware с конфигурацией лимитов.

        Args:
            get_response: Следующий middleware или view функция
        """
        self.get_response = get_response
        self.rate_limits = {
            "anonymous": {"limit": 50, "window": 3600},  # 50 запросов в час
            "authenticated": {"limit": 200, "window": 3600},  # 200 запросов в час
        }
        logger.info("ManagerRateLimitMiddleware инициализирован")

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """
        Обрабатывает запрос и применяет rate limiting.

        Проверяет количество запросов пользователя за текущий час.
        Если лимит превышен, возвращает 429 Too Many Requests.
        Для staff пользователей rate limiting не применяется.

        Args:
            request: HTTP request объект

        Returns:
            HttpResponse: Ответ от следующего middleware/view или 429 ошибка

        Example:
            >>> # Автоматически вызывается Django для каждого запроса
            >>> # Логика middleware:
            >>> if request.path.startswith("/api/managers/"):
            >>>     check_rate_limit()
        """
        # Применять только к /api/managers/ эндпоинтам
        if not request.path.startswith("/api/managers/"):
            return self.get_response(request)

        # Staff пользователи не ограничиваются
        if request.user.is_authenticated and request.user.is_staff:
            return self.get_response(request)

        # Определить тип пользователя и лимит
        if request.user.is_authenticated:
            user_type = "authenticated"
            user_id = f"user_{request.user.id}"
        else:
            user_type = "anonymous"
            user_id = f"ip_{self.get_client_ip(request)}"

        rate_config = self.rate_limits[user_type]
        cache_key = f"manager:rate_limit:{user_id}"

        # Получить текущее количество запросов
        try:
            current_count = cache.get(cache_key, 0)
        except Exception as e:
            logger.warning(f"Cache GET error in rate limit: {e}. Allowing request.")
            return self.get_response(request)

        # Проверить превышение лимита
        if current_count >= rate_config["limit"]:
            logger.warning(
                f"Rate limit превышен для {user_id}: "
                f"{current_count}/{rate_config['limit']} запросов"
            )
            return JsonResponse(
                {
                    "error": "Rate limit exceeded",
                    "detail": f"Максимум {rate_config['limit']} запросов в час",
                    "retry_after": rate_config["window"],
                },
                status=429,
            )

        # Увеличить счетчик
        try:
            cache.set(cache_key, current_count + 1, rate_config["window"])
        except Exception as e:
            logger.warning(f"Cache SET error in rate limit: {e}. Allowing request.")

        return self.get_response(request)

    @staticmethod
    def get_client_ip(request: HttpRequest) -> str:
        """
        Извлекает IP адрес клиента из request.

        Учитывает proxy и load balancer (заголовок X-Forwarded-For).

        Args:
            request: HTTP request объект

        Returns:
            str: IP адрес клиента

        Example:
            >>> ip = ManagerRateLimitMiddleware.get_client_ip(request)
            >>> print(ip)  # "192.168.1.100"
        """
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR", "unknown")
        return ip


# ============================================================================
# SECURITY HEADERS MIDDLEWARE - HTTP заголовки безопасности
# ============================================================================


class ManagerSecurityHeadersMiddleware:
    """
    Middleware для добавления HTTP заголовков безопасности.

    Добавляет защитные заголовки к ответам административного API
    для предотвращения атак XSS, clickjacking и других угроз.

    Заголовки:
        - X-Content-Type-Options: nosniff (защита от MIME sniffing)
        - X-Frame-Options: DENY (защита от clickjacking)
        - X-XSS-Protection: 1; mode=block (защита от XSS)
        - Referrer-Policy: strict-origin-when-cross-origin (контроль referrer)

    Применяется к:
        - /api/managers/* - Admin API endpoints
        - /managers/* - Admin dashboard pages

    Attributes:
        get_response: Следующий middleware или view в цепочке

    Example:
        # В settings.py
        MIDDLEWARE = [
            ...
            'manager.middleware.ManagerSecurityHeadersMiddleware',
            ...
        ]

        # Все ответы admin API получат заголовки:
        # X-Content-Type-Options: nosniff
        # X-Frame-Options: DENY
        # X-XSS-Protection: 1; mode=block
        # Referrer-Policy: strict-origin-when-cross-origin
    """

    def __init__(self, get_response: Callable):
        """
        Инициализирует middleware.

        Args:
            get_response: Следующий middleware или view функция
        """
        self.get_response = get_response
        logger.info("ManagerSecurityHeadersMiddleware инициализирован")

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """
        Обрабатывает запрос и добавляет заголовки безопасности к ответу.

        Заголовки добавляются только к ответам административных эндпоинтов.
        Если возникает ошибка, заголовки не добавляются и запрос продолжается.

        Args:
            request: HTTP request объект

        Returns:
            HttpResponse: Ответ с добавленными заголовками безопасности

        Example:
            >>> # Автоматически вызывается Django для каждого запроса
            >>> response = self.get_response(request)
            >>> if request.path.startswith("/api/managers/"):
            >>>     response["X-Frame-Options"] = "DENY"
        """
        try:
            response = self.get_response(request)

            # Применять только к /api/managers/ и /managers/ эндпоинтам
            if request.path.startswith("/api/managers/") or request.path.startswith("/managers/"):
                # Предотвратить MIME type sniffing
                response["X-Content-Type-Options"] = "nosniff"

                # Предотвратить clickjacking - DENY для admin области
                response["X-Frame-Options"] = "DENY"

                # Включить XSS protection
                response["X-XSS-Protection"] = "1; mode=block"

                # Контролировать передачу referrer информации
                response["Referrer-Policy"] = "strict-origin-when-cross-origin"

            return response

        except Exception as e:
            logger.error(f"Ошибка в ManagerSecurityHeadersMiddleware: {e}", exc_info=True)
            return self.get_response(request)
