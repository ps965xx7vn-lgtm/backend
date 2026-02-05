"""
Payments Views для Managers - Views для управления платежами.

Этот модуль содержит views для менеджеров по управлению платежами:
- Просмотр списка транзакций с фильтрацией
- Детальная информация о платеже
- Возврат средств
- Отчеты и статистика
- Export данных в CSV

Автор: Pyland Team
Дата: 2026
"""

from __future__ import annotations

import csv
import logging
from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Avg, Count, Q, Sum
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from authentication.decorators import require_any_role
from payments.models import Payment

from .forms import PaymentRefundForm, PaymentsFilterForm
from .utils import create_system_log

logger = logging.getLogger(__name__)


@login_required
@require_any_role(["manager"], redirect_url="/")
def payments_list_view(request: HttpRequest, user_uuid) -> HttpResponse:
    """
    Список всех платежных транзакций с фильтрацией и пагинацией.

    Отображает таблицу платежей с возможностью фильтрации по:
    - Поисковому запросу (ID, email, название курса)
    - Статусу платежа
    - Методу оплаты
    - Валюте
    - Диапазону дат
    - Диапазону сумм
    """
    # Базовый queryset
    payments = Payment.objects.select_related("user", "course").order_by("-created_at")

    # Фильтрация
    filter_form = PaymentsFilterForm(request.GET)
    if filter_form.is_valid():
        search = filter_form.cleaned_data.get("search")
        status = filter_form.cleaned_data.get("status")
        payment_method = filter_form.cleaned_data.get("payment_method")
        currency = filter_form.cleaned_data.get("currency")
        date_from = filter_form.cleaned_data.get("date_from")
        date_to = filter_form.cleaned_data.get("date_to")
        amount_min = filter_form.cleaned_data.get("amount_min")
        amount_max = filter_form.cleaned_data.get("amount_max")

        if search:
            payments = payments.filter(
                Q(transaction_id__icontains=search)
                | Q(user__email__icontains=search)
                | Q(course__title__icontains=search)
            )

        if status:
            payments = payments.filter(status=status)

        if payment_method:
            payments = payments.filter(payment_method=payment_method)

        if currency:
            payments = payments.filter(currency=currency)

        if date_from:
            payments = payments.filter(created_at__date__gte=date_from)

        if date_to:
            payments = payments.filter(created_at__date__lte=date_to)

        if amount_min:
            payments = payments.filter(amount__gte=amount_min)

        if amount_max:
            payments = payments.filter(amount__lte=amount_max)

    # Статистика
    stats = {
        "total_count": payments.count(),
        "total_amount": payments.filter(status="completed").aggregate(Sum("amount"))["amount__sum"]
        or Decimal("0.00"),
        "pending_count": payments.filter(status="pending").count(),
        "completed_count": payments.filter(status="completed").count(),
        "failed_count": payments.filter(status="failed").count(),
        "refunded_count": payments.filter(status="refunded").count(),
    }

    # Статистика по методам оплаты
    payment_methods_stats = (
        payments.filter(status="completed")
        .values("payment_method")
        .annotate(count=Count("id"), total=Sum("amount"))
        .order_by("-total")
    )

    # Статистика по валютам
    currency_stats = (
        payments.filter(status="completed")
        .values("currency")
        .annotate(count=Count("id"), total=Sum("amount"))
        .order_by("-total")
    )

    # Пагинация
    paginator = Paginator(payments, 20)
    page = request.GET.get("page")

    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # Логирование
    logger.info(
        f"Manager {request.user.email} viewed payments list (page {page_obj.number}, filters: {dict(request.GET)})"
    )

    return render(
        request,
        "managers/payments/payments_list.html",
        {
            "page_obj": page_obj,
            "filter_form": filter_form,
            "stats": stats,
            "payment_methods_stats": payment_methods_stats,
            "currency_stats": currency_stats,
            "total_count": stats["total_count"],
        },
    )


@login_required
@require_any_role(["manager"], redirect_url="/")
def payment_detail_view(request: HttpRequest, user_uuid, payment_id) -> HttpResponse:
    """Детальная информация о платеже."""
    payment = get_object_or_404(Payment.objects.select_related("user", "course"), id=payment_id)

    logger.info(f"Manager {request.user.email} viewed payment {payment_id} details")

    return render(
        request,
        "managers/payments/payment_detail.html",
        {
            "payment": payment,
        },
    )


