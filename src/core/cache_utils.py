"""
Утилиты для кеширования данных core приложения.
Использует Redis для оптимизации производительности статических страниц.
"""

from __future__ import annotations

import hashlib
import json
import logging
from functools import wraps

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


def get_cache_key(prefix: str, *args, **kwargs) -> str:
    """
    Генерирует уникальный ключ кеша на основе префикса и параметров.

    Args:
        prefix: Префикс ключа (например, 'home_page')
        *args: Позиционные аргументы для включения в ключ
        **kwargs: Именованные аргументы для включения в ключ

    Returns:
        str: Уникальный ключ кеша в формате "core:{prefix}:{hash}"

    Example:
        >>> key = get_cache_key('contact_info', user_id=123)
        >>> print(key)
        'core:contact_info:a1b2c3d4e5f6'
    """
    try:
        # Создаем строку из всех параметров
        params_str = json.dumps({"args": args, "kwargs": sorted(kwargs.items())}, sort_keys=True)

        # Хешируем для короткого ключа
        params_hash = hashlib.md5(params_str.encode(), usedforsecurity=False).hexdigest()[:12]

        return f"core:{prefix}:{params_hash}"
    except Exception as e:
        logger.error(f"Ошибка генерации ключа кеша: {e}")
        # Fallback к простому ключу
        return f"core:{prefix}:default"


def cache_page_data(timeout: int = None, key_prefix: str = "page"):
    """
    Декоратор для кеширования данных страницы.

    Args:
        timeout: Время жизни кеша в секундах (по умолчанию из settings)
        key_prefix: Префикс для ключа кеша

    Returns:
        Декорированная функция с кешированием

    Example:
        @cache_page_data(timeout=300, key_prefix='contact_info')
        def get_contact_info():
            # ... код получения контактов
            return contact_data
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Генерируем ключ кеша
                cache_key = get_cache_key(key_prefix, func.__name__, *args, **kwargs)

                # Пытаемся получить из кеша
                cached_data = cache.get(cache_key)
                if cached_data is not None:
                    return cached_data

                # Вызываем функцию и кешируем результат
                result = func(*args, **kwargs)

                # Определяем timeout
                ttl = timeout
                if ttl is None:
                    cache_ttl = getattr(settings, "CACHE_TTL", {})
                    ttl = cache_ttl.get(key_prefix, 300)  # 5 минут по умолчанию

                cache.set(cache_key, result, ttl)
                return result
            except Exception as e:
                logger.error(f"Ошибка кеширования для {func.__name__}: {e}")
                # При ошибке кеширования просто вызываем функцию
                return func(*args, **kwargs)

        return wrapper

    return decorator


def invalidate_core_cache(patterns: list[str] = None):
    """
    Инвалидирует кеш core приложения по паттернам.

    Args:
        patterns: Список паттернов для инвалидации (например, ['home_page', 'contact_info'])
                 Если None, инвалидирует весь кеш core

    Example:
        # Инвалидировать кеш главной страницы
        invalidate_core_cache(['home_page'])

        # Инвалидировать весь кеш core
        invalidate_core_cache()
    """
    try:
        if patterns is None:
            # Инвалидируем весь кеш core
            cache.delete_pattern("core:*")
            logger.info("Инвалидирован весь кеш core")
        else:
            # Инвалидируем по паттернам
            for pattern in patterns:
                cache.delete_pattern(f"core:{pattern}:*")
                logger.info(f"Инвалидирован кеш core:{pattern}")
    except Exception as e:
        logger.error(f"Ошибка инвалидации кеша: {e}")


def warm_cache():
    """
    Прогревает кеш популярными запросами.
    Можно вызывать периодически через Celery task.

    Кеширует:
    - Контактную информацию
    - Статистику платформы
    - Список курсов для главной страницы
    """
    try:
        from django.db.models import Count

        from courses.models import Course

        # Кешируем топ курсов для главной страницы
        top_courses = Course.objects.annotate(lessons_count=Count("lessons")).order_by(
            "-lessons_count", "name"
        )[:4]

        cache_key = get_cache_key("top_courses")
        try:
            cache.set(cache_key, list(top_courses), 600)  # 10 минут
            logger.info("Прогрет кеш топ курсов")
        except Exception as e:
            logger.warning(f"Ошибка записи в кеш {cache_key}: {e}")

        # Кешируем статистику
        from authentication.models import Student
        from courses.models import Lesson

        stats = {
            "students": Student.objects.filter(user__role__name="student").distinct().count(),
            "courses": Course.objects.count(),
            "lessons": Lesson.objects.count(),
        }

        cache_key = get_cache_key("platform_stats")
        try:
            cache.set(cache_key, stats, 600)  # 10 минут
            logger.info("Прогрет кеш статистики")
        except Exception as e:
            logger.warning(f"Ошибка записи в кеш {cache_key}: {e}")

    except Exception as e:
        logger.error(f"Ошибка прогрева кеша: {e}")


# Декораторы для использования в views и API


def cache_home_page(timeout: int = 300):
    """
    Кеширует данные главной страницы (5 минут).

    Example:
        @cache_home_page()
        def get_home_data():
            return {'courses': courses, 'features': features}
    """
    return cache_page_data(timeout=timeout, key_prefix="home_page")


def cache_contact_info(timeout: int = 1800):
    """
    Кеширует контактную информацию (30 минут).

    Example:
        @cache_contact_info()
        def get_contacts():
            return contact_info
    """
    return cache_page_data(timeout=timeout, key_prefix="contact_info")


def cache_about_page(timeout: int = 3600):
    """
    Кеширует страницу "О нас" (1 час).

    Example:
        @cache_about_page()
        def get_about_data():
            return about_info
    """
    return cache_page_data(timeout=timeout, key_prefix="about_page")


def cache_stats(timeout: int = 600):
    """
    Кеширует статистику платформы (10 минут).

    Example:
        @cache_stats()
        def get_platform_stats():
            return stats_data
    """
    return cache_page_data(timeout=timeout, key_prefix="stats")


def cache_legal_page(timeout: int = 86400):
    """
    Кеширует юридические страницы (24 часа).

    Example:
        @cache_legal_page()
        def get_terms():
            return terms_content
    """
    return cache_page_data(timeout=timeout, key_prefix="legal_page")
