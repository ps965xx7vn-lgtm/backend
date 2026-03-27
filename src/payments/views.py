"""
Payments Views Module - Django views для обработки платежей через Paddle Billing.

Этот модуль содержит представления для покупки курсов через Paddle.

Представления:
    - checkout_view: Страница оформления платежа и создание Paddle transaction
    - payment_success_view: Страница успешной оплаты
    - payment_cancel_view: Страница отмены оплаты
    - paddle_checkout_handler: Обработчик для Paddle Retain (_ptxn параметр)

Особенности:
    - Требуется авторизация (@login_required)
    - Интеграция с Paddle Billing API через paddle_service
    - Автоматическое создание customer, product, price в Paddle
    - Paddle.js overlay checkout для оплаты
    - Webhook обработчики для подтверждения платежей (в API модуле)
    - Автоматическое зачисление на курс после оплаты

Автор: Pyland Team
Дата: 2026
"""

from __future__ import annotations

import logging
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext
from django.utils.translation import gettext as _
from django.views.decorators.http import require_http_methods

from courses.models import Course

from .currency_service import get_currency_service
from .forms import CheckoutForm
from .models import Payment
from .paddle_service import get_paddle_service

logger = logging.getLogger(__name__)


def convert_currency(amount: Decimal, from_currency: str, to_currency: str) -> Decimal:
    """
    Конвертировать сумму из одной валюты в другую.

    Использует динамические курсы валют из CurrencyService.
    Автоматически обновляется каждый час.
    При ошибке использует fallback статичные курсы.

    Args:
        amount: Исходная сумма
        from_currency: Исходная валюта
        to_currency: Целевая валюта

    Returns:
        Decimal: Сконвертированная сумма
    """
    currency_service = get_currency_service()
    return currency_service.convert_currency(amount, from_currency, to_currency)


@login_required
@require_http_methods(["GET", "POST"])
def checkout_view(request: HttpRequest, course_slug: str) -> HttpResponse:
    """
    Представление для страницы оформления оплаты курса.

    GET: Отображает форму выбора метода оплаты и условия.
    POST: Обрабатывает выбор метода оплаты, создаёт Payment,
          перенаправляет на страницу платежной системы.

    Разрешены курсы со статусом active и published.
    Проверяет что студент еще не зачислен на курс.

    Args:
        request: HTTP-запрос пользователя
        course_slug: Slug курса для покупки

    Returns:
        HttpResponse: Страница checkout или редирект на оплату
    """
    course = get_object_or_404(Course, slug=course_slug, status__in=["active", "published"])

    try:
        student = request.user.student
        if course.student_enrollments.filter(id=student.id).exists():
            messages.info(request, gettext("Вы уже записаны на этот курс"))
            return redirect("courses:course_detail", course_slug=course_slug)
    except Exception as e:
        logger.error(f"Ошибка проверки enrollment: {e}")

    pending_payment = Payment.objects.filter(
        user=request.user, course=course, status="pending"
    ).first()

    if request.method == "POST":
        form = CheckoutForm(request.POST)

        if form.is_valid():
            payment_method = form.cleaned_data["payment_method"]
            currency = form.cleaned_data["currency"]

            course_price_usd = course.price
            amount = convert_currency(course_price_usd, "USD", currency)

            if pending_payment:
                payment = pending_payment
                payment.payment_method = payment_method
                payment.currency = currency
                payment.amount = amount
                payment.status = "pending"
                payment.save()
                logger.info(f"Обновлён существующий платеж {payment.id}")
            else:
                payment = Payment.objects.create(
                    user=request.user,
                    course=course,
                    amount=amount,
                    currency=currency,
                    payment_method=payment_method,
                    status="pending",
                )
                logger.info(f"Создан новый платеж {payment.id} на сумму {amount} {currency}")

            if payment_method == "paddle":
                try:
                    success_url = request.build_absolute_uri(
                        reverse("payments:payment_success", kwargs={"payment_id": payment.id})
                    )
                    cancel_url = request.build_absolute_uri(
                        reverse("payments:payment_cancel", kwargs={"payment_id": payment.id})
                    )

                    logger.info(
                        f"Создание Paddle checkout для платежа {payment.id}, "
                        f"курс: {course.name}, сумма: {amount} {currency}"
                    )

                    paddle_service = get_paddle_service()
                    paddle_data = paddle_service.create_transaction(
                        course_id=course.id,
                        course_name=course.name,
                        amount=amount,
                        currency=currency,
                        user_email=request.user.email,
                        user_id=request.user.id,
                        success_url=success_url,
                        cancel_url=cancel_url,
                    )

                    # Проверяем что paddle_data это dict и имеет нужные ключи
                    if not isinstance(paddle_data, dict) or "transaction_id" not in paddle_data:
                        raise ValueError("Invalid paddle_data format")

                    payment.transaction_id = paddle_data["transaction_id"]
                    payment.payment_url = f"paddle://transaction/{paddle_data['transaction_id']}"
                    payment.extra_data = paddle_data
                    payment.status = "processing"
                    payment.save(
                        update_fields=[
                            "transaction_id",
                            "payment_url",
                            "extra_data",
                            "status",
                        ]
                    )

                    client_token = paddle_data.get("client_token")
                    token_preview = str(client_token)[:20] if client_token else "Not created"

                    logger.info(
                        f"Paddle checkout создан для платежа {payment.id}, "
                        f"transaction_id: {paddle_data['transaction_id']}, "
                        f"client_token: {token_preview}..."
                    )

                    context = {
                        "transaction_id": str(paddle_data["transaction_id"]),
                        "client_token": paddle_data.get("client_token"),
                        "paddle_env": settings.PADDLE_ENVIRONMENT.lower(),
                        "success_url": success_url,
                        "cancel_url": cancel_url,
                        "course": course,
                        "payment": payment,
                    }

                    logger.info(
                        f"Открываем Paddle.js checkout для транзакции: {paddle_data['transaction_id']}"
                    )

                    return render(request, "payments/paddle_redirect.html", context)

                except Exception as e:
                    logger.error(
                        f"Ошибка создания Paddle checkout для платежа {payment.id}: {e}",
                        exc_info=True,
                    )
                    messages.error(
                        request,
                        _(
                            "Произошла ошибка при создании платежа: {error}. "
                            "Пожалуйста, попробуйте снова или выберите другой способ оплаты."
                        ).format(error=str(e)),
                    )
                    payment.status = "failed"
                    payment.save(update_fields=["status"])
                    return redirect("payments:checkout", course_slug=course_slug)

            else:
                logger.error(f"Неизвестный метод оплаты: {payment_method}")
                messages.error(
                    request,
                    _("Выбран неподдерживаемый метод оплаты. Пожалуйста, используйте Paddle."),
                )
                payment.status = "failed"
                payment.save(update_fields=["status"])
                return redirect("payments:checkout", course_slug=course_slug)

        else:
            messages.error(request, _("Пожалуйста, исправьте ошибки в форме"))

    else:
        form = CheckoutForm()

    prices_in_currencies = {}
    course_price_usd = course.price

    for currency_code, _currency_label in Payment.CURRENCY_CHOICES:
        prices_in_currencies[currency_code] = convert_currency(
            course_price_usd, "USD", currency_code
        )

    # Подсчет количества уроков и шагов
    lessons_count = course.lessons.count()
    steps_count = sum(lesson.steps.count() for lesson in course.lessons.all())

    context = {
        "course": course,
        "form": form,
        "prices": prices_in_currencies,
        "pending_payment": pending_payment,
        "lessons_count": lessons_count,
        "steps_count": steps_count,
    }

    return render(request, "payments/checkout.html", context)


