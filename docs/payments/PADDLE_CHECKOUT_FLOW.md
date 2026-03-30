# Paddle Checkout Integration - User Flow

## Описание

После интеграции Paddle пользователи теперь **сразу перенаправляются** на страницу оплаты Paddle без ожидания обработки. Webhook обрабатывает результат платежа асинхронно.

## Обновленный Flow

### 1. Пользователь выбирает курс

```
GET /ru/courses/<slug>/
```

Нажимает кнопку "Купить курс"

### 2. Checkout страница

```
GET /ru/payments/checkout/<slug>/
```

Пользователь:
- Выбирает метод оплаты: **BOG / TBC / Paddle**
- Выбирает валюту: USD / GEL / RUB
- Принимает условия

### 3. Создание платежа

```
POST /ru/payments/checkout/<slug>/
```

**Для Paddle:**
1. Создается запись `Payment` со статусом `pending`
2. Вызывается `PaddleService.create_transaction()`
3. Получается `checkout_url` от Paddle
4. **Пользователь сразу перенаправляется на Paddle** (нет ожидания!)

```python
# views.py - checkout_view
return redirect(paddle_data["checkout_url"])
```

### 4. Оплата на Paddle

Пользователь:
- Вводит данные карты на защищенной странице Paddle
- Завершает оплату
- Paddle возвращает пользователя на:
  - **Success URL:** `/ru/payments/success/{payment_id}/`
  - **Cancel URL:** `/ru/payments/cancel/{payment_id}/`

### 5. Success страница

```
GET /ru/payments/success/{payment_id}/
```

**Для Paddle платежей:**
- Показывает сообщение: "Платеж обрабатывается. Вы получите уведомление..."
- Статус: `processing` (пока webhook не обработан)
- НЕ зачисляет на курс сразу

**Для других методов (BOG/TBC):**
- Сразу помечает как `completed`
- Зачисляет на курс

### 6. Webhook обработка (асинхронно)

```
POST /api/payments/paddle/webhook (от Paddle)
```

Paddle отправляет событие `transaction.completed`:
1. Верифицируется signature
2. Находится Payment по `transaction_id`
3. Вызывается `payment.mark_as_completed()`
4. Статус обновляется на `completed`
5. **Пользователь зачисляется на курс**

---

## Преимущества нового подхода

### ✅ Быстрое перенаправление
Пользователь не ждет на странице - сразу попадает на Paddle checkout

### ✅ Асинхронная обработка
Webhook обрабатывает результат независимо от пользователя

### ✅ Надежность
Даже если пользователь закрыл страницу, webhook обновит статус

### ✅ Безопасность
Webhook верифицируется через HMAC SHA256 signature

---

## Тестирование

### 1. Локальный тест (без реальной оплаты)

```bash
# Запустить сервер
cd /Users/dmitrii/Documents/GitHub/pyschool_delete_css/backend/src
poetry run python manage.py runserver

# Открыть checkout
open http://127.0.0.1:8000/ru/payments/checkout/docker/
```

**Шаги:**
1. Залогиньтесь (если еще нет)
2. Выберите "Paddle" как метод оплаты
3. Выберите валюту (USD/GEL/RUB)
4. Нажмите "Оплатить"
5. **Вы будете перенаправлены на Paddle Sandbox**

### 2. Тест на Paddle Sandbox

**Тестовая карта:**
- Номер: `4242 4242 4242 4242`
- CVV: `123`
- Дата: любая будущая (например, 12/28)
- Имя: любое

После оплаты вернетесь на success страницу.

### 3. Проверка webhook (локально с ngrok)

```bash
# Установка ngrok
brew install ngrok

# Запуск ngrok
ngrok http 8000

# Полученный URL использовать в Paddle Dashboard
# Пример: https://abc123.ngrok.io/api/payments/paddle/webhook
```

**В Paddle Dashboard:**
1. Developer Tools → Notifications
2. Добавить Notification Destination
3. URL: `https://your-ngrok-url.ngrok.io/api/payments/paddle/webhook`
4. События: `transaction.completed`, `transaction.payment_failed`

---

## Статусы платежей

| Статус | Когда устанавливается | Описание |
|--------|----------------------|----------|
| `pending` | При создании Payment | Платеж создан, ждет оплаты |
| `processing` | После создания checkout в Paddle | Пользователь перенаправлен на оплату |
| `completed` | После webhook от Paddle | Оплата подтверждена, пользователь зачислен |
| `failed` | Ошибка создания или webhook | Платеж не прошел |
| `cancelled` | Пользователь отменил | Возврат с cancel_url |

---

## Что изменилось в коде

### views.py - checkout_view

**Было:**
```python
# TODO: Здесь будет интеграция с платежными системами
return render(request, "payments/payment_processing.html", ...)
```

**Стало:**
```python
if payment_method == "paddle":
    paddle_service = get_paddle_service()
    paddle_data = paddle_service.create_transaction(...)
    payment.transaction_id = paddle_data["transaction_id"]
    payment.payment_url = paddle_data["checkout_url"]
    payment.save()

    # Сразу перенаправляем на Paddle
    return redirect(paddle_data["checkout_url"])
```

### views.py - payment_success_view

**Было:**
```python
if payment.status == "processing":
    payment.mark_as_completed()  # Всегда для всех
```

**Стало:**
```python
if payment.payment_method == "paddle":
    # Для Paddle - ждем webhook
    messages.info("Платеж обрабатывается...")
else:
    # Для других - сразу completed
    payment.mark_as_completed()
```

---

## URL Configuration

Все URLs уже настроены:

```python
# payments/urls.py
urlpatterns = [
    path("checkout/<slug:course_slug>/", views.checkout_view),
    path("success/<uuid:payment_id>/", views.payment_success_view),
    path("cancel/<uuid:payment_id>/", views.payment_cancel_view),
]
```

Success и Cancel URLs формируются автоматически:
```python
success_url = request.build_absolute_uri(
    reverse("payments:payment_success", kwargs={"payment_id": payment.id})
)
```

---

## Troubleshooting

### Проблема: Ошибка при создании checkout

**Решение:**
- Проверьте `.env` - `PADDLE_SANDBOX_API_KEY` установлен
- Проверьте `PADDLE_ENVIRONMENT='sandbox'`
- Посмотрите логи Django

### Проблема: Webhook не приходит

**Решение:**
- Убедитесь что webhook URL доступен извне (не localhost)
- Используйте ngrok для локальной разработки
- Проверьте `PADDLE_WEBHOOK_SECRET` в `.env`
- Посмотрите логи webhook в Paddle Dashboard

### Проблема: Статус не обновляется на completed

**Причина:** Webhook еще не пришел или не прошел верификацию

**Решение:**
- Проверьте Paddle Dashboard → Notifications → Event logs
- Проверьте Django логи на ошибки webhook
- Проверьте что signature верификация работает

---

## Дальнейшие улучшения

- [ ] Добавить email уведомления при успешной оплате
- [ ] Добавить retry логику для webhook
- [ ] Создать админ панель для просмотра платежей
- [ ] Добавить аналитику по конверсии платежей
- [ ] Интегрировать BOG и TBC аналогичным образом

---

**Версия:** 1.0.0
**Дата:** 9 марта 2026
**Автор:** Pyland Team
