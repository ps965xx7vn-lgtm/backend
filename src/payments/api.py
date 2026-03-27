"""
Payments API Module - REST API для обработки платежей.

Этот модуль содержит эндпоинты для платежей:

Endpoints:
    POST   /api/payments/create              - Создать платеж
    POST   /api/payments/paddle/checkout     - Создать Paddle checkout
    GET    /api/payments/{id}                - Получить статус платежа
    GET    /api/payments/history             - История платежей пользователя
    POST   /api/payments/paddle/webhook      - Webhook от Paddle
    GET    /api/payments/verify/{id}         - Проверить статус транзакции

Особенности:
    - Интеграция с Paddle Billing
    - JWT аутентификация для защищенных эндпоинтов
    - Валидация webhook событий
    - Автоматическое обновление статусов
    - Логирование всех операций

Автор: Pyland Team
Дата: 2026
"""

import logging
from uuid import UUID

from django.contrib.auth import get_user_model
from django.db import transaction
from ninja import Router

from courses.models import Course
from payments.models import Payment
from payments.paddle_service import get_paddle_service
from payments.schemas import (
    PaddleCheckoutInput,
    PaymentCheckoutOutput,
    PaymentErrorOutput,
    PaymentHistoryOutput,
    PaymentOutput,
    PaymentStatusOutput,
    WebhookResponseOutput,
)

User = get_user_model()
logger = logging.getLogger(__name__)

router = Router(tags=["Payments"])


@router.get("/ping", auth=None)
def ping(request):
    """Проверка доступности сервиса"""
    return {"ping": "pong", "service": "payments"}


@router.post(
    "/paddle/checkout",
    response={200: PaymentCheckoutOutput, 400: PaymentErrorOutput, 500: PaymentErrorOutput},
)
def create_paddle_checkout(request, payload: PaddleCheckoutInput):
    """
    Создать Paddle checkout сессию для оплаты курса.

    Процесс:
    1. Проверяет существование курса
    2. Создает запись Payment в БД
    3. Создает транзакцию в Paddle
    4. Возвращает checkout URL для перенаправления

    Args:
        request: HTTP запрос с JWT токеном
        payload: Данные для создания checkout

    Returns:
        PaymentCheckoutOutput: URL для оплаты и данные транзакции

    Raises:
        HttpError: При ошибках валидации или создания
    """
    try:
        user = request.auth

        try:
            course = Course.objects.get(id=payload.course_id)
        except Course.DoesNotExist:
            return 400, {
                "error": "Course not found",
                "details": f"Course with ID {payload.course_id} does not exist",
            }

        if hasattr(user, "student"):
            if course.student_enrollments.filter(id=user.student.id).exists():
                return 400, {
                    "error": "Already enrolled",
                    "details": "User is already enrolled in this course",
                }

        with transaction.atomic():
            payment = Payment.objects.create(
                user=user,
                course=course,
                amount=course.price,
                currency="USD",
                status="pending",
                payment_method="paddle",
            )

        paddle_service = get_paddle_service()

        paddle_data = paddle_service.create_transaction(
            course_id=course.id,
            course_name=course.name,
            amount=course.price,
            currency="USD",
            user_email=user.email,
            user_id=user.id,
        )

        payment.transaction_id = paddle_data["transaction_id"]
        payment.payment_url = paddle_data["checkout_url"]
        payment.extra_data = paddle_data
        payment.save(update_fields=["transaction_id", "payment_url", "extra_data"])

        logger.info(
            f"Paddle checkout создан: payment_id={payment.id}, "
            f"transaction_id={paddle_data['transaction_id']}, user={user.email}"
        )

        return 200, PaymentCheckoutOutput(
            payment_id=payment.id,
            checkout_url=paddle_data["checkout_url"],
            transaction_id=paddle_data["transaction_id"],
            status=paddle_data["status"],
            amount=paddle_data["amount"],
            currency=paddle_data["currency"],
        )

    except Exception as e:
        logger.error(f"Ошибка при создании Paddle checkout: {e}", exc_info=True)
        return 500, {
            "error": "Internal server error",
            "details": str(e),
        }


