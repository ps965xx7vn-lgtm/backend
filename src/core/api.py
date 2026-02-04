"""
Core API Router Module - REST API для основных функций платформы Pyland School.

Этот модуль содержит публичные эндпоинты для работы с базовыми функциями сайта.
Используется Django Ninja для автоматической генерации OpenAPI документации и валидации.

API Эндпоинты:
    POST /api/core/feedback/ - Отправка обратной связи от пользователей
    POST /api/core/subscribe/ - Подписка на email рассылку новостей
    GET /api/core/contact-info/ - Получение контактной информации компании
    GET /api/core/stats/ - Получение общей статистики платформы

Особенности:
    - Все эндпоинты публичные (auth=None), не требуют авторизации
    - Полная валидация данных через Pydantic схемы (schemas.py)
    - Обработка дублирования подписок
    - Реактивация неактивных подписок
    - Автоматическая документация в Swagger UI (/api/docs)
    - Type hints для всех параметров и возвращаемых значений

Архитектура:
    - Request/Response модели в schemas.py
    - Все ответы проходят Pydantic валидацию
    - Логика бизнес-процессов в views (формы используются там же)
    - Этот API используется для AJAX запросов с фронтенда

Схемы (Pydantic):
    Input: FeedbackSchema, SubscriptionSchema
    Output: FeedbackResponseSchema, SubscriptionResponseSchema, ContactInfoSchema, StatsSchema

Автор: Pyland Team
Дата: 2025
"""

from __future__ import annotations

import logging

from ninja import Router

from authentication.models import Student
from courses.models import Course, Lesson
from managers.models import Feedback
from notifications.models import Subscription

from .cache_utils import cache_contact_info, cache_stats
from .health import health_check, readiness_check
from .schemas import (
    ContactInfoSchema,
    FeedbackResponseSchema,
    FeedbackSchema,
    StatsSchema,
    SubscriptionResponseSchema,
    SubscriptionSchema,
)

logger = logging.getLogger(__name__)

router = Router(tags=["Core"])

# Вспомогательные функции с кешированием


@cache_contact_info()
def get_cached_contact_info():
    """
    Получает контактную информацию с кешированием (30 минут).
    Статические данные, меняются редко.

    Returns:
        dict: Контактная информация
    """
    return {
        "email": "info@pyland.ru",
        "phone": "+7 (999) 123-45-67",
        "address": "Москва, ул. Примерная, д. 1, офис 101",
        "social_links": {
            "telegram": "https://t.me/pyland",
            "youtube": "https://youtube.com/@pyland",
            "github": "https://github.com/pyland",
            "vk": "https://vk.com/pyland",
        },
        "working_hours": "Пн-Пт: 10:00-18:00 МСК",
    }


@cache_stats()
def get_cached_stats():
    """
    Получает статистику платформы с кешированием (10 минут).

    Returns:
        dict: Словарь со статистикой
    """
    stats = {}

    try:
        stats["total_students"] = (
            Student.objects.filter(user__role__name="student").distinct().count()
        )
    except Exception as e:
        logger.error(f"Ошибка при подсчете студентов: {e}")
        stats["total_students"] = 0

    try:
        stats["total_courses"] = Course.objects.count()
    except Exception as e:
        logger.error(f"Ошибка при подсчете курсов: {e}")
        stats["total_courses"] = 0

    try:
        stats["total_lessons"] = Lesson.objects.count()
    except Exception as e:
        logger.error(f"Ошибка при подсчете уроков: {e}")
        stats["total_lessons"] = 0

    stats["total_hours"] = 0.0
    stats["completion_rate"] = 0.0

    return stats


@router.post("/feedback/", response=FeedbackResponseSchema, auth=None)
def create_feedback(request, data: FeedbackSchema):
    """
    Создает новую заявку обратной связи.

    Публичный эндпоинт (auth=None), доступен без авторизации.

    Args:
        request: HTTP request объект
        data: FeedbackSchema с валидированными данными формы

    Returns:
        FeedbackResponseSchema с информацией об успешном создании

    Example:
        POST /api/core/feedback/
        {
            "first_name": "Иван",
            "phone_number": "+79991234567",
            "email": "ivan@example.com",
            "message": "Хочу узнать больше о курсах",
            "agree_terms": true
        }

        Response 200:
        {
            "success": true,
            "message": "Спасибо! Мы получили ваше сообщение...",
            "feedback_id": 42
        }
    """
    try:
        feedback = Feedback.objects.create(
            first_name=data.first_name,
            phone_number=data.phone_number,
            email=data.email,
            message=data.message,
        )

        logger.info(
            f"API: Создана заявка обратной связи #{feedback.id} от {data.email} ({data.first_name})"
        )

        return FeedbackResponseSchema(
            success=True,
            message="Спасибо! Мы получили ваше сообщение и свяжемся с вами в ближайшее время.",
            feedback_id=feedback.id,
        )
    except Exception as e:
        logger.error(f"API: Ошибка при создании заявки обратной связи: {e}")
        return FeedbackResponseSchema(
            success=False,
            message="Произошла ошибка при отправке сообщения. Пожалуйста, попробуйте позже.",
            feedback_id=None,
        )


