# Payments System Documentation

## Обзор

Система платежей Pyland использует **Paddle Billing** как единственный платежный шлюз для обработки покупок курсов.

## Архитектура

```
┌─────────────┐     ┌──────────────┐     ┌────────────────┐
│   Student   │────▶│  Django App  │────▶│ Paddle Billing │
│   (Browser) │     │  (Backend)   │     │   (External)   │
└─────────────┘     └──────────────┘     └────────────────┘
       │                    │                      │
       │                    ▼                      │
       │            ┌──────────────┐               │
       │            │   Payment    │               │
       │            │    Model     │               │
       │            └──────────────┘               │
       │                                           │
       └───────────── Paddle.js overlay ──────────┘
```

## Основные компоненты

### 1. Backend (Django)

- **models.py** - модель Payment для хранения транзакций
- **paddle_service.py** - сервис для работы с Paddle Billing API
- **views.py** - Django views для checkout и страниц результата
- **api.py** - REST API endpoints (Django Ninja)
- **forms.py** - форма checkout с валидацией
- **constants.py** - CSP домены для Paddle

### 2. Frontend

- **checkout.html** - страница выбора валюты и подтверждения
- **paddle_redirect.html** - страница инициализации Paddle.js
- **payment_success.html** - страница успешной оплаты
- **payment_cancel.html** - страница отмены

### 3. Static Files

- **payments/css/paddle_checkout.css** - стили форм оплаты
- **payments/js/paddle_checkout.js** - Paddle.js интеграция

## Поддерживаемые валюты

- **USD** - Доллар США (базовая валюта)
- **EUR** - Евро
- **RUB** - Российский рубль
- **GEL** - Грузинский лари

## Статусы платежей

| Статус | Описание |
|--------|----------|
| `pending` | Платеж создан, ожидает оплаты |
| `processing` | Платеж в обработке (после redirect с Paddle) |
| `completed` | Платеж завершен, студент зачислен на курс |
| `failed` | Ошибка при оплате |
| `cancelled` | Платеж отменен пользователем |
| `refunded` | Платеж возвращен |

## Процесс оплаты

### Шаг 1: Пользователь выбирает курс
- URL: `/payments/checkout/{course_slug}/`
- Отображается форма с выбором валюты
- Показываются цены во всех валютах (конвертация через exchange rates)

### Шаг 2: Создание транзакции
```python
# Django создает Payment в БД
payment = Payment.objects.create(
    user=user,
    course=course,
    amount=amount,
    currency=currency,
    payment_method="paddle",
    status="pending"
)

# Вызывает Paddle Service
paddle_data = paddle_service.create_transaction(
    course_id=course.id,
    course_name=course.name,
    amount=amount,
    currency=currency,
    user_email=user.email,
    user_id=user.id,
    success_url=success_url,
    cancel_url=cancel_url
)
```

### Шаг 3: Paddle.js Overlay
- Пользователь перенаправляется на `paddle_redirect.html`
- JavaScript инициализирует Paddle.js с client token
- Открывается overlay с формой оплаты
- Пользователь вводит данные карты прямо в Paddle

### Шаг 4: Обработка результата
- **Success**: redirect на `/payments/success/{payment_id}/`
- **Cancel**: redirect на `/payments/cancel/{payment_id}/`
- В sandbox режиме автоматически завершается и зачисляется на курс
- В production ждет webhook от Paddle

### Шаг 5: Зачисление на курс
```python
# При завершении платежа
payment.mark_as_completed()  # Автоматически добавляет в course.student_enrollments
```

## Окружения

### Sandbox (Development)
- URL: `https://sandbox-api.paddle.com`
- Тестовые карты: `4242 4242 4242 4242`
- Автоматическое завершение платежей
- Client token генерируется для каждой транзакции

### Production
- URL: `https://api.paddle.com`
- Реальные карты
- Webhook обработка (TODO)
- Полная интеграция с Paddle Retain

## Безопасность

### Content Security Policy
Для работы Paddle.js требуются следующие домены в CSP:

```python
# constants.py
PADDLE_SCRIPT_SRC = (
    "https://cdn.paddle.com",
    "https://sandbox-cdn.paddle.com",
)

PADDLE_FRAME_SRC = (
    "https://checkout.paddle.com",
    "https://sandbox-checkout.paddle.com",
    "https://buy.paddle.com",
    "https://sandbox-buy.paddle.com",
)
```

### Webhook Verification
TODO: Реализовать проверку подписи Paddle webhook.

## Конфигурация

### Переменные окружения (.env)
```bash
PADDLE_API_KEY=pdl_sdbx_apikey_*****  # API ключ из Paddle Dashboard
PADDLE_ENVIRONMENT=sandbox            # sandbox или production
```

### Django Settings
```python
# settings.py
PADDLE_API_KEY = os.getenv("PADDLE_API_KEY")
PADDLE_ENVIRONMENT = os.getenv("PADDLE_ENVIRONMENT", "sandbox")
```

## API Endpoints

### REST API (Django Ninja)

```http
POST /api/payments/paddle/checkout
Content-Type: application/json
Authorization: Bearer {jwt_token}

{
  "course_id": 123,
  "success_url": "...",
  "cancel_url": "..."
}
```

**Response:**
```json
{
  "checkout_url": "/payments/paddle/redirect/...",
  "transaction_id": "txn_...",
  "payment_id": "uuid"
}
```

## Логирование

Все операции с Paddle логируются с контекстом:

```python
logger.info(
    "Paddle transaction created",
    extra={
        "transaction_id": transaction_id,
        "course_id": course_id,
        "amount": amount,
        "currency": currency,
        "user_email": user_email
    }
)
```

## Дополнительная документация

- [Техническая интеграция Paddle](./PADDLE_INTEGRATION.md)
- [Тестирование платежей](./PADDLE_TESTING.md)
- [Официальная документация Paddle](https://developer.paddle.com/)

## Roadmap

- [ ] Webhook handler для production
- [ ] Возврат средств (refunds)
- [ ] Подписки (subscriptions)
- [ ] Купоны и скидки
- [ ] Analytics и отчеты
- [ ] Apple Pay / Google Pay
- [ ] Paddle Retain интеграция
