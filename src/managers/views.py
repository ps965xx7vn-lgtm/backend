"""
Manager Views Module - Django views для административной панели менеджеров.

Современная архитектура на основе reviewers/views.py:
- Чистые function-based views
- Декораторы из authentication
- Полное кэширование
- Type hints
- Подробная документация

Views:
    - dashboard_view: Главная страница dashboard со статистикой
    - feedback_list_view: Список всех обращений
    - feedback_detail_view: Детальный просмотр обращения
    - feedback_delete_view: Удаление обращения
    - system_logs_view: Просмотр системных логов
    - api_feedback_stats: API endpoint для статистики

Особенности:
    - Декоратор @require_any_role(['manager'])
    - Кеширование статистики для быстрой загрузки
    - Пагинация списков
    - Фильтрация данных через формы
    - Современный дизайн с уникальной цветовой схемой

Автор: Pyland Team
Дата: 2025
"""

from __future__ import annotations

import logging
import uuid
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from authentication.decorators import require_any_role

from .cache_utils import get_cached_feedback_stats, invalidate_feedback_cache
from .forms import FeedbackFilterForm, SystemLogsFilterForm
from .models import Feedback, SystemLog
from .utils import log_feedback_action

User = get_user_model()
logger = logging.getLogger(__name__)

# ============================================================================
# DASHBOARD - Главная страница панели менеджера
# ============================================================================


@login_required
@require_any_role(["manager"], redirect_url="/")
def dashboard_view(request: HttpRequest, user_uuid: uuid.UUID) -> HttpResponse:
    """
    Главная страница панели менеджера с полной статистикой платформы.

    Отображает:
        - Статистика по пользователям (всего, активных, по ролям, новые за неделю/месяц)
        - Статистика по контенту (статьи, курсы, сертификаты, комментарии)
        - Статистика по платежам (всего, сумма, статусы)
        - Статистика по обратной связи (всего, необработанных, за сегодня)
        - Последние 5 обращений
        - Последние 10 системных логов

    Args:
        request: HTTP запрос от менеджера
        user_uuid: UUID профиля менеджера

    Returns:
        HttpResponse: Отрендеренная страница dashboard

    Template:
        managers/dashboard.html
    """
    # Получаем профиль менеджера
    from authentication.models import Manager

    get_object_or_404(Manager, user=request.user)
    # Получаем кешированную статистику по feedback
    feedback_stats = get_cached_feedback_stats()

    # Последние 5 обращений
    recent_feedback = Feedback.objects.select_related("processed_by").order_by("-registered_at")[:5]

    # Последние 10 системных логов
    recent_logs = SystemLog.objects.select_related("user").order_by("-created_at")[:10]

    # === Статистика по пользователям ===
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    try:
        from authentication.models import Role

        # Базовая статистика
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        new_users_week = User.objects.filter(date_joined__gte=week_ago).count()
        new_users_month = User.objects.filter(date_joined__gte=month_ago).count()

        # Статистика по ролям - преобразуем в список для удобства в шаблоне
        roles_stats = []
        for role in Role.objects.all():
            count = User.objects.filter(role=role).count()
            roles_stats.append({"name": role.get_name_display(), "count": count})

        user_stats = {
            "total_users": total_users,
            "active_users": active_users,
            "new_users_week": new_users_week,
            "new_users_month": new_users_month,
            "by_roles": roles_stats,  # Изменено с by_role на by_roles для соответствия шаблону
        }
    except Exception as e:
        logger.warning(f"Ошибка получения статистики пользователей: {e}")
        user_stats = {
            "total_users": 0,
            "active_users": 0,
            "new_users_week": 0,
            "new_users_month": 0,
            "by_roles": [],  # Изменено на пустой список
        }

    # === Статистика по контенту ===
    content_stats = {}
    try:
        from blog.models import Article, Comment

        content_stats["articles"] = Article.objects.count()
        content_stats["published_articles"] = Article.objects.filter(status="published").count()
        content_stats["comments"] = Comment.objects.count()
    except ImportError:
        logger.debug("Blog app not available")

    try:
        from courses.models import Course

        content_stats["courses"] = Course.objects.count()
    except ImportError:
        logger.debug("Courses app not available")

    try:
        from certificates.models import Certificate

        content_stats["certificates"] = Certificate.objects.count()
    except ImportError:
        logger.debug("Certificates app not available")

    # === Статистика по платежам ===
    payment_stats = {}
    try:
        from payments.models import Payment

        payments = Payment.objects.all()
        payment_stats["total_payments"] = payments.count()
        payment_stats["total_revenue"] = sum(p.amount for p in payments if p.status == "completed")
        payment_stats["pending"] = payments.filter(status="pending").count()
        payment_stats["completed"] = payments.filter(status="completed").count()
        payment_stats["failed"] = payments.filter(status="failed").count()
    except ImportError:
        logger.debug("Payments app not available")

    context = {
        "feedback_stats": feedback_stats,
        "recent_feedback": recent_feedback,
        "recent_logs": recent_logs,
        "user_stats": user_stats,
        "content_stats": content_stats,
        "payment_stats": payment_stats,
    }

    logger.info(f"Manager {request.user.email} accessed dashboard")
    return render(request, "managers/dashboard.html", context)