@router.post("/subscribe/", response=SubscriptionResponseSchema, auth=None)
def create_subscription(request, data: SubscriptionSchema):
    """
    Подписывает email на рассылку новостей.

    Публичный эндпоинт (auth=None), доступен без авторизации.
    Проверяет существование подписки перед созданием новой.

    Args:
        request: HTTP request объект
        data: SubscriptionSchema с email адресом

    Returns:
        SubscriptionResponseSchema с результатом подписки

    Example:
        POST /api/core/subscribe/
        {
            "email": "user@example.com"
        }

        Response 200 (новая подписка):
        {
            "success": true,
            "message": "Вы успешно подписаны на рассылку!",
            "already_subscribed": false
        }

        Response 200 (уже подписан):
        {
            "success": true,
            "message": "Этот email уже подписан на рассылку.",
            "already_subscribed": true
        }
    """
    try:
        subscription, created = Subscription.subscribe(
            email=data.email,
            subscription_type="email_notifications",  # Общая подписка на все уведомления
        )

        if not created and not subscription.is_active:
            # Реактивация неактивной подписки
            subscription.is_active = True
            subscription.save()
            logger.info(f"API: Реактивирована подписка для {data.email}")
            return SubscriptionResponseSchema(
                success=True,
                message="Ваша подписка снова активна!",
                already_subscribed=False,
            )

        if created:
            logger.info(f"API: Новая подписка на рассылку: {data.email}")
            message = "Вы успешно подписаны на рассылку!"
        else:
            logger.warning(f"API: Попытка повторной подписки: {data.email}")
            message = "Этот email уже подписан на рассылку."

        return SubscriptionResponseSchema(
            success=True, message=message, already_subscribed=not created
        )
    except Exception as e:
        logger.error(f"API: Ошибка при создании подписки: {e}")
        return SubscriptionResponseSchema(
            success=False,
            message="Произошла ошибка при подписке. Пожалуйста, попробуйте позже.",
            already_subscribed=False,
        )


@router.get("/contact-info/", response=ContactInfoSchema, auth=None)
def get_contact_info(request):
    """
    Возвращает контактную информацию компании с кешированием.

    Публичный эндпоинт (auth=None), доступен без авторизации.
    Используется для отображения контактов на фронтенде.
    Данные кешируются на 30 минут.

    Args:
        request: HTTP request объект

    Returns:
        ContactInfoSchema с контактными данными (из кеша)

    Example:
        GET /api/core/contact-info/

        Response 200:
        {
            "email": "info@pyland.ru",
            "phone": "+7 (999) 123-45-67",
            "address": "Москва, ул. Примерная, д. 1",
            "social_links": {
                "telegram": "https://t.me/pyland",
                "youtube": "https://youtube.com/@pyland",
                "github": "https://github.com/pyland"
            },
            "working_hours": "Пн-Пт: 10:00-18:00 МСК"
        }
    """
    # Получаем данные из кеша (30 минут)
    contact_data = get_cached_contact_info()
    return ContactInfoSchema(**contact_data)


@router.get("/stats/", response=StatsSchema, auth=None)
def get_platform_stats(request):
    """
    Возвращает общую статистику платформы.

    Публичный эндпоинт (auth=None), доступен без авторизации.
    Используется для отображения метрик на главной странице.

    Собирает реальные данные из БД:
    - Количество активных студентов
    - Количество опубликованных курсов
    - Общее количество уроков
    - Общая продолжительность контента
    - Средний процент завершения курсов

    Args:
        request: HTTP request объект

    Returns:
        StatsSchema со статистикой платформы

    Example:
        GET /api/core/stats/

        Response 200:
        {
            "total_students": 0,
            "total_courses": 15,
            "total_lessons": 230,
            "total_hours": 145.5,
            "completion_rate": 0.0
        }
        Note: Student count and completion rate are not publicly displayed
    """
    try:
        # Получаем статистику с кешированием (10 минут)
        stats = get_cached_stats()

        return StatsSchema(
            total_students=stats.get("total_students", 0),
            total_courses=stats.get("total_courses", 0),
            total_lessons=stats.get("total_lessons", 0),
            total_hours=stats.get("total_hours", 0.0),
            completion_rate=stats.get("completion_rate", 0.0),
        )
    except Exception as e:
        logger.error(f"API: Критическая ошибка при получении статистики: {e}")
        return StatsSchema(
            total_students=0,
            total_courses=0,
            total_lessons=0,
            total_hours=0.0,
            completion_rate=0.0,
        )


# === Health Check Endpoints для Kubernetes ===


@router.get("/health/", auth=None, include_in_schema=False)
def health_endpoint(request):
    """
    Базовая проверка здоровья (liveness probe).
    Используется Kubernetes для проверки что под жив.

    Returns:
        dict: Базовый статус приложения
    """
    result = health_check()
    return result


@router.get("/readiness/", auth=None, include_in_schema=False)
def readiness_endpoint(request):
    """
    Проверка готовности к обработке запросов (readiness probe).
    Проверяет все критичные зависимости (БД, Redis).

    Returns:
        dict: Полный статус приложения и зависимостей
    """
    result = readiness_check()
    status_code = 200 if result.get("ready", False) else 503

    # Для Ninja можно вернуть tuple (data, status_code)
    if status_code != 200:
        return result, status_code
    return result
