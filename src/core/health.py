"""
Health check endpoints для Kubernetes liveness/readiness probes.
"""

import logging
from typing import Any

from django.core.cache import cache
from django.db import connections
from django.db.utils import OperationalError

logger = logging.getLogger(__name__)


def check_database() -> dict[str, Any]:
    """
    Проверка подключения к PostgreSQL.

    Returns:
        dict: Статус подключения к БД
    """
    try:
        conn = connections["default"]
        conn.cursor()
        return {"status": "healthy", "database": "connected"}
    except OperationalError as e:
        logger.error(f"Database connection failed: {e}")
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected database error: {e}")
        return {"status": "unhealthy", "database": "error", "error": str(e)}


def check_redis() -> dict[str, Any]:
    """
    Проверка подключения к Redis.

    Returns:
        dict: Статус подключения к Redis
    """
    try:
        # Пытаемся записать и прочитать из кэша
        cache.set("health_check", "ok", timeout=10)
        result = cache.get("health_check")

        if result == "ok":
            return {"status": "healthy", "redis": "connected"}
        else:
            return {"status": "unhealthy", "redis": "cache_mismatch"}
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        # Redis может быть недоступен, но приложение должно работать (dummy cache)
        return {"status": "degraded", "redis": "disconnected", "error": str(e)}


def health_check() -> dict[str, Any]:
    """
    Базовая проверка здоровья (liveness probe).
    Проверяет только то, что приложение запущено.

    Returns:
        dict: Базовый статус приложения
    """
    return {
        "status": "healthy",
        "service": "pyland-backend",
        "version": "1.0.0",
    }


def readiness_check() -> dict[str, Any]:
    """
    Проверка готовности к обработке запросов (readiness probe).
    Проверяет все критичные зависимости.

    Returns:
        dict: Полный статус приложения и зависимостей
    """
    db_status = check_database()
    redis_status = check_redis()

    # Приложение готово если БД доступна
    # Redis может быть недоступен (degraded) - приложение всё равно работает
    is_ready = db_status["status"] == "healthy"

    overall_status = "healthy" if is_ready else "unhealthy"
    if redis_status["status"] == "degraded":
        overall_status = "degraded"

    return {
        "status": overall_status,
        "service": "pyland-backend",
        "version": "1.0.0",
        "checks": {
            "database": db_status,
            "redis": redis_status,
        },
        "ready": is_ready,
    }