@router.get("/history", response=PaymentHistoryOutput)
def get_payment_history(request, page: int = 1, page_size: int = 10):
    """
    Получить историю платежей текущего пользователя.

    Args:
        request: HTTP запрос с JWT токеном
        page: Номер страницы (default: 1)
        page_size: Размер страницы (default: 10, max: 100)

    Returns:
        PaymentHistoryOutput: Список платежей с пагинацией
    """
    user = request.auth
    page_size = min(page_size, 100)

    payments_qs = Payment.objects.filter(user=user).select_related("course").order_by("-created_at")

    total_count = payments_qs.count()
    start = (page - 1) * page_size
    end = start + page_size

    payments = payments_qs[start:end]

    payment_outputs = []
    for payment in payments:
        payment_outputs.append(
            PaymentOutput(
                id=payment.id,
                user_email=user.email,
                course_id=payment.course.id,
                course_name=payment.course.name,
                amount=payment.amount,
                currency=payment.currency,
                status=payment.status,
                payment_method=payment.payment_method,
                transaction_id=payment.transaction_id,
                payment_url=payment.payment_url,
                payment_date=payment.payment_date,
                created_at=payment.created_at,
                updated_at=payment.updated_at,
            )
        )

    return PaymentHistoryOutput(
        payments=payment_outputs,
        total_count=total_count,
        page=page,
        page_size=page_size,
    )


@router.get("/{payment_id}", response={200: PaymentStatusOutput, 404: PaymentErrorOutput})
def get_payment_status(request, payment_id: UUID):
    """
    Получить статус платежа из локальной БД (быстро).

    БЫСТРЫЙ МЕТОД: Читает статус только из БД, без запросов к Paddle.

    Когда использовать:
        - Для отображения в UI (списки платежей, история)
        - Когда нужен быстрый ответ
        - Статус обновляется автоматически через webhook

    Когда НЕ использовать:
        - Если webhook не настроен
        - Если нужен 100% актуальный статус из Paddle (используйте /verify)

    Args:
        request: HTTP запрос с JWT токеном
        payment_id: UUID платежа

    Returns:
        PaymentStatusOutput: Статус платежа из БД
    """
    user = request.auth

    try:
        payment = Payment.objects.get(id=payment_id, user=user)

        return 200, PaymentStatusOutput(
            id=payment.id,
            status=payment.status,
            transaction_id=payment.transaction_id,
            payment_date=payment.payment_date,
        )
    except Payment.DoesNotExist:
        return 404, {
            "error": "Payment not found",
            "details": f"Payment with ID {payment_id} not found for current user",
            "payment_id": payment_id,
        }


@router.get("/verify/{payment_id}", response={200: PaymentStatusOutput, 404: PaymentErrorOutput})
def verify_payment(request, payment_id: UUID):
    """
    Синхронизировать статус платежа с Paddle API (медленный, точный).

    ПРИНУДИТЕЛЬНАЯ СИНХРОНИЗАЦИЯ: Делает запрос к Paddle API и обновляет БД.

    РЕДКОЕ ИСПОЛЬЗОВАНИЕ: Обычно не нужен - есть автоматизация через:
        - Webhook (основной способ) - мгновенное обновление
        - Celery task (каждые 30 мин) - автоматическая проверка зависших платежей

    Когда использовать (очень редко):
        - Admin/Support: Отладка конкретного проблемного платежа
        - Development: Ручная проверка в sandbox режиме
        - Customer support: Клиент звонит что оплата не прошла
        - Emergency: Webhook не работает И Celery task еще не отработал

    Когда НЕ использовать (почти всегда):
        - Для частых проверок (есть rate limits Paddle API)
        - В UI для обычных пользователей (используйте GET /{id})
        - В циклах или batch операциях (используйте Celery task)
        - Для мониторинга (используйте Celery task + метрики)

    Альтернативы (используйте их вместо):
        1. GET /api/payments/{id} - быстрая проверка из БД
        2. Celery task - автоматическая проверка каждые 30 мин
        3. Webhook - мгновенное асинхронное обновление

    Workflow:
        1. Запрашивает transaction status из Paddle API (~500-2000ms)
        2. Сравнивает с локальным статусом
        3. Обновляет БД если различается
        4. Логирует расхождения для мониторинга

    Args:
        request: HTTP запрос с JWT токеном (admin/support)
        payment_id: UUID платежа для проверки

    Returns:
        PaymentStatusOutput: Актуальный статус из Paddle API

    Example (Admin/Support only):
        ```bash
        # Отладка конкретного платежа
        curl -X GET "https://api.pyland.com/api/payments/verify/{payment_id}" \
          -H "Authorization: Bearer {admin_jwt_token}"
        ```
    """
    user = request.auth

    try:
        payment = Payment.objects.get(id=payment_id, user=user)

        if not payment.transaction_id:
            return 404, {
                "error": "No transaction ID",
                "details": "Payment does not have a Paddle transaction ID",
                "payment_id": payment_id,
            }

        paddle_service = get_paddle_service()
        paddle_data = paddle_service.get_transaction(payment.transaction_id)

        paddle_status = paddle_data["status"]
        if paddle_status == "completed":
            payment.mark_as_completed()
        elif paddle_status == "failed" or paddle_status == "canceled":
            payment.mark_as_failed("Transaction failed or canceled in Paddle")

        logger.info(f"Payment {payment_id} verified with Paddle: status={paddle_status}")

        return 200, PaymentStatusOutput(
            id=payment.id,
            status=payment.status,
            transaction_id=payment.transaction_id,
            payment_date=payment.payment_date,
        )

    except Payment.DoesNotExist:
        return 404, {
            "error": "Payment not found",
            "details": f"Payment with ID {payment_id} not found",
            "payment_id": payment_id,
        }
    except Exception as e:
        logger.error(f"Ошибка при верификации платежа {payment_id}: {e}", exc_info=True)
        return 500, {
            "error": "Verification failed",
            "details": str(e),
            "payment_id": payment_id,
        }