# ============================================================================
# FEEDBACK MANAGEMENT - Управление обратной связью
# ============================================================================


@login_required
@require_any_role(["manager"], redirect_url="/")
def feedback_list_view(request: HttpRequest, user_uuid: uuid.UUID) -> HttpResponse:
    """
    Список всех обращений обратной связи с фильтрацией и пагинацией.

    Поддерживает фильтрацию по:
        - Поиск по имени, email, телефону, сообщению
        - Дата от/до
        - Статус обработки
        - Тема обращения

    Args:
        request: HTTP запрос (GET параметры для фильтрации)

    Returns:
        HttpResponse: Отрендеренный список обращений

    Template:
        managers/feedback_list.html
    """
    # Получаем все обращения
    feedback_qs = Feedback.objects.select_related("processed_by").order_by("-registered_at")

    # Применяем фильтры из формы
    filter_form = FeedbackFilterForm(request.GET or None)

    if filter_form.is_valid():
        search = filter_form.cleaned_data.get("search")
        date_from = filter_form.cleaned_data.get("date_from")
        date_to = filter_form.cleaned_data.get("date_to")
        is_processed = filter_form.cleaned_data.get("is_processed")
        topic = filter_form.cleaned_data.get("topic")

        # Поиск по нескольким полям
        if search:
            feedback_qs = feedback_qs.filter(
                Q(first_name__icontains=search)
                | Q(email__icontains=search)
                | Q(phone_number__icontains=search)
                | Q(message__icontains=search)
            )

        # Фильтр по дате
        if date_from:
            feedback_qs = feedback_qs.filter(registered_at__date__gte=date_from)
        if date_to:
            feedback_qs = feedback_qs.filter(registered_at__date__lte=date_to)

        # Фильтр по статусу
        if is_processed is not None:
            feedback_qs = feedback_qs.filter(is_processed=is_processed)

        # Фильтр по теме
        if topic:
            feedback_qs = feedback_qs.filter(topic=topic)

    # Пагинация
    paginator = Paginator(feedback_qs, 20)  # 20 записей на страницу
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    # Статистика для sidebar
    stats = {
        "total": Feedback.objects.count(),
        "unprocessed": Feedback.objects.filter(is_processed=False).count(),
        "processed_today": Feedback.objects.filter(
            is_processed=True, processed_at__date=timezone.now().date()
        ).count(),
    }

    # Счетчики для кнопок фильтрации
    pending_count = Feedback.objects.filter(is_processed=False).count()
    processed_count = Feedback.objects.filter(is_processed=True).count()

    logger.info(f"Manager {request.user.email} viewed feedback list (page {page_number})")

    return render(
        request,
        "managers/feedback/feedback_list.html",
        {
            "page_obj": page_obj,
            "filter_form": filter_form,
            "stats": stats,
            "total_count": Feedback.objects.count(),
            "pending_count": pending_count,
            "processed_count": processed_count,
        },
    )