@login_required
@require_any_role(["manager"], redirect_url="/")
def payment_refund_view(request: HttpRequest, user_uuid, payment_id) -> HttpResponse:
    """Оформление возврата средств."""
    payment = get_object_or_404(Payment, id=payment_id)

    # Проверка возможности возврата
    if payment.status not in ["completed"]:
        messages.error(request, "Возврат возможен только для завершенных платежей")
        return redirect("managers:payment_detail", user_uuid, payment_id)

    if request.method == "POST":
        form = PaymentRefundForm(request.POST)
        if form.is_valid():
            refund_amount = form.cleaned_data["refund_amount"]
            refund_reason = form.cleaned_data["refund_reason"]

            # Проверка суммы
            if refund_amount > payment.amount:
                messages.error(request, "Сумма возврата не может превышать сумму платежа")
                return render(
                    request,
                    "managers/payments/payment_refund.html",
                    {"payment": payment, "form": form},
                )

            # Оформление возврата
            payment.status = "refunded"
            payment.updated_at = timezone.now()
            payment.extra_data = payment.extra_data or {}
            payment.extra_data["refund"] = {
                "amount": float(refund_amount),
                "reason": refund_reason,
                "processed_by": request.user.email,
                "processed_at": timezone.now().isoformat(),
            }
            payment.save()

            # Логирование
            create_system_log(
                level="WARNING",
                action_type="PAYMENT_PROCESSED",
                message=f"Возврат платежа {payment.transaction_id} на сумму {refund_amount} {payment.currency}",
                request=request,
                details={
                    "payment_id": str(payment.id),
                    "refund_amount": float(refund_amount),
                    "refund_reason": refund_reason,
                    "transaction_id": payment.transaction_id,
                },
            )

            messages.success(
                request, f"Возврат на сумму {refund_amount} {payment.currency} успешно оформлен"
            )
            logger.info(
                f"Manager {request.user.email} refunded payment {payment_id}: {refund_amount} {payment.currency}"
            )

            return redirect("managers:payment_detail", user_uuid, payment_id)
    else:
        form = PaymentRefundForm(initial={"refund_amount": payment.amount})

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
def payments_reports_view(request: HttpRequest, user_uuid) -> HttpResponse:
    """Отчеты и аналитика по платежам."""
    # Период для отчета (по умолчанию последние 30 дней)
    days = int(request.GET.get("days", 30))
    date_from = timezone.now() - timedelta(days=days)

    payments = Payment.objects.filter(created_at__gte=date_from)

    # Общая статистика
    total_stats = {
        "total_revenue": payments.filter(status="completed").aggregate(Sum("amount"))["amount__sum"]
        or Decimal("0.00"),
        "total_transactions": payments.count(),
        "completed_transactions": payments.filter(status="completed").count(),
        "failed_transactions": payments.filter(status="failed").count(),
        "refunded_amount": payments.filter(status="refunded").aggregate(Sum("amount"))[
            "amount__sum"
        ]
        or Decimal("0.00"),
        "average_transaction": payments.filter(status="completed").aggregate(Avg("amount"))[
            "amount__avg"
        ]
        or Decimal("0.00"),
    }

    # Статистика по датам (последние 30 дней)
    daily_stats = []
    for i in range(days):
        date = (timezone.now() - timedelta(days=i)).date()
        day_payments = payments.filter(created_at__date=date, status="completed")
        daily_stats.append(
            {
                "date": date,
                "count": day_payments.count(),
                "amount": day_payments.aggregate(Sum("amount"))["amount__sum"] or Decimal("0.00"),
            }
        )
    daily_stats.reverse()

    # Топ курсов по доходу
    top_courses = (
        payments.filter(status="completed")
        .values("course__title")
        .annotate(count=Count("id"), revenue=Sum("amount"))
        .order_by("-revenue")[:10]
    )

    # Статистика по методам оплаты
    payment_methods = (
        payments.filter(status="completed")
        .values("payment_method")
        .annotate(count=Count("id"), total=Sum("amount"))
    )

    # Статистика по валютам
    currencies = (
        payments.filter(status="completed")
        .values("currency")
        .annotate(count=Count("id"), total=Sum("amount"))
    )

    logger.info(f"Manager {request.user.email} viewed payments reports ({days} days)")

    return render(
        request,
        "managers/payments/payments_reports.html",
        {
            "days": days,
            "total_stats": total_stats,
            "daily_stats": daily_stats,
            "top_courses": top_courses,
            "payment_methods": payment_methods,
            "currencies": currencies,
        },
    )


@login_required
@require_any_role(["manager"], redirect_url="/")
def payments_export_view(request: HttpRequest, user_uuid) -> HttpResponse:
    """Export платежей в CSV."""
    # Применяем те же фильтры что и в списке
    payments = Payment.objects.select_related("user", "course").order_by("-created_at")

    filter_form = PaymentsFilterForm(request.GET)
    if filter_form.is_valid():
        # Применяем фильтры (тот же код что в payments_list_view)
        search = filter_form.cleaned_data.get("search")
        status = filter_form.cleaned_data.get("status")
        payment_method = filter_form.cleaned_data.get("payment_method")
        currency = filter_form.cleaned_data.get("currency")
        date_from = filter_form.cleaned_data.get("date_from")
        date_to = filter_form.cleaned_data.get("date_to")
        amount_min = filter_form.cleaned_data.get("amount_min")
        amount_max = filter_form.cleaned_data.get("amount_max")

        if search:
            payments = payments.filter(
                Q(transaction_id__icontains=search)
                | Q(user__email__icontains=search)
                | Q(course__title__icontains=search)
            )
        if status:
            payments = payments.filter(status=status)
        if payment_method:
            payments = payments.filter(payment_method=payment_method)
        if currency:
            payments = payments.filter(currency=currency)
        if date_from:
            payments = payments.filter(created_at__date__gte=date_from)
        if date_to:
            payments = payments.filter(created_at__date__lte=date_to)
        if amount_min:
            payments = payments.filter(amount__gte=amount_min)
        if amount_max:
            payments = payments.filter(amount__lte=amount_max)

    # Создаем CSV
    response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
    response["Content-Disposition"] = (
        f'attachment; filename="payments_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    )

    writer = csv.writer(response)
    writer.writerow(
        [
            "ID",
            "Дата",
            "Пользователь",
            "Email",
            "Курс",
            "Сумма",
            "Валюта",
            "Статус",
            "Метод оплаты",
            "ID транзакции",
        ]
    )

    for payment in payments:
        writer.writerow(
            [
                str(payment.id),
                payment.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                payment.user.get_full_name() or payment.user.email,
                payment.user.email,
                payment.course.title,
                float(payment.amount),
                payment.currency,
                payment.get_status_display(),
                payment.get_payment_method_display(),
                payment.transaction_id or "",
            ]
        )

    logger.info(f"Manager {request.user.email} exported {payments.count()} payments to CSV")

    return response
