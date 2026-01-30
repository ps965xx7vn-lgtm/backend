"""
Payments Views Module - Django views для обработки платежей.

Этот модуль содержит представления для покупки курсов через
CloudPayments (РФ) и TBC Bank (Грузия).

Представления:
    - checkout_view: Страница оформления платежа с выбором метода оплаты
    - payment_success_view: Страница успешной оплаты
    - payment_cancel_view: Страница отмены оплаты

Особенности:
    - Требуется авторизация (@login_required)
    - Отображение деталей курса и цены в разных валютах
    - Валидация данных через CheckoutForm
    - Создание записи Payment в БД
    - Подготовка данных для перенаправления на платежные системы
    - Обработка callback от платежных систем

Будущие улучшения:
    - Интеграция API CloudPayments
    - Интеграция API TBC Bank
    - Webhook обработчики для подтверждения платежей
    - История платежей пользователя
    - Возвраты и отмены

Автор: Pyland Team
Дата: 2025
"""

from __future__ import annotations

import logging
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext
from django.utils.translation import gettext as _
from django.views.decorators.http import require_http_methods

from courses.models import Course

from .forms import CheckoutForm
from .models import Payment

logger = logging.getLogger(__name__)


# Курсы валют для конвертации (можно вынести в settings или получать из API)
EXCHANGE_RATES: dict[str, Decimal] = {
    "USD": Decimal("1.00"),
    "GEL": Decimal("2.65"),  # 1 USD = 2.65 GEL (примерный курс)
    "RUB": Decimal("90.00"),  # 1 USD = 90 RUB (примерный курс)
}


def convert_currency(amount: Decimal, from_currency: str, to_currency: str) -> Decimal:
    """
    Конвертировать сумму из одной валюты в другую.

    Args:
        amount: Исходная сумма
        from_currency: Исходная валюта
        to_currency: Целевая валюта

    Returns:
        Decimal: Сконвертированная сумма
    """
    if from_currency == to_currency:
        return amount

    # Конвертируем через USD как базовую валюту
    usd_amount = amount / EXCHANGE_RATES[from_currency]
    result = usd_amount * EXCHANGE_RATES[to_currency]

    return result.quantize(Decimal("0.01"))


@login_required
@require_http_methods(["GET", "POST"])
def checkout_view(request: HttpRequest, course_slug: str) -> HttpResponse:
    """
    Представление для страницы оформления оплаты курса.

    GET: Отображает форму выбора метода оплаты и условия.
    POST: Обрабатывает выбор метода оплаты, создаёт Payment,
          перенаправляет на страницу платежной системы.

    Args:
        request: HTTP-запрос пользователя
        course_slug: Slug курса для покупки

    Returns:
        HttpResponse: Страница checkout или редирект на оплату
    """
    # Разрешаем покупку курсов со статусом active и published
    # Исключаем draft, archived, coming_soon
    course = get_object_or_404(Course, slug=course_slug, status__in=["active", "published"])

    # Проверяем, не купил ли уже пользователь этот курс
    try:
        student = request.user.student
        # Используем правильный related_name из модели Student
        if course.student_enrollments.filter(id=student.id).exists():
            messages.info(request, gettext("Вы уже записаны на этот курс"))
            return redirect("courses:course_detail", course_slug=course_slug)
    except Exception as e:
        logger.error(f"Ошибка проверки enrollment: {e}")

    # Проверяем наличие незавершенных платежей
    pending_payment = Payment.objects.filter(
        user=request.user, course=course, status="pending"
    ).first()

    if request.method == "POST":
        form = CheckoutForm(request.POST)

        if form.is_valid():
            payment_method = form.cleaned_data["payment_method"]
            currency = form.cleaned_data["currency"]

            # Конвертируем цену курса в выбранную валюту
            course_price_usd = course.price
            amount = convert_currency(course_price_usd, "USD", currency)

            # Создаём или обновляем платеж
            if pending_payment:
                payment = pending_payment
                payment.payment_method = payment_method
                payment.currency = currency
                payment.amount = amount
                payment.status = "processing"
                payment.save()
                logger.info(f"Обновлён существующий платеж {payment.id}")
            else:
                payment = Payment.objects.create(
                    user=request.user,
                    course=course,
                    amount=amount,
                    currency=currency,
                    payment_method=payment_method,
                    status="processing",
                )
                logger.info(f"Создан новый платеж {payment.id} на сумму {amount} {currency}")

            # TODO: Здесь будет интеграция с платежными системами
            # Пока просто перенаправляем на страницу успеха (для разработки)
            messages.success(
                request,
                gettext(
                    "Платёж создан. В продакшене здесь будет перенаправление "
                    "на страницу платежной системы."
                ),
            )

            # В продакшене здесь будет редирект на payment.payment_url
            # return redirect(payment.payment_url)

            # Для разработки показываем информацию о платеже
            return render(
                request,
                "payments/payment_processing.html",
                {
                    "payment": payment,
                    "course": course,
                },
            )

        else:
            messages.error(request, _("Пожалуйста, исправьте ошибки в форме"))

    else:
        form = CheckoutForm()

    # Подготавливаем цены в разных валютах для отображения
    prices_in_currencies = {}
    course_price_usd = course.price

    for currency_code, currency_label in Payment.CURRENCY_CHOICES:
        prices_in_currencies[currency_code] = convert_currency(
            course_price_usd, "USD", currency_code
        )

    context = {
        "course": course,
        "form": form,
        "prices": prices_in_currencies,
        "pending_payment": pending_payment,
    }

    return render(request, "payments/checkout.html", context)


@login_required
def payment_success_view(request: HttpRequest, payment_id: str) -> HttpResponse:
    """
    Страница успешной оплаты.

    Args:
        request: HTTP-запрос
        payment_id: UUID платежа

    Returns:
        HttpResponse: Страница с информацией об успешной оплате
    """
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)

    # Обновляем статус если пришли с платежной системы
    if payment.status == "processing":
        payment.mark_as_completed()
        messages.success(
            request,
            _("Оплата успешно завершена! Вы зачислены на курс {course}").format(
                course=payment.course.name
            ),
        )

    return render(
        request,
        "payments/payment_success.html",
        {
            "payment": payment,
            "course": payment.course,
        },
    )


@login_required
def payment_cancel_view(request: HttpRequest, payment_id: str) -> HttpResponse:
    """
    Страница отмены оплаты.

    Args:
        request: HTTP-запрос
        payment_id: UUID платежа

    Returns:
        HttpResponse: Страница с информацией об отмене
    """
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)

    if payment.status in ["pending", "processing"]:
        payment.status = "cancelled"
        payment.save()
        logger.info(f"Платеж {payment.id} отменён пользователем")

    messages.info(request, _("Оплата отменена"))

    return render(
        request,
        "payments/payment_cancel.html",
        {
            "payment": payment,
            "course": payment.course,
        },
    )
