"""
Middleware для blog приложения.
- Rate limiting для защиты API от злоупотреблений
- Security headers для улучшения безопасности
"""

from __future__ import annotations

import logging
import time

from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse

logger = logging.getLogger(__name__)


class RateLimitMiddleware:
    """
    Middleware для ограничения частоты запросов к API.

    Лимиты по умолчанию:
    - Анонимные пользователи: 100 запросов в час
    - Авторизованные пользователи: 1000 запросов в час
    """

    def __init__(self, get_response):
        self.get_response = get_response

        # Настройки rate limit (можно вынести в settings)
        self.rate_limits = getattr(
            settings,
            "API_RATE_LIMITS",
            {
                "anonymous": {"requests": 100, "window": 3600},  # 100 req/hour
                "authenticated": {"requests": 1000, "window": 3600},  # 1000 req/hour
            },
        )

        # Пути, которые нужно проверять
        self.api_paths = getattr(
            settings,
            "RATE_LIMIT_PATHS",
            [
                "/api/blog/",
                "/api/students/",
                "/api/courses/",
            ],
        )

        logger.info("BlogRateLimitMiddleware инициализирован")

    def __call__(self, request):
        # Проверяем только API endpoints
        if not any(request.path.startswith(path) for path in self.api_paths):
            return self.get_response(request)

        # Определяем лимит для пользователя
        if request.user.is_authenticated:
            user_key = f"rate_limit_user_{request.user.id}"
            limit_config = self.rate_limits["authenticated"]
        else:
            # Используем IP адрес для анонимных пользователей
            user_ip = self._get_client_ip(request)
            user_key = f"rate_limit_ip_{user_ip}"
            limit_config = self.rate_limits["anonymous"]

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
                ttl = cache.ttl(user_key)
            except Exception:
                ttl = window
            retry_after = ttl if ttl > 0 else window

            return JsonResponse(
                {
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Please try again in {retry_after} seconds.",
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
                cache.incr(user_key)
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

    def _get_client_ip(self, request):
        """Получает IP адрес клиента из запроса."""
        x_forwarded_for = request.headers.get("x-forwarded-for")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


class BlogSecurityHeadersMiddleware:
    """
    Middleware для добавления security headers к ответам blog приложения.

    Добавляет headers:
    - X-Content-Type-Options: nosniff
    - X-Frame-Options: SAMEORIGIN (для blog можно встраивать на свой сайт)
    - X-XSS-Protection: 1; mode=block
    - Referrer-Policy: strict-origin-when-cross-origin
    - Content-Security-Policy: базовая защита от XSS

    Использование:
        Добавьте в settings.py MIDDLEWARE:
        'blog.middleware.BlogSecurityHeadersMiddleware',
    """

    def __init__(self, get_response):
        self.get_response = get_response
        logger.info("BlogSecurityHeadersMiddleware инициализирован")

    def __call__(self, request):
        """Добавляет security headers к ответу."""
        try:
            response = self.get_response(request)

            # Предотвращает MIME-sniffing
            response["X-Content-Type-Options"] = "nosniff"

            # Разрешаем встраивание только с того же origin (для iframe в админке)
            response["X-Frame-Options"] = "SAMEORIGIN"

            # Включает XSS фильтр браузера
            response["X-XSS-Protection"] = "1; mode=block"

            # Контролирует информацию в Referer
            response["Referrer-Policy"] = "strict-origin-when-cross-origin"

            # Базовая CSP для блога (разрешаем встраивание изображений, стилей)
            # В production настройте более строгую политику
            if not response.get("Content-Security-Policy"):
                csp = getattr(
                    settings,
                    "BLOG_CSP_POLICY",
                    "default-src 'self'; "
                    "img-src 'self' data: https:; "
                    "style-src 'self' 'unsafe-inline'; "
                    "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                    "font-src 'self' data:;",
                )
                response["Content-Security-Policy"] = csp

            return response
        except Exception as e:
            logger.error(f"Ошибка в BlogSecurityHeadersMiddleware: {e}")
            return self.get_response(request)
