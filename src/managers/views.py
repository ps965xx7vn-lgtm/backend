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
from .forms import FeedbackFilterForm, PaymentRefundForm, PaymentsFilterForm, SystemLogsFilterForm
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


# ============================================================================
# PAYMENTS VIEWS - Управление платежами
# ============================================================================


@login_required
@require_any_role(["manager"], redirect_url="/")
def payments_list_view(request: HttpRequest, user_uuid: uuid.UUID) -> HttpResponse:
    """
    Список всех платежей с фильтрацией и статистикой.

    Показывает:
    - Все транзакции с пагинацией
    - Фильтры: статус, метод оплаты, валюта, диапазоны дат/сумм
    - Статистику: общий доход, количество по статусам
    """
    from authentication.models import Manager
    from payments.models import Payment

    # Проверка прав доступа
    get_object_or_404(Manager, id=user_uuid)
    if request.user.manager.id != user_uuid:
        return redirect("core:home")

    # Фильтрация
    filter_form = PaymentsFilterForm(request.GET or None)
    payments = Payment.objects.select_related("user", "course").order_by("-created_at")

    if filter_form.is_valid():
        data = filter_form.cleaned_data

        if search := data.get("search"):
            payments = payments.filter(
                Q(user__email__icontains=search)
                | Q(user__first_name__icontains=search)
                | Q(user__last_name__icontains=search)
                | Q(transaction_id__icontains=search)
            )

        if status := data.get("status"):
            payments = payments.filter(status=status)

        if payment_method := data.get("payment_method"):
            payments = payments.filter(payment_method=payment_method)

        if currency := data.get("currency"):
            payments = payments.filter(currency=currency)

        if date_from := data.get("date_from"):
            payments = payments.filter(created_at__gte=date_from)

        if date_to := data.get("date_to"):
            payments = payments.filter(created_at__lte=date_to)

        if amount_from := data.get("amount_from"):
            payments = payments.filter(amount__gte=amount_from)

        if amount_to := data.get("amount_to"):
            payments = payments.filter(amount__lte=amount_to)

    # Статистика
    from django.db.models import Count, Sum

    stats = Payment.objects.aggregate(
        total_revenue=Sum("amount", filter=Q(status="completed")),
        total_count=Count("id"),
        completed_count=Count("id", filter=Q(status="completed")),
        pending_count=Count("id", filter=Q(status="pending")),
        processing_count=Count("id", filter=Q(status="processing")),
        failed_count=Count("id", filter=Q(status="failed")),
        refunded_count=Count("id", filter=Q(status="refunded")),
    )

    # Если нет completed платежей, ставим 0
    if stats["total_revenue"] is None:
        stats["total_revenue"] = 0

    # Пагинация
    paginator = Paginator(payments, 20)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    logger.info(f"Manager {request.user.email} viewed payments list (page {page_number})")

    return render(
        request,
        "managers/payments/payments_list.html",
        {
            "page_obj": page_obj,
            "filter_form": filter_form,
            "stats": stats,
            "total_count": paginator.count,
        },
    )


@login_required
@require_any_role(["manager"], redirect_url="/")
def payment_detail_view(
    request: HttpRequest, user_uuid: uuid.UUID, payment_id: int
) -> HttpResponse:
    """
    Детальный просмотр платежа с историей изменений.
    """
    from authentication.models import Manager
    from payments.models import Payment

    get_object_or_404(Manager, id=user_uuid)
    if request.user.manager.id != user_uuid:
        return redirect("core:home")

    payment = get_object_or_404(Payment.objects.select_related("user", "course"), id=payment_id)

    logger.info(f"Manager {request.user.email} viewed payment #{payment_id}")

    return render(
        request,
        "managers/payments/payment_detail.html",
        {
            "payment": payment,
        },
    )