@router.post("/paddle/webhook", auth=None, response=WebhookResponseOutput)
def paddle_webhook(request):
    """
    Webhook endpoint для автоматических уведомлений от Paddle (ОСНОВНОЙ СПОСОБ).

    АВТОМАТИЧЕСКОЕ ОБНОВЛЕНИЕ: Paddle вызывает этот endpoint при изменении статуса.

    Как работает:
        1. Paddle отправляет событие (transaction.completed, payment_failed и т.д.)
        2. Проверяется подпись Paddle-Signature (защита от подделок)
        3. Обновляется статус платежа в БД
        4. Возвращается 200 OK для Paddle

    События обрабатываются:
        - transaction.completed → payment.mark_as_completed()
        - transaction.payment_failed → payment.mark_as_failed()

    Настройка в Paddle Dashboard:
        1. Settings → Webhooks → Add endpoint
        2. URL: https://yoursite.com/api/payments/paddle/webhook
        3. Events: transaction.completed, transaction.payment_failed
        4. Secret: копируете в PADDLE_WEBHOOK_SECRET в .env

    Отличия от других endpoints:
        - auth=None (без JWT, вызывается Paddle'ом)
        - Проверка Paddle-Signature вместо JWT
        - Асинхронный (не ждет пользователь)
        - Идемпотентный (можно вызывать много раз)

    Security:
        ✅ Webhook signature verification (Paddle-Signature header)
        ✅ Only Paddle IP addresses should reach this endpoint
        ✅ HTTPS required in production

    Args:
        request: HTTP запрос от Paddle с подписью и телом события

    Returns:
        WebhookResponseOutput: Результат обработки для Paddle
    """
    try:
        signature = request.headers.get("paddle-signature", "")

        if not signature:
            logger.warning("Webhook получен без Paddle-Signature")
            return WebhookResponseOutput(
                success=False,
                message="Missing Paddle-Signature header",
            )

        paddle_service = get_paddle_service()
        event_data = paddle_service.verify_webhook(request.body, signature)

        if not event_data:
            logger.warning("Webhook верификация не прошла")
            return WebhookResponseOutput(
                success=False,
                message="Webhook verification failed",
            )

        event_type = event_data["event_type"]
        transaction_data = event_data["data"]

        logger.info(f"Paddle webhook получен: {event_type}")

        if event_type == "transaction.completed":
            transaction_id = transaction_data.get("id")

            try:
                payment = Payment.objects.get(transaction_id=transaction_id)
                payment.mark_as_completed()
                logger.info(f"Payment {payment.id} marked as completed via webhook")

            except Payment.DoesNotExist:
                logger.error(f"Payment not found for transaction_id: {transaction_id}")

        elif event_type == "transaction.payment_failed":
            transaction_id = transaction_data.get("id")

            try:
                payment = Payment.objects.get(transaction_id=transaction_id)
                payment.mark_as_failed("Payment failed in Paddle")
                logger.info(f"Payment {payment.id} marked as failed via webhook")

            except Payment.DoesNotExist:
                logger.error(f"Payment not found for transaction_id: {transaction_id}")

        return WebhookResponseOutput(
            success=True,
            message="Webhook processed successfully",
            event_type=event_type,
        )

    except Exception as e:
        logger.error(f"Ошибка при обработке Paddle webhook: {e}", exc_info=True)
        return WebhookResponseOutput(
            success=False,
            message=f"Internal error: {str(e)}",
        )