@login_required
@require_any_role(["manager"], redirect_url="/")
def feedback_detail_view(request: HttpRequest, user_uuid: uuid.UUID, pk: int) -> HttpResponse:
    """
    Детальный просмотр и обработка обращения обратной связи.

    Позволяет:
        - Просмотреть полную информацию об обращении
        - Отметить как обработанное/необработанное
        - Добавить заметки менеджера
        - Просмотреть историю обработки

    Args:
        request: HTTP запрос
        pk: ID обращения

    Returns:
        HttpResponse: Детальная страница обращения
        GET: Отображение формы
        POST: Обработка обновления статуса и заметок

    Template:
        managers/feedback_detail.html
    """
    feedback = get_object_or_404(Feedback.objects.select_related("processed_by"), pk=pk)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "mark_processed":
            feedback.is_processed = True
            feedback.processed_by = request.user
            feedback.processed_at = timezone.now()
            feedback.admin_notes = request.POST.get("admin_notes", "")
            feedback.save()
            invalidate_feedback_cache()

            # Логируем обработку
            log_feedback_action(
                action_type="FEEDBACK_UPDATED",
                feedback_id=feedback.id,
                message=f"Обращение #{feedback.id} отмечено как обработанное",
                request=request,
                details={
                    "email": feedback.email,
                    "processed_by": request.user.email,
                },
            )

            messages.success(request, "Обращение успешно обработано.")
            logger.info(f"Manager {request.user.email} processed feedback #{pk}")
            return redirect("managers:feedback_detail", user_uuid, pk)

        elif action == "mark_unprocessed":
            feedback.is_processed = False
            feedback.processed_by = None
            feedback.processed_at = None
            feedback.save()
            invalidate_feedback_cache()

            # Логируем отмену обработки
            log_feedback_action(
                action_type="FEEDBACK_UPDATED",
                feedback_id=feedback.id,
                message=f"Обращение #{feedback.id} возвращено в необработанные",
                request=request,
                details={
                    "email": feedback.email,
                    "unmarked_by": request.user.email,
                },
            )

            messages.info(request, "Обращение отмечено как необработанное.")
            logger.info(f"Manager {request.user.email} unmarked feedback #{pk}")
            return redirect("managers:feedback_detail", user_uuid, pk)

        elif action == "save_notes":
            feedback.admin_notes = request.POST.get("admin_notes", "")
            feedback.save()
            messages.success(request, "Заметки обновлены.")
            logger.info(f"Manager {request.user.email} updated notes for feedback #{pk}")
            return redirect("managers:feedback_detail", user_uuid, pk)

    return render(request, "managers/feedback/feedback_detail.html", {"feedback": feedback})


@login_required
@require_any_role(["manager"], redirect_url="/")
def feedback_delete_view(request: HttpRequest, user_uuid: uuid.UUID, pk: int) -> HttpResponse:
    """
    Удаление обращения обратной связи.

    Args:
        request: HTTP запрос
        pk: ID обращения

    Returns:
        HttpResponse: Redirect на список обращений после удаления
    """
    feedback = get_object_or_404(Feedback, pk=pk)

    if request.method == "POST":
        feedback.delete()
        invalidate_feedback_cache()
        messages.success(request, "Обращение успешно удалено.")
        logger.warning(f"Manager {request.user.email} deleted feedback #{pk}")
        return redirect("managers:feedback_list", user_uuid)

    return render(request, "managers/feedback/feedback_confirm_delete.html", {"feedback": feedback})


