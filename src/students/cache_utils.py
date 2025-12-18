"""
Account Cache Utils Module - Утилиты для безопасной работы с Redis кэшем.

Этот модуль предоставляет функции для управления кэшированием данных профилей:
    - safe_cache_get: Безопасное чтение из кэша с обработкой ошибок Redis
    - safe_cache_set: Безопасная запись в кэш с обработкой ошибок Redis
    - safe_cache_delete: Безопасное удаление из кэша
    - ProgressCacheManager: Менеджер кэша для прогресса обучения пользователей

Все функции обрабатывают исключения Redis и логируют ошибки,
обеспечивая продолжение работы приложения при недоступности кэша.

Автор: Pyland Team
Дата: 2025
"""

from __future__ import annotations

import logging
from typing import Any, List, Optional

from django.core.cache import cache

logger = logging.getLogger(__name__)


def safe_cache_get(key: str, default: Any = None) -> Any:
    """
    Безопасное получение значения из кэша с обработкой ошибок Redis.

    Args:
        key: ключ кэша
        default: значение по умолчанию, если кэш недоступен

    Returns:
        Значение из кэша или default при ошибке
    """
    try:
        return cache.get(key, default)
    except Exception as e:
        logger.warning(f"Redis cache get failed for key '{key}': {e}")
        return default


def safe_cache_set(key: str, value: Any, timeout: Optional[int] = None) -> bool:
    """
    Безопасная запись значения в кэш с обработкой ошибок Redis.

    Args:
        key: ключ кэша
        value: значение для записи
        timeout: время жизни в секундах

    Returns:
        True если запись успешна, False при ошибке
    """
    try:
        cache.set(key, value, timeout)
        return True
    except Exception as e:
        logger.warning(f"Redis cache set failed for key '{key}': {e}")
        return False


def safe_cache_delete(key: str) -> bool:
    """
    Безопасное удаление значения из кэша с обработкой ошибок Redis.

    Args:
        key: ключ кэша

    Returns:
        True если удаление успешно, False при ошибке
    """
    try:
        cache.delete(key)
        return True
    except Exception as e:
        logger.warning(f"Redis cache delete failed for key '{key}': {e}")
        return False


class ProgressCacheManager:
    """Менеджер кэша для данных прогресса обучения"""

    @staticmethod
    def get_cache_keys(student_id: str, course_id: str = None, lesson_id: str = None) -> List[str]:
        """Получить все ключи кэша для студента"""
        keys = [
            f"dashboard_stats_{student_id}",
            f"user_courses_stats_{student_id}",
        ]

        if course_id:
            keys.append(f"course_progress_{course_id}_{student_id}")

        if lesson_id:
            keys.append(f"lesson_progress_{lesson_id}_{student_id}")

        return keys

    @staticmethod
    def invalidate_user_cache(student_id: str, course_id: str = None, lesson_id: str = None):
        """Инвалидировать весь кэш студента или частично"""
        keys = ProgressCacheManager.get_cache_keys(student_id, course_id, lesson_id)

        for key in keys:
            safe_cache_delete(key)

        logger.info(f"Invalidated cache keys: {keys}")

    @staticmethod
    def warm_up_cache(profile, courses=None):
        """
        Предварительно разогреть кэш для пользователя.
        Полезно после регистрации или добавления курсов.
        """

        if not courses:
            courses = profile.courses.prefetch_related(
                "lessons__steps", "lessons__steps__progress"
            ).all()

        # Разогреваем кэш прогресса по курсам
        for course in courses:
            course.get_progress_for_profile(profile, use_cache=True)

            # Разогреваем кэш уроков
            for lesson in course.lessons.all():
                lesson.get_progress_for_profile(profile, use_cache=True)

        logger.info(f"Warmed up cache for profile {profile.id} with {len(courses)} courses")

    @staticmethod
    def get_cache_stats(student_id: str) -> dict:
        """Получить статистику кэша для студента"""
        keys = ProgressCacheManager.get_cache_keys(student_id)
        stats = {}

        for key in keys:
            cached_data = safe_cache_get(key)
            stats[key] = {
                "exists": cached_data is not None,
                "size": len(str(cached_data)) if cached_data else 0,
            }

        return stats


class CacheInvalidationSignals:
    """Сигналы для автоматической инвалидации кэша"""

    @staticmethod
    def on_step_progress_change(sender, instance, **kwargs):
        """Обработчик изменения прогресса шага"""
        student_id = instance.profile.id
        lesson_id = instance.step.lesson.id
        course_id = instance.step.lesson.course.id

        ProgressCacheManager.invalidate_user_cache(student_id, course_id, lesson_id)

    @staticmethod
    def on_course_enrollment(sender, instance, **kwargs):
        """Обработчик записи на курс"""
        # При добавлении курса к профилю
        if kwargs.get("action") == "post_add":
            student_id = instance.id
            ProgressCacheManager.invalidate_user_cache(student_id)

            # Разогреваем кэш для новых курсов
            new_courses = kwargs.get("pk_set", [])
            if new_courses:
                from courses.models import Course

                courses = Course.objects.filter(id__in=new_courses).prefetch_related(
                    "lessons__steps"
                )
                ProgressCacheManager.warm_up_cache(instance, courses)


def setup_cache_signals():
    """Настройка сигналов для автоматической инвалидации кэша"""
    from django.db.models.signals import m2m_changed, post_save

    from authentication.models import Student
    from reviewers.models import StepProgress

    # Сигнал на изменение прогресса шага
    post_save.connect(CacheInvalidationSignals.on_step_progress_change, sender=StepProgress)

    # Сигнал на изменение курсов пользователя
    m2m_changed.connect(
        CacheInvalidationSignals.on_course_enrollment, sender=Student.courses.through
    )


# Декоратор для кэширования результатов методов
def cached_method(timeout=60 * 15, key_prefix=""):
    """
    Декоратор для кэширования результатов методов моделей.

    Args:
        timeout: время жизни кэша в секундах
        key_prefix: префикс для ключа кэша
    """

    def decorator(func):
        def wrapper(self, *args, **kwargs):
            # Генерируем ключ кэша на основе имени метода и аргументов
            cache_key = f"{key_prefix}_{func.__name__}_{self.id}_{hash(str(args) + str(kwargs))}"

            # Проверяем кэш
            cached_result = safe_cache_get(cache_key)
            if cached_result is not None:
                return cached_result

            # Вычисляем результат
            result = func(self, *args, **kwargs)

            # Кэшируем результат
            safe_cache_set(cache_key, result, timeout)

            return result

        return wrapper

    return decorator


# Контекстный менеджер для временного отключения кэша
class disable_cache:
    """Контекстный менеджер для временного отключения кэша"""

    def __init__(self, student_id):
        self.student_id = student_id
        self.disabled_keys = []

    def __enter__(self):
        # Получаем все ключи и временно удаляем их
        keys = ProgressCacheManager.get_cache_keys(self.student_id)
        for key in keys:
            cached_data = safe_cache_get(key)
            if cached_data:
                self.disabled_keys.append((key, cached_data))
                safe_cache_delete(key)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Восстанавливаем кэш только если не было исключений
        if exc_type is None:
            for key, data in self.disabled_keys:
                safe_cache_set(key, data, 60 * 15)  # восстанавливаем на 15 минут