@login_required
@require_any_role(["manager"], redirect_url="/")
def payment_refund_view(
    request: HttpRequest, user_uuid: uuid.UUID, payment_id: int
) -> HttpResponse:
    """
    Обработка возврата платежа.
    """
    from authentication.models import Manager
    from payments.models import Payment

    get_object_or_404(Manager, id=user_uuid)
    if request.user.manager.id != user_uuid:
        return redirect("core:home")

    payment = get_object_or_404(Payment, id=payment_id)

    if payment.status != "completed":
        messages.error(request, "Возврат возможен только для завершенных платежей")
        return redirect("managers:payment_detail", user_uuid, payment_id)

    if request.method == "POST":
        form = PaymentRefundForm(request.POST)
        if form.is_valid():
            # Обновляем статус платежа
            payment.status = "refunded"
            payment.refund_reason = form.cleaned_data["reason"]
            payment.refund_amount = form.cleaned_data["amount"]
            payment.refunded_at = timezone.now()
            payment.refunded_by = request.user
            payment.save()

            # Логируем действие
            from .utils import create_system_log

            create_system_log(
                level="INFO",
                action_type="PAYMENT_REFUNDED",
                message=f"Возврат платежа #{payment_id} на сумму {payment.refund_amount}",
                request=request,
                user=request.user,
                details={
                    "payment_id": payment_id,
                    "amount": float(payment.refund_amount),
                    "reason": payment.refund_reason,
                },
            )

            messages.success(request, f"Возврат платежа #{payment_id} успешно выполнен")
            logger.info(f"Manager {request.user.email} refunded payment #{payment_id}")
            return redirect("managers:payment_detail", user_uuid, payment_id)
    else:
        form = PaymentRefundForm(initial={"amount": payment.amount})

    return render(
        request,
        "managers/payments/payment_refund.html",
        {
            "payment": payment,
            "form": form,
        },
    )


@login_required
@require_any_role(["manager"], redirect_url="/")
def payments_reports_view(request: HttpRequest, user_uuid: uuid.UUID) -> HttpResponse:
    """
    Отчеты и аналитика по платежам.
    """
    from django.db.models import Count, Sum
    from django.db.models.functions import TruncDate

    from authentication.models import Manager
    from payments.models import Payment

    get_object_or_404(Manager, id=user_uuid)
    if request.user.manager.id != user_uuid:
        return redirect("core:home")

    # Период для отчета
    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")

    # Фильтруем платежи
    payments_qs = Payment.objects.filter(status="completed")

    if from_date:
        payments_qs = payments_qs.filter(created_at__gte=from_date)
    if to_date:
        payments_qs = payments_qs.filter(created_at__lte=to_date)

    # Общая статистика
    total_stats = payments_qs.aggregate(
        total_revenue=Sum("amount"),
        total_count=Count("id"),
    )
    # Вычисляем среднее значение
    if total_stats["total_count"] and total_stats["total_count"] > 0:
        total_stats["avg_amount"] = total_stats["total_revenue"] / total_stats["total_count"]
    else:
        total_stats["avg_amount"] = 0

    # Статистика по статусам
    status_stats = Payment.objects.values("status").annotate(count=Count("id"), total=Sum("amount"))

    # Статистика по методам оплаты
    method_stats = Payment.objects.values("payment_method").annotate(
        count=Count("id"), total=Sum("amount")
    )

    # Доход по дням (последние 30 дней)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    daily_revenue = (
        Payment.objects.filter(created_at__gte=thirty_days_ago, status="completed")
        .annotate(date=TruncDate("created_at"))
        .values("date")
        .annotate(revenue=Sum("amount"), count=Count("id"))
        .order_by("date")
    )

    # Топ курсов по доходу
    top_courses = (
        Payment.objects.filter(status="completed")
        .values("course__name")
        .annotate(revenue=Sum("amount"), count=Count("id"))
        .order_by("-revenue")[:10]
    )

    logger.info(f"Manager {request.user.email} viewed payments reports")

    return render(
        request,
        "managers/payments/payments_reports.html",
        {
            "total_stats": total_stats,
            "status_stats": status_stats,
            "method_stats": method_stats,
            "daily_revenue": list(daily_revenue),
            "top_courses": top_courses,
        },
    )


