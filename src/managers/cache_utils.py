"""
Manager Cache Utils Module - Утилиты кеширования для административных функций.

Этот модуль предоставляет декораторы и функции для кеширования
административной статистики и часто запрашиваемых данных.

Функции кеширования:
    - get_cache_key() - Генерация уникальных ключей кеша с хешированием
    - invalidate_feedback_cache() - Инвалидация всего кеша обратной связи
    - warm_feedback_cache() - Прогрев кеша популярными данными

Декораторы:
    - @cache_feedback_stats() - Кеш статистики обратной связи (10 мин)
    - @cache_feedback_list() - Кеш списка обратной связи (5 мин)

Кешируемые данные:
    - get_cached_feedback_stats() - Статистика обратной связи
    - get_cached_recent_feedback() - Последние сообщения

Особенности:
    - Использует Redis через Django cache framework
    - Автоматическое хеширование длинных ключей (MD5)
    - Поддержка паттернов для массовой инвалидации
    - Логирование всех операций кеша
    - Type hints для всех функций

TTL (Time To Live):
    - Статистика: 600 сек (10 минут)
    - Список сообщений: 300 сек (5 минут)
    - Recent feedback: 300 сек (5 минут)

Примечание:
    При создании/удалении feedback необходимо вызывать invalidate_feedback_cache()
    для обновления кешированных данных.

Автор: Pyland Team
Дата: 2025
"""

from __future__ import annotations

import hashlib
import logging
from collections.abc import Callable
from datetime import datetime, timedelta
from functools import wraps
from typing import Any

from django.core.cache import cache
from django.db.models import Count

from .models import Feedback

logger = logging.getLogger(__name__)

# ============================================================================
# CACHE KEY GENERATION - Генерация ключей кеша
# ============================================================================


def get_cache_key(prefix: str, *args, **kwargs) -> str:
    """
    Генерирует уникальный ключ кеша с префиксом и параметрами.

    Если ключ длиннее 200 символов, автоматически создает MD5 хеш.
    Это необходимо для соблюдения ограничений Redis/Memcached.

    Args:
        prefix: Префикс ключа (например, "manager:feedback_stats")
        *args: Позиционные аргументы для включения в ключ
        **kwargs: Именованные аргументы для включения в ключ

    Returns:
        str: Уникальный ключ кеша

    Example:
        >>> get_cache_key("manager:feedback", page=1, size=20)
        "manager:feedback:page=1:size=20"

        >>> get_cache_key("manager:very_long_key", *range(100))
        "manager:very_long_key:a1b2c3d4..."  # MD5 хеш
    """
    key_parts = [prefix]

    if args:
        key_parts.extend(str(arg) for arg in args)

    if kwargs:
        sorted_kwargs = sorted(kwargs.items())
        key_parts.extend(f"{k}={v}" for k, v in sorted_kwargs)

    key_string = ":".join(key_parts)

    # Хешировать если ключ слишком длинный
    if len(key_string) > 200:
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        return f"{prefix}:{key_hash}"

    return key_string


# ============================================================================
# CACHING DECORATORS - Декораторы кеширования
# ============================================================================


def cache_feedback_stats(timeout: int = 600):
    """
    Декоратор для кеширования статистики обратной связи.

    Кеширует результаты функции на указанное время.
    При повторном вызове с теми же параметрами возвращает кешированные данные.

    Args:
        timeout: Время жизни кеша в секундах (по умолчанию: 10 минут)

    Returns:
        Callable: Декорированная функция

    Example:
        >>> @cache_feedback_stats(timeout=300)  # 5 минут
        >>> def get_stats():
        >>>     return calculate_expensive_stats()
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            cache_key = get_cache_key("manager:feedback_stats", *args, **kwargs)

            # Попытаться получить из кеша
            try:
                cached_data = cache.get(cache_key)
                if cached_data is not None:

                    return cached_data
            except Exception as e:
                logger.warning(f"Cache GET error: {e}. Proceeding without cache.")

            # Получить свежие данные

            data = func(*args, **kwargs)

            # Сохранить в кеш
            try:
                cache.set(cache_key, data, timeout)
            except Exception as e:
                logger.warning(f"Cache SET error: {e}. Data still returned.")

            return data

        return wrapper

    return decorator


def cache_feedback_list(timeout: int = 300):
    """
    Декоратор для кеширования списка обратной связи.

    Кеширует результаты функции на указанное время.
    Используется для пагинированных списков.

    Args:
        timeout: Время жизни кеша в секундах (по умолчанию: 5 минут)

    Returns:
        Callable: Декорированная функция

    Example:
        >>> @cache_feedback_list(timeout=180)  # 3 минуты
        >>> def get_feedback_page(page, size):
        >>>     return Feedback.objects.all()[start:end]
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            cache_key = get_cache_key("manager:feedback_list", *args, **kwargs)

            # Попытаться получить из кеша
            try:
                cached_data = cache.get(cache_key)
                if cached_data is not None:

                    return cached_data
            except Exception as e:
                logger.warning(f"Cache GET error: {e}. Proceeding without cache.")

            # Получить свежие данные

            data = func(*args, **kwargs)

            # Сохранить в кеш
            try:
                cache.set(cache_key, data, timeout)
            except Exception as e:
                logger.warning(f"Cache SET error: {e}. Data still returned.")

            return data

        return wrapper

    return decorator