@login_required
def payment_success_view(request: HttpRequest, payment_id: str) -> HttpResponse:
    """
    Страница успешной оплаты.

    Обрабатывает возврат пользователя после оплаты.

    Для Paddle: статус обновляется через webhook асинхронно,
    здесь только показываем статус и информируем пользователя.

    Для других методов: может обновлять статус напрямую.

    Args:
        request: HTTP-запрос
        payment_id: UUID платежа

    Returns:
        HttpResponse: Страница с информацией об успешной оплате
    """
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)

    if payment.status == "processing":
        if settings.PADDLE_ENVIRONMENT == "sandbox":
            logger.info(
                f"Sandbox режим: автоматически завершаем платёж {payment.id} "
                f"и зачисляем на курс {payment.course.name}"
            )
            payment.mark_as_completed()
            messages.success(
                request,
                _("Оплата успешно завершена! Вы зачислены на курс {course}").format(
                    course=payment.course.name
                ),
            )
        else:
            messages.info(
                request,
                _(
                    "Платеж обрабатывается. Вы получите уведомление когда "
                    "оплата будет подтверждена и вы будете зачислены на курс."
                ),
            )
    elif payment.status == "completed":
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


def paddle_checkout_handler(request: HttpRequest) -> HttpResponse:
    """
    Обработчик Paddle checkout с параметром _ptxn.

    Этот view показывает страницу с Paddle.js который автоматически
    открывает checkout для транзакции.

    Используется как Default Payment Link в Paddle Dashboard.

    Args:
        request: HTTP-запрос с параметром _ptxn

    Returns:
        HttpResponse: Страница с Paddle checkout
    """
    transaction_id = request.GET.get("_ptxn")

    if not transaction_id:
        messages.error(request, _("Отсутствует ID транзакции"))
        return redirect("core:home")

    logger.info(f"Paddle checkout handler вызван для transaction {transaction_id}")

    from django.conf import settings

    try:
        payment = Payment.objects.get(transaction_id=transaction_id)
        success_url = request.build_absolute_uri(
            reverse("payments:payment_success", kwargs={"payment_id": payment.id})
        )
        cancel_url = request.build_absolute_uri(
            reverse("payments:payment_cancel", kwargs={"payment_id": payment.id})
        )
    except Payment.DoesNotExist:
        logger.warning(f"Payment не найден для transaction {transaction_id}")
        success_url = request.build_absolute_uri("/")
        cancel_url = request.build_absolute_uri("/")

    return render(
        request,
        "payments/paddle_redirect.html",
        {
            "transaction_id": transaction_id,
            "paddle_env": settings.PADDLE_ENVIRONMENT,
            "success_url": success_url,
            "cancel_url": cancel_url,
        },
    )