@login_required
@require_any_role(["manager"], redirect_url="/")
def payments_export_view(request: HttpRequest, user_uuid: uuid.UUID) -> HttpResponse:
    """
    Экспорт платежей в CSV.
    """
    import csv

    from django.http import HttpResponse

    from authentication.models import Manager
    from payments.models import Payment

    get_object_or_404(Manager, id=user_uuid)
    if request.user.manager.id != user_uuid:
        return redirect("core:home")

    # Создаем CSV response
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="payments_export.csv"'
    response.write("\ufeff")  # BOM для правильного отображения в Excel

    writer = csv.writer(response)
    writer.writerow(
        [
            "ID",
            "Дата",
            "Пользователь",
            "Email",
            "Телефон",
            "Курс",
            "Сумма",
            "Валюта",
            "Статус",
            "Метод оплаты",
            "ID транзакции",
        ]
    )

    payments = Payment.objects.select_related("user", "course").order_by("-created_at")

    for payment in payments:
        writer.writerow(
            [
                payment.id,
                payment.created_at.strftime("%d.%m.%Y %H:%M"),
                payment.user.get_full_name(),
                payment.user.email,
                (
                    payment.user.student.phone
                    if hasattr(payment.user, "student") and payment.user.student.phone
                    else "-"
                ),
                payment.course.name if payment.course else "-",
                payment.amount,
                payment.currency,
                payment.get_status_display(),
                payment.get_payment_method_display(),
                payment.transaction_id or "-",
            ]
        )

    logger.info(f"Manager {request.user.email} exported payments to CSV")

    return response


# ============================================================================
# USERS MANAGEMENT - Управление пользователями
# ============================================================================