# ============================================================================
# CACHED HELPER FUNCTIONS - Кешированные вспомогательные функции
# ============================================================================


@cache_feedback_stats(timeout=600)
def get_cached_feedback_stats(recent_count: int = 5) -> dict[str, Any]:
    """
    Получает кешированную статистику обратной связи.

    Вычисляет статистику за различные периоды:
    - Всего сообщений
    - Сегодня, за неделю, за месяц
    - Среднее количество в день
    - Самый активный день недели
    - Последние N сообщений

    Результаты кешируются на 10 минут (600 сек).

    Args:
        recent_count: Количество последних сообщений для включения

    Returns:
        dict: Словарь со статистикой

    Example:
        >>> stats = get_cached_feedback_stats(recent_count=10)
        >>> print(stats['total_feedback'])  # 500
        >>> print(stats['today_feedback'])  # 10
    """
    try:
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=7)
        month_start = today_start - timedelta(days=30)

        # Базовые счетчики
        total = Feedback.objects.count()
        today = Feedback.objects.filter(registered_at__gte=today_start).count()
        week = Feedback.objects.filter(registered_at__gte=week_start).count()
        month = Feedback.objects.filter(registered_at__gte=month_start).count()

        # Среднее в день
        avg_per_day = round(month / 30, 2) if month > 0 else 0.0

        # Самый активный день
        most_active_day = None
        if week > 0:
            daily_counts = (
                Feedback.objects.filter(registered_at__gte=week_start)
                .extra(select={"day": "DATE(registered_at)"})
                .values("day")
                .annotate(count=Count("id"))
                .order_by("-count")
                .first()
            )
            if daily_counts:
                most_active_day = str(daily_counts["day"])

        # Последние сообщения
        recent = list(
            Feedback.objects.all()
            .order_by("-registered_at")[:recent_count]
            .values("id", "first_name", "email", "registered_at")
        )

        logger.info(f"Статистика обратной связи вычислена: всего={total}, сегодня={today}")

        return {
            "total_feedback": total,
            "today_feedback": today,
            "this_week_feedback": week,
            "this_month_feedback": month,
            "average_per_day": avg_per_day,
            "most_active_day": most_active_day,
            "recent_feedback": recent,
        }

    except Exception as e:
        logger.error(f"Ошибка при вычислении статистики обратной связи: {e}", exc_info=True)
        return {
            "total_feedback": 0,
            "today_feedback": 0,
            "this_week_feedback": 0,
            "this_month_feedback": 0,
            "average_per_day": 0.0,
            "most_active_day": None,
            "recent_feedback": [],
        }


@cache_feedback_list(timeout=300)
def get_cached_recent_feedback(count: int = 10) -> list[Feedback]:
    """
    Получает кешированный список последних сообщений обратной связи.

    Результаты кешируются на 5 минут (300 сек).

    Args:
        count: Количество сообщений для возврата

    Returns:
        list: Список объектов Feedback

    Example:
        >>> recent = get_cached_recent_feedback(count=20)
        >>> for feedback in recent:
        >>>     print(feedback.email, feedback.message)
    """
    try:
        feedback_list = list(Feedback.objects.all().order_by("-registered_at")[:count])
        return feedback_list

    except Exception as e:
        logger.error(f"Ошибка при получении последних сообщений: {e}", exc_info=True)
        return []


# ============================================================================
# CACHE INVALIDATION - Инвалидация кеша
# ============================================================================


def invalidate_feedback_cache():
    """
    Инвалидирует весь кеш связанный с обратной связью.

    Должна вызываться при:
    - Создании нового сообщения обратной связи
    - Удалении сообщения
    - Любых изменениях данных feedback

    Удаляет все ключи кеша с паттернами:
    - manager:feedback_stats:*
    - manager:feedback_list:*

    Example:
        >>> feedback = Feedback.objects.create(...)
        >>> invalidate_feedback_cache()  # Обновить кеш
    """
    try:
        # Удалить кеш статистики
        try:
            cache.delete_pattern("manager:feedback_stats:*")
        except Exception as e:
            logger.warning(f"Cache delete_pattern error for feedback_stats: {e}")

        # Удалить кеш списка
        try:
            cache.delete_pattern("manager:feedback_list:*")
        except Exception as e:
            logger.warning(f"Cache delete_pattern error for feedback_list: {e}")

        logger.info("Кеш обратной связи инвалидирован")

    except Exception as e:
        logger.error(f"Ошибка при инвалидации кеша обратной связи: {e}", exc_info=True)


def warm_feedback_cache():
    """
    Прогревает кеш обратной связи часто используемыми данными.

    Заранее вычисляет и кеширует популярные запросы:
    - Статистику с 5 последними сообщениями
    - Последние 10 сообщений

    Рекомендуется вызывать:
    - При запуске приложения
    - Периодически через Celery (каждые 5-10 минут)
    - После инвалидации кеша

    Example:
        >>> # В Celery task
        >>> @periodic_task(run_every=timedelta(minutes=5))
        >>> def warm_cache_task():
        >>>     warm_feedback_cache()
    """
    try:
        # Прогреть кеш статистики
        get_cached_feedback_stats(recent_count=5)

        # Прогреть кеш последних сообщений
        get_cached_recent_feedback(count=10)

        logger.info("Кеш обратной связи успешно прогрет")

    except Exception as e:
        logger.error(f"Ошибка при прогреве кеша обратной связи: {e}", exc_info=True)
