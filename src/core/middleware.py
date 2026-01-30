"""
Middleware для rate limiting API запросов core приложения.
Использует Redis для хранения счетчиков запросов.
"""

from __future__ import annotations

import logging
import time

from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse

logger = logging.getLogger(__name__)


class CoreRateLimitMiddleware:
    """
    Middleware для ограничения частоты запросов к Core API.

    Защищает публичные эндпоинты от злоупотреблений:
    - /api/core/feedback/ - форма обратной связи
    - /api/core/subscribe/ - подписка на рассылку

    Лимиты по умолчанию:
    - Анонимные пользователи: 50 запросов в час
    - Авторизованные пользователи: 200 запросов в час

    Использование:
        Добавьте в settings.py MIDDLEWARE:
        'core.middleware.CoreRateLimitMiddleware',
    """

    def __init__(self, get_response):
        self.get_response = get_response

        # Настройки rate limit (можно переопределить в settings)
        self.rate_limits = getattr(
            settings,
            "CORE_API_RATE_LIMITS",
            {
                "anonymous": {"requests": 50, "window": 3600},  # 50 req/hour
                "authenticated": {"requests": 200, "window": 3600},  # 200 req/hour
            },
        )

        # Пути, которые нужно проверять (только Core API)
        self.api_paths = getattr(
            settings,
            "CORE_RATE_LIMIT_PATHS",
            [
                "/api/core/feedback/",
                "/api/core/subscribe/",
            ],
        )

        logger.info("CoreRateLimitMiddleware инициализирован")

    def __call__(self, request):
        """
        Обрабатывает входящий запрос и проверяет rate limit.

        Args:
            request: Django HttpRequest объект

        Returns:
            HttpResponse или JsonResponse с ошибкой 429
        """
        try:
            # Проверяем только Core API endpoints
            if not any(request.path.startswith(path) for path in self.api_paths):
                return self.get_response(request)

            # Определяем лимит для пользователя
            if request.user.is_authenticated:
                user_key = f"core_rate_limit_user_{request.user.id}"
                limit_config = self.rate_limits["authenticated"]
                user_identifier = f"user:{request.user.id}"
            else:
                # Используем IP адрес для анонимных пользователей
                user_ip = self._get_client_ip(request)
                user_key = f"core_rate_limit_ip_{user_ip}"
                limit_config = self.rate_limits["anonymous"]
                user_identifier = f"IP:{user_ip}"

            max_requests = limit_config["requests"]
            window = limit_config["window"]

            # Получаем текущее количество запросов
            try:
                current_requests = cache.get(user_key, 0)
            except Exception:
                # Если кэш недоступен, пропускаем rate limiting
                return self.get_response(request)

            # Проверяем лимит
            if current_requests >= max_requests:
                # Получаем время до сброса
                try:
                    ttl = cache.ttl(user_key) if hasattr(cache, "ttl") else window
                except Exception:
                    ttl = window
                retry_after = ttl if ttl > 0 else window

                logger.warning(
                    f"Rate limit превышен для {user_identifier} "
                    f"на {request.path}: {current_requests}/{max_requests}"
                )

                return JsonResponse(
                    {
                        "error": "Rate limit exceeded",
                        "message": (
                            f"Превышен лимит запросов. Попробуйте снова через {retry_after} секунд."
                        ),
                        "retry_after": retry_after,
                        "limit": max_requests,
                        "window": window,
                    },
                    status=429,
                )

            # Увеличиваем счетчик
            try:
                if current_requests == 0:
                    # Первый запрос - устанавливаем счетчик и TTL
                    cache.set(user_key, 1, window)
                else:
                    # Инкрементируем существующий счетчик
                    try:
                        cache.incr(user_key)
                    except ValueError:
                        # Если ключ истек между get и incr, создаем заново
                        cache.set(user_key, 1, window)
            except Exception:
                # Если кэш недоступен, пропускаем обновление счетчика
                pass

            # Продолжаем обработку запроса
            response = self.get_response(request)

            # Добавляем headers с информацией о rate limit
            remaining = max(0, max_requests - current_requests - 1)
            response["X-RateLimit-Limit"] = str(max_requests)
            response["X-RateLimit-Remaining"] = str(remaining)
            response["X-RateLimit-Reset"] = str(int(time.time()) + window)

            return response

        except Exception as e:
            logger.error(f"Ошибка в CoreRateLimitMiddleware: {e}")
            # При ошибке пропускаем запрос (fail-open подход)
            return self.get_response(request)

    def _get_client_ip(self, request) -> str:
        """
        Получает реальный IP адрес клиента из запроса.

        Проверяет заголовки в порядке приоритета:
        1. X-Forwarded-For (для проксированных запросов)
        2. X-Real-IP (nginx)
        3. REMOTE_ADDR (прямое подключение)

        Args:
            request: Django HttpRequest объект

        Returns:
            str: IP адрес клиента

        Example:
            >>> ip = self._get_client_ip(request)
            >>> print(ip)
            '192.168.1.1'
        """
        # Проверяем X-Forwarded-For (может содержать цепочку прокси)
        x_forwarded_for = request.headers.get("x-forwarded-for")
        if x_forwarded_for:
            # Берем первый IP (реальный клиент)
            ip = x_forwarded_for.split(",")[0].strip()
            return ip

        # Проверяем X-Real-IP (nginx)
        x_real_ip = request.headers.get("x-real-ip")
        if x_real_ip:
            return x_real_ip.strip()

        # Fallback на REMOTE_ADDR
        return request.META.get("REMOTE_ADDR", "0.0.0.0")


class CoreSecurityHeadersMiddleware:
    """
    Middleware для добавления security headers к ответам.

    Добавляет headers:
    - X-Content-Type-Options: nosniff
    - X-Frame-Options: DENY
    - X-XSS-Protection: 1; mode=block
    - Referrer-Policy: strict-origin-when-cross-origin

    Использование:
        Добавьте в settings.py MIDDLEWARE:
        'core.middleware.CoreSecurityHeadersMiddleware',
    """

    def __init__(self, get_response):
        self.get_response = get_response
        logger.info("CoreSecurityHeadersMiddleware инициализирован")

    def __call__(self, request):
        """Добавляет security headers к ответу."""
        try:
            response = self.get_response(request)

            # Предотвращает MIME-sniffing
            response["X-Content-Type-Options"] = "nosniff"

            # Предотвращает clickjacking (можно изменить на SAMEORIGIN)
            response["X-Frame-Options"] = "DENY"

            # Включает XSS фильтр браузера
            response["X-XSS-Protection"] = "1; mode=block"

            # Контролирует информацию в Referer
            response["Referrer-Policy"] = "strict-origin-when-cross-origin"

            return response
        except Exception as e:
            logger.error(f"Ошибка в CoreSecurityHeadersMiddleware: {e}")
            return self.get_response(request)