@login_required
@require_any_role(["manager"], redirect_url="/")
def users_list_view(request: HttpRequest, user_uuid: uuid.UUID) -> HttpResponse:
    """
    Список всех пользователей с фильтрами.
    """
    from django.db.models import Q

    from authentication.models import Manager

    from .forms import UserFilterForm

    User = get_user_model()

    # Проверка прав доступа
    get_object_or_404(Manager, id=user_uuid)
    if request.user.manager.id != user_uuid:
        return redirect("core:home")

    # Фильтрация
    filter_form = UserFilterForm(request.GET or None)
    users = (
        User.objects.select_related("role")
        .prefetch_related("student", "reviewer")
        .order_by("-date_joined")
    )

    if filter_form.is_valid():
        data = filter_form.cleaned_data

        if search := data.get("search"):
            users = users.filter(
                Q(email__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
            )

        if role := data.get("role"):
            users = users.filter(role__name=role)

        is_active = data.get("is_active")
        # Фильтруем только если это действительно boolean
        if isinstance(is_active, bool):
            users = users.filter(is_active=is_active)

        if from_date := data.get("from_date"):
            users = users.filter(date_joined__gte=from_date)

        if to_date := data.get("to_date"):
            users = users.filter(date_joined__lte=to_date)

    # Статистика
    stats = {
        "total_users": User.objects.count(),
        "active_users": User.objects.filter(is_active=True).count(),
        "students_count": User.objects.filter(role__name="student").count(),
        "new_this_month": User.objects.filter(
            date_joined__year=timezone.now().year,
            date_joined__month=timezone.now().month,
        ).count(),
    }

    # Пагинация
    paginator = Paginator(users, 20)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    logger.info(f"Manager {request.user.email} viewed users list (page {page_number})")

    return render(
        request,
        "managers/users/users_list.html",
        {
            "page_obj": page_obj,
            "form": filter_form,
            "total_users": stats["total_users"],
            "active_users": stats["active_users"],
            "students_count": stats["students_count"],
            "new_this_month": stats["new_this_month"],
        },
    )


@login_required
@require_any_role(["manager"], redirect_url="/")
def user_detail_view(request: HttpRequest, user_uuid: uuid.UUID, user_id: int) -> HttpResponse:
    """
    Детальная информация о пользователе с статистикой.
    """
    from django.db.models import Sum

    from authentication.models import Manager
    from managers.forms import ManagerNoteForm
    from managers.models import ManagerNote

    User = get_user_model()

    get_object_or_404(Manager, id=user_uuid)
    if request.user.manager.id != user_uuid:
        return redirect("core:home")

    user = get_object_or_404(
        User.objects.select_related("role").prefetch_related("student", "reviewer"), id=user_id
    )

    # Обработка POST запросов
    if request.method == "POST":
        action = request.POST.get("action")

        # Добавление комментария
        if action == "add_note":
            note_form = ManagerNoteForm(request.POST)
            if note_form.is_valid():
                ManagerNote.objects.create(
                    user=user, manager=request.user, note=note_form.cleaned_data["note"]
                )
                messages.success(request, "Комментарий успешно добавлен")
                return redirect("managers:user_detail", user_uuid=user_uuid, user_id=user_id)

        # Подтверждение email вручную
        elif action == "verify_email":
            user.email_is_verified = True
            user.save(update_fields=["email_is_verified"])

            # Логируем действие
            SystemLog.objects.create(
                level="INFO",
                action_type="USER_UPDATED",
                user=request.user,
                message=f"Менеджер {request.user.email} вручную подтвердил email для {user.email}",
                details={"user_id": user.id, "verified_manually": True},
            )

            messages.success(request, "Email успешно подтвержден")
            return redirect("managers:user_detail", user_uuid=user_uuid, user_id=user_id)

    # Получаем все заметки о пользователе
    manager_notes = ManagerNote.objects.filter(user=user).select_related("manager")[:10]
    note_form = ManagerNoteForm()

    context = {
        "viewed_user": user,  # Просматриваемый пользователь
        "manager_notes": manager_notes,
        "note_form": note_form,
    }

    # Статистика для студентов - получаем реальный прогресс
    if hasattr(user, "student") and user.student:
        from certificates.models import Certificate
        from courses.models import Course
        from reviewers.models import LessonSubmission

        # Используем ManyToMany связь
        enrolled_courses = Course.objects.filter(student_enrollments=user.student)

        # Получаем все сертификаты студента
        certificates = Certificate.objects.filter(student=user.student).select_related("course")
        certificates_by_course = {cert.course_id: cert for cert in certificates}

        # Получаем прогресс каждого курса
        enrollments_with_progress = []
        total_completed_steps = 0

        for course in enrolled_courses[:5]:  # Первые 5 курсов
            progress = course.get_progress_for_profile(user.student, use_cache=False)
            certificate = certificates_by_course.get(course.id)

            enrollments_with_progress.append(
                {
                    "course": course,
                    "progress": progress["completion_percentage"],
                    "completed_steps": progress["completed_steps"],
                    "total_steps": progress["total_steps"],
                    "completed_lessons": progress["completed_lessons"],
                    "total_lessons": progress["total_lessons"],
                    "certificate": certificate,
                }
            )
            total_completed_steps += progress["completed_steps"]

        # Получаем pending submissions для студента (работы ожидающие проверки)
        pending_reviews = LessonSubmission.objects.filter(
            student=user.student, status="pending"
        ).count()

        context.update(
            {
                "enrolled_courses": enrolled_courses.count(),
                "enrollments": enrollments_with_progress,
                "completed_steps": total_completed_steps,
                "pending_reviews": pending_reviews,
            }
        )

    # Статистика для ревьюеров
    if hasattr(user, "reviewer") and user.reviewer:
        from reviewers.models import Review

        reviews = Review.objects.filter(reviewer=user.reviewer)
        context.update(
            {
                "total_reviews": reviews.count(),
                "approved_reviews": reviews.filter(status="approved").count(),
                "pending_reviews": reviews.filter(status="pending").count(),
            }
        )

    # История платежей (для всех)
    from payments.models import Payment

    payments = (
        Payment.objects.filter(user=user).select_related("course").order_by("-created_at")[:10]
    )
    total_spent = payments.aggregate(total=Sum("amount"))["total"] or 0

    context.update(
        {
            "total_payments": payments.count(),
            "total_spent": total_spent,
            "recent_payments": payments[:5],
        }
    )

    logger.info(f"Manager {request.user.email} viewed user profile #{user_id}")

    return render(
        request,
        "managers/users/user_detail.html",
        context,
    )


__all__ = [
    "dashboard_view",
    "feedback_list_view",
    "feedback_detail_view",
    "feedback_delete_view",
    "system_logs_view",
    "api_feedback_stats",
    "api_unprocessed_count",
    "users_list_view",
    "user_detail_view",
    "payments_list_view",
    "payment_detail_view",
    "payment_refund_view",
    "payments_reports_view",
    "payments_export_view",
]
