"""
Celery tasks для приложения платежей.

Фоновые задачи для обновления курсов валют, обработки платежей и синхронизации.
"""

import logging

from celery import shared_task

from payments.currency_service import get_currency_service

logger = logging.getLogger(__name__)


@shared_task(name="payments.update_currency_rates")
def update_currency_rates_task():
    """
    Периодическая задача для автоматического обновления курсов валют.

    Запускается каждый час через Celery Beat для гарантии актуальных курсов.
    При ошибке API автоматически использует fallback курсы.

    Логика:
        1. Получает singleton instance CurrencyService
        2. Инвалидирует старый кэш
        3. Запрашивает свежие курсы из API
        4. Кэширует на 1 час
        5. Логирует результат

    Returns:
        str: Статус выполнения задачи

    Examples:
        >>> # Вызов вручную из Django shell
        >>> from payments.tasks import update_currency_rates_task
        >>> result = update_currency_rates_task.delay()
        >>> result.get()
        "Currency rates updated: USD=1.00, EUR=0.9234, RUB=92.34, GEL=2.68"
    """
    try:
        currency_service = get_currency_service()

        # Инвалидируем старый кэш для принудительного обновления
        currency_service.invalidate_cache()
        logger.info("Запущено автоматическое обновление курсов валют (Celery Beat)")

        # Получаем свежие курсы (будет запрос к API)
        rates = currency_service.get_exchange_rates(base_currency="USD")

        # Форматируем курсы для логирования
        rates_str = ", ".join([f"{currency}={float(rate):.4f}" for currency, rate in rates.items()])

        logger.info(f"✅ Курсы валют автоматически обновлены через Celery: {rates_str}")

        return f"Currency rates updated: {rates_str}"

    except Exception as e:
        error_msg = f"Ошибка при автоматическом обновлении курсов валют: {e}"
        logger.error(error_msg)
        return f"Error: {str(e)}"


@shared_task(name="payments.check_pending_payments")
def check_pending_payments_task():
    """
    Периодическая задача для проверки "зависших" платежей (автоматизация /verify).

    🤖 АВТОМАТИЧЕСКАЯ ПРОВЕРКА вместо ручного /verify endpoint.

    Что делает:
        1. Находит Payment со status='processing' старше 30 минут
        2. Для каждого делает запрос к Paddle API
        3. Обновляет статус если изменился
        4. Логирует расхождения

    Когда запускается:
        - Каждые 30 минут через Celery Beat
        - Или вручную: check_pending_payments_task.delay()

    Зачем нужно:
        - Webhook может не дойти (сеть, таймауты)
        - Гарантия что ни один платеж не "зависнет"
        - Альтернатива ручному /verify для каждого платежа

    Returns:
        dict: Статистика обработки

    Example:
        >>> from payments.tasks import check_pending_payments_task
        >>> result = check_pending_payments_task.delay()
        >>> result.get()
        {"checked": 5, "updated": 2, "errors": 0}
    """
    from datetime import timedelta

    from django.utils import timezone

    from payments.models import Payment
    from payments.paddle_service import get_paddle_service

    try:
        # Ищем платежи в статусе processing старше 30 минут
        threshold = timezone.now() - timedelta(minutes=30)
        stuck_payments = Payment.objects.filter(
            status="processing", created_at__lt=threshold
        ).exclude(transaction_id__isnull=True)

        count = stuck_payments.count()

        if count == 0:
            logger.info("✅ Проверка платежей: все актуальны, зависших нет")
            return {"checked": 0, "updated": 0, "errors": 0}

        logger.warning(f"⚠️ Найдено {count} платежей со статусом 'processing' старше 30 минут")

        paddle_service = get_paddle_service()
        updated_count = 0
        error_count = 0

        for payment in stuck_payments:
            try:
                # Запрос к Paddle API
                paddle_data = paddle_service.get_transaction(payment.transaction_id)
                paddle_status = paddle_data.get("status")

                # Проверяем нужно ли обновить
                if paddle_status == "completed" and payment.status != "completed":
                    payment.mark_as_completed()
                    updated_count += 1
                    logger.info(
                        f"✅ Payment {payment.id} обновлен: processing → completed "
                        f"(автоматически через Celery task)"
                    )

                elif paddle_status in ["failed", "canceled"] and payment.status != "failed":
                    payment.mark_as_failed(f"Transaction {paddle_status} in Paddle")
                    updated_count += 1
                    logger.info(
                        f"❌ Payment {payment.id} обновлен: processing → failed "
                        f"(автоматически через Celery task)"
                    )

                else:
                    logger.debug(f"Payment {payment.id} статус не изменился: {paddle_status}")

            except Exception as e:
                error_count += 1
                logger.error(f"Ошибка при проверке payment {payment.id}: {e}", exc_info=True)

        result = {"checked": count, "updated": updated_count, "errors": error_count}

        logger.info(
            f"✅ Проверка платежей завершена: "
            f"проверено={count}, обновлено={updated_count}, ошибок={error_count}"
        )

        return result

    except Exception as e:
        error_msg = f"Критическая ошибка при проверке платежей: {e}"
        logger.error(error_msg, exc_info=True)
        return {"checked": 0, "updated": 0, "errors": 1, "error": str(e)}
