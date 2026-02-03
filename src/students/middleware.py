"""
Students Middleware Module - Middleware для кэширования, rate limiting и мониторинга.

Этот модуль содержит middleware компоненты для студентов:
    - StudentsRateLimitMiddleware: Ограничение частоты запросов для студентов
    - ProgressCacheMiddleware: Мониторинг и заголовки кэша (debug режим)
    - CacheHitCounterMiddleware: Подсчет попаданий/промахов кэша
    - cache_context_processor: Передача статистики кэша в шаблоны
    - cache_key_versioning: Версионирование ключей кэша
    - get_cache_settings: Рекомендуемые настройки Redis

Используется для защиты от злоупотреблений и оптимизации производительности.

Автор: Pyland Team
Дата: 2025
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from typing import Any

from django.conf import settings
from django.core.cache import cache
from django.http import HttpRequest, HttpResponse, JsonResponse

logger = logging.getLogger(__name__)


class StudentsRateLimitMiddleware:
    """
    Rate limiting middleware для защиты студентских endpoints от злоупотреблений.

    Ограничивает количество запросов к /students/* маршрутам:
        - Аутентифицированные: 1000 запросов/час
        - Анонимные: 100 запросов/час

    Использует Redis для хранения счетчиков с автоматическим TTL.
    При превышении лимита возвращает HTTP 429 с информацией о retry_after.

    Attributes:
        get_response: Callable для получения ответа Django
        rate_limits: Настройки лимитов для разных типов пользователей

    Example:
        # В settings.py:
        MIDDLEWARE = [
            ...
            'students.middleware.StudentsRateLimitMiddleware',
        ]

        # При превышении лимита:
        # HTTP 429 Too Many Requests
        # {
        #     "error": "Rate limit exceeded",
        #     "retry_after": 3600,
        #     "limit": 1000
        # }
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        """
        Инициализация middleware с настройками лимитов.

        Args:
            get_response: Callable для обработки запроса Django
        """
        self.get_response = get_response
        self.rate_limits = {
            "authenticated": {
                "requests": getattr(settings, "STUDENTS_RATE_LIMIT_AUTHENTICATED", 1000),
                "window": 3600,  # 1 час
            },
            "anonymous": {
                "requests": getattr(settings, "STUDENTS_RATE_LIMIT_ANONYMOUS", 100),
                "window": 3600,  # 1 час
            },
        }
        logger.info("StudentsRateLimitMiddleware инициализирован")

    def _get_client_ip(self, request: HttpRequest) -> str:
        """
        Получает IP адрес клиента с учетом прокси.

        Args:
            request: HTTP запрос Django

        Returns:
            IP адрес клиента
        """
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """
        Проверяет rate limit перед обработкой запроса к /students/*.

        Args:
            request: HTTP запрос Django

        Returns:
            HttpResponse или JsonResponse(429) при превышении лимита
        """
        # Применяем rate limiting только к /students/ маршрутам
        if not request.path.startswith("/students/"):
            return self.get_response(request)

        # Определяем ключ и лимит на основе аутентификации
        if request.user.is_authenticated:
            user_key = f"students_rate_limit_user_{request.user.id}"
            limit_config = self.rate_limits["authenticated"]
            user_identifier = f"User:{request.user.id}"
        else:
            user_ip = self._get_client_ip(request)
            user_key = f"students_rate_limit_ip_{user_ip}"
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
                f"Rate limit exceeded for {user_identifier} "
                f"on {request.path}: {current_requests}/{max_requests}"
            )

            return JsonResponse(
                {
                    "error": "Rate limit exceeded",
                    "message": f"Превышен лимит запросов. Попробуйте снова через {retry_after} секунд.",
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


class StudentsSecurityHeadersMiddleware:
    """
    Middleware for adding security headers to students app responses.

    Adds headers:
    - X-Content-Type-Options: nosniff
    - X-Frame-Options: DENY (students area should not be embedded)
    - X-XSS-Protection: 1; mode=block
    - Referrer-Policy: strict-origin-when-cross-origin
    - Content-Security-Policy: basic XSS protection

    Usage:
        Add to settings.py MIDDLEWARE:
        'students.middleware.StudentsSecurityHeadersMiddleware',
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        """
        Initialize middleware.

        Args:
            get_response: Callable for handling Django request
        """
        self.get_response = get_response
        logger.info("StudentsSecurityHeadersMiddleware инициализирован")

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """
        Add security headers to response.

        Args:
            request: Django HTTP request

        Returns:
            HttpResponse with security headers
        """
        try:
            response = self.get_response(request)

            # Prevent MIME-sniffing
            response["X-Content-Type-Options"] = "nosniff"

            # Deny embedding in iframes (students area is private)
            response["X-Frame-Options"] = "DENY"

            # Enable browser XSS filter
            response["X-XSS-Protection"] = "1; mode=block"

            # Control Referer information
            response["Referrer-Policy"] = "strict-origin-when-cross-origin"

            # Basic CSP for students (stricter than blog)
            # In production configure more restrictive policy
            if not response.get("Content-Security-Policy"):
                csp = getattr(
                    settings,
                    "STUDENTS_CSP_POLICY",
                    "default-src 'self'; "
                    "img-src 'self' data: https:; "
                    "style-src 'self' 'unsafe-inline'; "
                    "script-src 'self' 'unsafe-inline'; "
                    "font-src 'self' data:; "
                    "frame-ancestors 'none';",
                )
                response["Content-Security-Policy"] = csp

            return response

        except Exception as e:
            logger.error(f"Error in StudentsSecurityHeadersMiddleware: {e}")
            return self.get_response(request)


class ProgressCacheMiddleware:
    """
    Middleware для мониторинга производительности кэша прогресса обучения.

    В DEBUG режиме добавляет HTTP заголовки с метриками:
        - X-Cache-Stats: количество закэшированных записей
        - X-Cache-Performance: время выполнения запроса

    Attributes:
        get_response: Callable для получения ответа Django

    Example:
        # В settings.py:
        MIDDLEWARE = [
            ...
            'students.middleware.ProgressCacheMiddleware',
        ]

        # В ответе появятся заголовки:
        # X-Cache-Stats: 5/10 cached
        # X-Cache-Performance: 0.123s
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        """
        Инициализация middleware.

        Args:
            get_response: Callable для обработки запроса Django
        """
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """
        Обрабатывает входящий запрос и добавляет заголовки с метриками кэша.

        Args:
            request: HTTP запрос Django

        Returns:
            HttpResponse с дополнительными заголовками в DEBUG режиме
        """
        # Засекаем время начала запроса
        start_time = time.time()

        response = self.get_response(request)

        # В debug режиме добавляем заголовки с информацией о кэше
        if settings.DEBUG and hasattr(request, "user") and request.user.is_authenticated:
            try:
                elapsed = time.time() - start_time

                # Получаем информацию о кэше пользователя
                if hasattr(request.user, "student"):
                    from students.cache_utils import ProgressCacheManager

                    cache_stats = ProgressCacheManager.get_cache_stats(request.user.student.id)
                    cached_entries = sum(
                        1 for stat in cache_stats.values() if stat.get("exists", False)
                    )
                    total_entries = len(cache_stats)

                    response["X-Cache-Stats"] = f"{cached_entries}/{total_entries} cached"
                response["X-Cache-Performance"] = f"{elapsed:.3f}s"
            except Exception:
                pass

        return response


class CacheHitCounterMiddleware:
    """
    Middleware для подсчета и логирования попаданий/промахов кэша.

    Оборачивает методы cache.get() и cache.set() для логирования операций
    с ключами прогресса обучения, dashboard и статистики курсов.

    Attributes:
        get_response: Callable для получения ответа Django
        original_get: Оригинальный метод cache.get
        original_set: Оригинальный метод cache.set

    Example:
        # В логах появятся записи:
        # DEBUG Cache HIT: progress_user_123_course_456
        # DEBUG Cache MISS: dashboard_stats_user_789
        # DEBUG Cache SET: courses_stats_user_123 (timeout: 900s)
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        """
        Инициализация middleware и подмена методов кэша.

        Args:
            get_response: Callable для обработки запроса Django
        """
        self.get_response = get_response
        self.original_get = cache.get
        self.original_set = cache.set

        # Заменяем методы кэша для подсчета
        cache.get = self._counted_get
        cache.set = self._counted_set

    def _counted_get(self, key: str, default: Any = None, version: Any = None) -> Any:
        """
        Обертка для cache.get с логированием попаданий и промахов.

        Args:
            key: Ключ кэша
            default: Значение по умолчанию если ключ не найден
            version: Версия ключа кэша

        Returns:
            Значение из кэша или default
        """
        result = self.original_get(key, default, version)

        # Логируем только ключи прогресса
        if "progress" in key or "dashboard" in key or "courses_stats" in key:
            if result is not None:
                pass
            else:
                pass

        return result

    def _counted_set(
        self, key: str, value: Any, timeout: int | None = None, version: Any = None
    ) -> bool:
        """
        Обертка для cache.set с логированием установки значений.

        Args:
            key: Ключ кэша
            value: Значение для сохранения
            timeout: Время жизни в секундах
            version: Версия ключа кэша

        Returns:
            True если значение успешно сохранено
        """
        if "progress" in key or "dashboard" in key or "courses_stats" in key:
            pass

        return self.original_set(key, value, timeout, version)

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """
        Обрабатывает запрос (без модификаций).

        Args:
            request: HTTP запрос Django

        Returns:
            HttpResponse без изменений
        """
        return self.get_response(request)


def cache_key_versioning(user_id: str | int, version: str = "v1") -> str:
    """
    Генератор версионированных ключей кэша для пользователя.

    Используется для инвалидации кэша при изменении структуры данных.

    Args:
        user_id: ID пользователя или UUID профиля
        version: Версия структуры данных (по умолчанию 'v1')

    Returns:
        Версионированный ключ в формате: v1_user_123

    Example:
        >>> cache_key_versioning(123, 'v2')
        'v2_123'
        >>> cache_key_versioning('uuid-here')
        'v1_uuid-here'
    """
    return f"{version}_{user_id}"


def get_cache_settings() -> dict[str, Any]:
    """
    Возвращает рекомендуемые настройки Redis для кэширования прогресса обучения.

    Настройки оптимизированы для хранения прогресса пользователей с TTL 15 минут.

    Returns:
        Dict с конфигурацией Django cache backend для Redis

    Example:
        # В settings.py:
        >>> from students.middleware import get_cache_settings
        >>> CACHES = get_cache_settings()
    """
    return {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": "redis://127.0.0.1:6379/1",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            },
            "KEY_PREFIX": "pyland_progress",
            "TIMEOUT": 60 * 15,  # 15 минут по умолчанию
        }
    }


def cache_context_processor(request: HttpRequest) -> dict[str, Any]:
    """
    Контекстный процессор для передачи статистики кэша в шаблоны (только DEBUG).

    Добавляет информацию о кэше в контекст всех шаблонов для отладки:
        - cached_entries: количество закэшированных записей
        - total_entries: общее количество записей
        - total_size: размер кэша в байтах
        - cache_efficiency: процент попаданий в кэш

    Args:
        request: HTTP запрос Django

    Returns:
        Dict с ключом 'cache_info' и статистикой или пустой dict

    Example:
        # В settings.py:
        TEMPLATES = [{
            'OPTIONS': {
                'context_processors': [
                    'students.middleware.cache_context_processor',
                ]
            }
        }]

        # В шаблоне:
        {{ cache_info.cache_efficiency }}  # "75.5%"
    """
    if not settings.DEBUG or not request.user.is_authenticated:
        return {}

    if not hasattr(request.user, "student"):
        return

    try:
        from students.cache_utils import ProgressCacheManager

        cache_stats = ProgressCacheManager.get_cache_stats(request.user.student.id)
        cached_entries = sum(1 for stat in cache_stats.values() if stat["exists"])
        total_size = sum(stat["size"] for stat in cache_stats.values())

        return {
            "cache_info": {
                "cached_entries": cached_entries,
                "total_entries": len(cache_stats),
                "total_size": total_size,
                "cache_efficiency": (
                    f"{cached_entries / len(cache_stats) * 100:.1f}%" if cache_stats else "0%"
                ),
            }
        }
    except Exception as e:
        logger.error(f"Ошибка получения статистики кэша: {e}")
        return {}
        return {"cache_info": None}