@login_required
@require_any_role(["manager"], redirect_url="/")
def feedback_delete(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Удаление обращения обратной связи.

    Args:
        request: HTTP запрос (только POST)
        pk: ID обращения для удаления

    Returns:
        HttpResponse: Редирект на список после удаления

    Security:
        - Только POST метод
        - Требует подтверждения
        - Логирует удаление в SystemLog

    Примечание:
        Перед удалением создается запись в SystemLog для аудита.
    """
    feedback = get_object_or_404(Feedback, pk=pk)

    if request.method == "POST":
        # Логируем удаление с использованием новой утилиты
        log_feedback_action(
            action_type="FEEDBACK_DELETED",
            feedback_id=feedback.id,
            message=f"Обращение #{feedback.id} от {feedback.email} удалено",
            request=request,
            details={
                "email": feedback.email,
                "name": feedback.first_name,
                "deleted_by": request.user.email,
            },
        )

        feedback.delete()
        messages.success(request, f"Обращение #{pk} успешно удалено.")
        return redirect("manager:feedback_list")

    context = {
        "feedback": feedback,
        "page_title": "Подтверждение удаления",
    }

    return render(request, "managers/feedback_confirm_delete.html", context)


# ============================================================================
# SYSTEM LOGS - Просмотр системных логов
# ============================================================================


@login_required
@require_any_role(["manager"], redirect_url="/")
def system_logs_view(request: HttpRequest, user_uuid: uuid.UUID) -> HttpResponse:
    """
    Просмотр системных логов с фильтрацией.

    Позволяет просматривать и фильтровать системные события:
        - По уровню (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        - По типу действия (LOGIN, LOGOUT, CREATE, UPDATE, DELETE и т.д.)
        - По дате
        - По поисковому запросу

    Args:
        request: HTTP запрос (GET параметры для фильтрации)

    Returns:
        HttpResponse: Страница со списком логов

    Template:
        managers/logs/system_logs.html
    """
    logs_qs = SystemLog.objects.select_related("user").order_by("-created_at")

    # Применяем фильтры из формы
    filter_form = SystemLogsFilterForm(request.GET or None)

    if filter_form.is_valid():
        search = filter_form.cleaned_data.get("search")
        level = filter_form.cleaned_data.get("level")
        action_type = filter_form.cleaned_data.get("action_type")
        date_from = filter_form.cleaned_data.get("date_from")
        date_to = filter_form.cleaned_data.get("date_to")

        if search:
            logs_qs = logs_qs.filter(Q(message__icontains=search) | Q(ip_address__icontains=search))

        if level:
            logs_qs = logs_qs.filter(level=level)

        if action_type:
            logs_qs = logs_qs.filter(action_type=action_type)

        if date_from:
            logs_qs = logs_qs.filter(created_at__date__gte=date_from)

        if date_to:
            logs_qs = logs_qs.filter(created_at__date__lte=date_to)

    # Пагинация
    paginator = Paginator(logs_qs, 20)  # 20 записей на страницу
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    logger.info(f"Manager {request.user.email} viewed system logs (page {page_number})")

    return render(
        request,
        "managers/logs/system_logs.html",
        {
            "page_obj": page_obj,
            "filter_form": filter_form,
            "total_count": logs_qs.count(),
        },
    )


# ============================================================================
# API ENDPOINTS - JSON endpoints для динамической загрузки
# ============================================================================


@login_required
@require_any_role(["manager"], redirect_url="/")
def api_feedback_stats(request: HttpRequest, user_uuid: uuid.UUID) -> JsonResponse:
    """
    API endpoint для получения статистики по обратной связи.

    Returns:
        JsonResponse: JSON с актуальной статистикой
    """
    stats = get_cached_feedback_stats()
    return JsonResponse(stats)


@login_required
@require_any_role(["manager"], redirect_url="/")
def api_unprocessed_count(request: HttpRequest, user_uuid: uuid.UUID) -> JsonResponse:
    """
    API endpoint для получения количества необработанных обращений.

    Returns:
        JsonResponse: {"count": int}
    """
    count = Feedback.objects.filter(is_processed=False).count()
    return JsonResponse({"count": count})
