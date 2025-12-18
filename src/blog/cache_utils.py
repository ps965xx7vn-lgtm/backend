"""
Утилиты для кеширования данных блога.
Использует Redis для оптимизации производительности.
"""

import hashlib
import json
import logging
from functools import wraps

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


def get_cache_key(prefix, *args, **kwargs):
    """
    Генерирует уникальный ключ кеша на основе префикса и параметров.

    Args:
        prefix: Префикс ключа (например, 'article_list')
        *args: Позиционные аргументы для включения в ключ
        **kwargs: Именованные аргументы для включения в ключ

    Returns:
        str: Уникальный ключ кеша
    """
    # Создаем строку из всех параметров
    params_str = json.dumps({"args": args, "kwargs": sorted(kwargs.items())}, sort_keys=True)

    # Хешируем для короткого ключа
    params_hash = hashlib.md5(params_str.encode()).hexdigest()[:12]

    return f"blog:{prefix}:{params_hash}"


def cache_page_data(timeout=None, key_prefix="page"):
    """
    Декоратор для кеширования данных страницы с безопасной обработкой ошибок Redis.

    Args:
        timeout: Время жизни кеша в секундах (по умолчанию из settings)
        key_prefix: Префикс для ключа кеша

    Example:
        @cache_page_data(timeout=300, key_prefix='article_list')
        def get_articles(category=None, page=1):
            # ... код получения статей
            return articles
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Генерируем ключ кеша
            cache_key = get_cache_key(key_prefix, func.__name__, *args, **kwargs)

            # Пытаемся получить из кеша (с обработкой ошибок Redis)
            try:
                cached_data = cache.get(cache_key)
                if cached_data is not None:
                    return cached_data
            except Exception as e:
                logger.warning(f"Ошибка чтения кеша {cache_key}: {e}. Продолжаем без кеша.")

            # Вызываем функцию и кешируем результат
            result = func(*args, **kwargs)

            # Определяем timeout
            ttl = timeout
            if ttl is None:
                cache_ttl = getattr(settings, "CACHE_TTL", {})
                ttl = cache_ttl.get(key_prefix, 300)  # 5 минут по умолчанию

            # Пытаемся сохранить в кеш (с обработкой ошибок Redis)
            try:
                cache.set(cache_key, result, ttl)
            except Exception as e:
                logger.warning(f"Ошибка записи в кеш {cache_key}: {e}. Данные не закешированы.")

            return result

        return wrapper

    return decorator


def invalidate_blog_cache(patterns=None):
    """
    Инвалидирует кеш блога по паттернам с безопасной обработкой ошибок Redis.

    Args:
        patterns: Список паттернов для инвалидации (например, ['article_list', 'article_detail'])
                 Если None, инвалидирует весь кеш блога

    Example:
        # Инвалидировать кеш списка статей
        invalidate_blog_cache(['article_list'])

        # Инвалидировать весь кеш блога
        invalidate_blog_cache()
    """
    try:
        if patterns is None:
            # Инвалидируем весь кеш блога
            cache.delete_pattern("blog:*")
        else:
            # Инвалидируем по паттернам
            for pattern in patterns:
                cache.delete_pattern(f"blog:{pattern}:*")
    except Exception as e:
        logger.warning(f"Ошибка инвалидации кеша блога: {e}. Продолжаем работу.")


def warm_cache():
    """
    Прогревает кеш популярными запросами с безопасной обработкой ошибок.
    Можно вызывать периодически через Celery task.
    """
    from blog.models import Article, Category

    try:
        # Кешируем популярные данные
        popular_articles = Article.objects.filter(status="published").order_by("-views_count")[:10]

        cache_key = get_cache_key("popular_articles")
        try:
            cache.set(cache_key, list(popular_articles), 300)
        except Exception as e:
            logger.warning(f"Ошибка записи в кеш {cache_key}: {e}")

        # Кешируем категории
        categories = list(Category.objects.all())
        cache_key = get_cache_key("categories")
        try:
            cache.set(cache_key, categories, 1800)  # 30 минут
        except Exception as e:
            logger.warning(f"Ошибка записи в кеш {cache_key}: {e}")
    except Exception as e:
        logger.warning(f"Ошибка прогрева кеша: {e}. Кеш не прогрет.")


# Декораторы для использования в views


def cache_article_list(timeout=300):
    """Кеширует список статей."""
    return cache_page_data(timeout=timeout, key_prefix="article_list")


def cache_article_detail(timeout=900):
    """Кеширует детали статьи."""
    return cache_page_data(timeout=timeout, key_prefix="article_detail")


def cache_category_list(timeout=1800):
    """Кеширует список категорий."""
    return cache_page_data(timeout=timeout, key_prefix="category_list")


def cache_stats(timeout=600):
    """Кеширует статистику."""
    return cache_page_data(timeout=timeout, key_prefix="stats")
