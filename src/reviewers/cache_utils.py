"""
Reviewers Cache Utils - Утилиты кэширования для оптимизации производительности.

Паттерны основаны на students/cache_utils.py:
- Простые функции для получения кэшированных данных
- Инвалидация кэша при изменениях
- Fallback на dummy cache если Redis недоступен

Автор: Pyland Team
Дата: 2025
"""

from __future__ import annotations

import logging
from typing import Any

from django.core.cache import cache
from django.db.models import Avg
from django.utils import timezone

logger = logging.getLogger(__name__)

# Timeout для кэша (10 минут)
CACHE_TIMEOUT = 600


def get_reviewer_stats(reviewer_id: Any) -> dict[str, Any]:
    """
    Получить статистику ревьюера с кэшированием.

    Args:
        reviewer_id: ID ревьюера (UUID)

    Returns:
        dict: Статистика {
            'total_reviews': int,
            'pending_count': int,
            'reviewed_today': int,
            'avg_rating': float,
        }
    """
    cache_key = f"reviewer_stats:{reviewer_id}"

    try:
        # Пробуем получить из кэша
        cached_stats = cache.get(cache_key)
        if cached_stats:
            logger.debug(f"Cache hit for reviewer stats: {reviewer_id}")
            return cached_stats

        # Если нет в кэше - вычисляем
        from authentication.models import Reviewer
        from reviewers.models import LessonSubmission, Review

        reviewer = Reviewer.objects.get(id=reviewer_id)

        # Всего проверок
        total_reviews = Review.objects.filter(reviewer=reviewer).count()

        # Ожидают проверки (по курсам ревьюера)
        pending_count = LessonSubmission.objects.filter(
            status="pending", lesson__course__in=reviewer.courses.all()
        ).count()

        # Проверено сегодня
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        reviewed_today = Review.objects.filter(
            reviewer=reviewer, reviewed_at__gte=today_start
        ).count()

        # Средний рейтинг
        avg_rating = (
            Review.objects.filter(reviewer=reviewer, rating__isnull=False).aggregate(
                avg=Avg("rating")
            )["avg"]
            or 0
        )

        stats = {
            "total_reviews": total_reviews,
            "pending_count": pending_count,
            "reviews_today": reviewed_today,  # Изменено с 'reviewed_today' для соответствия шаблону
            "avg_rating": round(float(avg_rating), 1) if avg_rating else 0.0,
        }

        # Сохраняем в кэш
        cache.set(cache_key, stats, CACHE_TIMEOUT)
        logger.debug(f"Cached reviewer stats: {reviewer_id}")

        return stats

    except Exception as e:
        logger.error(f"Error fetching reviewer stats for {reviewer_id}: {e}")
        # Возвращаем пустую статистику при ошибке
        return {
            "total_reviews": 0,
            "pending_count": 0,
            "reviews_today": 0,  # Изменено с 'reviewed_today' для соответствия шаблону
            "avg_rating": 0.0,
        }


def invalidate_reviewer_cache(reviewer_id: Any) -> None:
    """
    Инвалидировать кэш статистики ревьюера.

    Вызывается при изменении данных:
    - После создания новой проверки
    - После обновления профиля ревьюера
    - После изменения курсов ревьюера

    Args:
        reviewer_id: ID ревьюера (UUID)
    """
    cache_key = f"reviewer_stats:{reviewer_id}"

    try:
        cache.delete(cache_key)
        logger.debug(f"Инвалидирован кэш для ревьюера: {reviewer_id}")
    except Exception as e:
        logger.warning(f"Не удалось инвалидировать кэш для ревьюера {reviewer_id}: {e}")


def get_submission_review_cache_key(submission_id: int) -> str:
    """
    Получить ключ кэша для проверки работы.

    Args:
        submission_id: ID работы

    Returns:
        str: Ключ кэша
    """
    return f"submission_review:{submission_id}"


def cache_submission_review(
    submission_id: int, review_data: dict[str, Any], timeout: int = 300
) -> None:
    """
    Закэшировать данные проверки работы.

    Args:
        submission_id: ID работы
        review_data: Данные проверки
        timeout: Время жизни кэша (по умолчанию 5 минут)
    """
    try:
        cache_key = get_submission_review_cache_key(submission_id)
        cache.set(cache_key, review_data, timeout)
        logger.debug(f"Закэширована проверка работы: {submission_id}")
    except Exception as e:
        logger.warning(f"Не удалось закэшировать проверку работы {submission_id}: {e}")


def get_cached_submission_review(submission_id: int) -> dict[str, Any] | None:
    """
    Получить закэшированные данные проверки работы.

    Args:
        submission_id: ID работы

    Returns:
        dict or None: Данные проверки из кэша или None
    """
    try:
        cache_key = get_submission_review_cache_key(submission_id)
        return cache.get(cache_key)
    except Exception as e:
        logger.warning(f"Failed to get cached submission review {submission_id}: {e}")
        return None


def invalidate_submission_review_cache(submission_id: int) -> None:
    """
    Инвалидировать кэш проверки работы.

    Args:
        submission_id: ID работы
    """
    try:
        cache_key = get_submission_review_cache_key(submission_id)
        cache.delete(cache_key)
        logger.debug(f"Invalidated submission review cache: {submission_id}")
    except Exception as e:
        logger.warning(f"Failed to invalidate submission review cache {submission_id}: {e}")
