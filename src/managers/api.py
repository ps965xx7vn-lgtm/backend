"""
Manager API Router Module - REST API для административных функций платформы.

Этот модуль содержит приватные (manager-only) эндпоинты для управления платформой.
Все эндпоинты требуют роли менеджера.

API Эндпоинты:
    GET /api/managers/feedback/ - Список всех сообщений обратной связи (с пагинацией)
    GET /api/managers/feedback/{id}/ - Детали конкретного сообщения
    DELETE /api/managers/feedback/{id}/ - Удаление сообщения обратной связи
    GET /api/managers/feedback/stats/ - Статистика по обратной связи

Особенности:
    - Требуется роль 'manager' для доступа
    - Полная валидация данных через Pydantic схемы
    - Логирование всех административных действий
    - Автоматическая документация в Swagger UI (/api/docs)

Автор: Pyland Team
Дата: 2025
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta

from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import HttpRequest
from ninja import Router

from authentication.decorators import require_role_api

from .models import Feedback
from .schemas import (
    ErrorResponse,
    FeedbackDeleteResponse,
    FeedbackListOut,
    FeedbackOut,
    FeedbackStatsOut,
)

logger = logging.getLogger(__name__)

# Create router (auth handled at API level)
router = Router(tags=["Managers"])

# ============================================================================
# FEEDBACK MANAGEMENT - Управление обратной связью
# ============================================================================


@router.get(
    "/feedback/",
    response={200: FeedbackListOut, 403: ErrorResponse, 500: ErrorResponse},
    summary="Список всех сообщений обратной связи",
    description="Получить пагинированный список всех сообщений обратной связи (только для менеджеров)",
)
@require_role_api(["manager"])
def list_feedback(
    request: HttpRequest,
    page: int = 1,
    page_size: int = 20,
    search: str | None = None,
):
    """
    Получает пагинированный список сообщений обратной связи.

    Доступен только менеджерам.
    Поддерживает поиск по имени, email, телефону и тексту сообщения.

    Args:
        request: HTTP request объект
        page: Номер страницы (по умолчанию: 1)
        page_size: Количество элементов на странице (по умолчанию: 20)
        search: Поисковый запрос (опционально)

    Returns:
        FeedbackListOut: Пагинированный список с метаданными

    Raises:
        403: Недостаточно прав (не менеджер)
        500: Ошибка сервера

    Example:
        GET /api/managers/feedback/?page=1&page_size=20&search=python

        Response 200:
        {
            "count": 100,
            "results": [...],
            "page": 1,
            "page_size": 20,
            "total_pages": 5
        }
    """
    try:
        # Базовый queryset
        queryset = Feedback.objects.all().order_by("-registered_at")

        # Применить поисковый фильтр
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search)
                | Q(email__icontains=search)
                | Q(message__icontains=search)
                | Q(phone_number__icontains=search)
            )

        # Пагинация
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)

        logger.info(
            f"API: Запрошен список обратной связи: страница={page}, "
            f"размер={page_size}, поиск='{search}', всего={paginator.count}"
        )

        return 200, {
            "count": paginator.count,
            "results": list(page_obj.object_list),
            "page": page,
            "page_size": page_size,
            "total_pages": paginator.num_pages,
        }

    except Exception as e:
        logger.error(f"API: Ошибка при получении списка обратной связи: {e}", exc_info=True)
        return 500, {"error": "Не удалось получить список", "detail": str(e)}


@router.get(
    "/feedback/{feedback_id}/",
    response={200: FeedbackOut, 403: ErrorResponse, 404: ErrorResponse, 500: ErrorResponse},
    summary="Детали сообщения обратной связи",
    description="Получить подробную информацию о конкретном сообщении (только для менеджеров)",
)
@require_role_api(["manager"])
def get_feedback(request: HttpRequest, feedback_id: int):
    """
    Получает детальную информацию о сообщении обратной связи по ID.

    Доступен только менеджерам.

    Args:
        request: HTTP request объект
        feedback_id: ID сообщения обратной связи

    Returns:
        FeedbackOut: Объект с полной информацией о сообщении

    Raises:
        403: Недостаточно прав (не менеджер)
        404: Сообщение не найдено
        500: Ошибка сервера

    Example:
        GET /api/managers/feedback/42/

        Response 200:
        {
            "id": 42,
            "first_name": "Иван",
            "phone_number": "+79991234567",
            "email": "ivan@example.com",
            "message": "Хочу узнать о курсах",
            "registered_at": "2025-11-10T10:00:00"
        }
    """
    try:
        feedback = Feedback.objects.get(id=feedback_id)
        logger.info(f"API: Получена обратная связь: ID={feedback_id}")
        return 200, feedback

    except Feedback.DoesNotExist:
        logger.warning(f"API: Обратная связь не найдена: ID={feedback_id}")
        return 404, {
            "error": "Обратная связь не найдена",
            "detail": f"Сообщение с ID {feedback_id} не существует",
        }

    except Exception as e:
        logger.error(f"API: Ошибка при получении обратной связи {feedback_id}: {e}", exc_info=True)
        return 500, {"error": "Не удалось получить сообщение", "detail": str(e)}


@router.delete(
    "/feedback/{feedback_id}/",
    response={
        200: FeedbackDeleteResponse,
        403: ErrorResponse,
        404: ErrorResponse,
        500: ErrorResponse,
    },
    summary="Удалить сообщение обратной связи",
    description="Удалить сообщение обратной связи по ID (только для менеджеров)",
)
@require_role_api(["manager"])
def delete_feedback(request: HttpRequest, feedback_id: int):
    """
    Удаляет сообщение обратной связи по ID.

    Доступен только менеджерам.
    Действие необратимо - сообщение будет удалено из базы данных.

    Args:
        request: HTTP request объект
        feedback_id: ID сообщения для удаления

    Returns:
        FeedbackDeleteResponse: Результат операции удаления

    Raises:
        403: Недостаточно прав (не менеджер)
        404: Сообщение не найдено
        500: Ошибка сервера

    Example:
        DELETE /api/managers/feedback/42/

        Response 200:
        {
            "success": true,
            "message": "Обратная связь успешно удалена",
            "deleted_id": 42
        }
    """
    try:
        feedback = Feedback.objects.get(id=feedback_id)
        feedback_info = str(feedback)
        feedback.delete()

        admin_email = getattr(request.user, "email", "unknown")
        logger.info(
            f"API: Удалена обратная связь: ID={feedback_id}, "
            f"администратор={admin_email}, инфо={feedback_info}"
        )

        return 200, {
            "success": True,
            "message": "Обратная связь успешно удалена",
            "deleted_id": feedback_id,
        }

    except Feedback.DoesNotExist:
        logger.warning(f"API: Обратная связь не найдена для удаления: ID={feedback_id}")
        return 404, {
            "error": "Обратная связь не найдена",
            "detail": f"Сообщение с ID {feedback_id} не существует",
        }

    except Exception as e:
        logger.error(f"API: Ошибка при удалении обратной связи {feedback_id}: {e}", exc_info=True)
        return 500, {"error": "Не удалось удалить сообщение", "detail": str(e)}


@router.get(
    "/feedback/stats/",
    response={200: FeedbackStatsOut, 403: ErrorResponse, 500: ErrorResponse},
    summary="Статистика обратной связи",
    description="Получить подробную статистику по сообщениям обратной связи (только для менеджеров)",
)
@require_role_api(["manager"])
def get_feedback_stats(request: HttpRequest, recent_count: int = 5):
    """
    Получает статистику по обратной связи за различные периоды.

    Доступен только менеджерам.
    Предоставляет агрегированные данные: сегодня, за неделю, за месяц, среднее.
    Результаты кешируются (см. cache_utils.py).

    Args:
        request: HTTP request объект
        recent_count: Количество последних сообщений для включения (по умолчанию: 5)

    Returns:
        FeedbackStatsOut: Объект со статистикой

    Raises:
        403: Недостаточно прав (не менеджер)
        500: Ошибка сервера

    Example:
        GET /api/managers/feedback/stats/?recent_count=10

        Response 200:
        {
            "total_feedback": 500,
            "today_feedback": 10,
            "this_week_feedback": 50,
            "this_month_feedback": 200,
            "average_per_day": 6.67,
            "most_active_day": "2025-11-09",
            "recent_feedback": [...]
        }
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

        # Среднее в день (за последние 30 дней)
        avg_per_day = round(month / 30, 2) if month > 0 else 0.0

        # Самый активный день (за последние 7 дней)
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
        recent = list(Feedback.objects.all().order_by("-registered_at")[:recent_count])

        logger.info(
            f"API: Запрошена статистика обратной связи: "
            f"всего={total}, сегодня={today}, неделя={week}, месяц={month}"
        )

        return 200, {
            "total_feedback": total,
            "today_feedback": today,
            "this_week_feedback": week,
            "this_month_feedback": month,
            "average_per_day": avg_per_day,
            "most_active_day": most_active_day,
            "recent_feedback": recent,
        }

    except Exception as e:
        logger.error(f"API: Ошибка при получении статистики: {e}", exc_info=True)
        return 500, {"error": "Не удалось получить статистику", "detail": str(e)}
