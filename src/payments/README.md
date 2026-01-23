# Payments Application

Приложение обработки платежей платформы Pyland School.

## Описание

Payments отвечает за обработку платежей за курсы, интеграцию с платежными шлюзами и управление транзакциями.

## Модели

### Payment
Основная модель платежа:
- **user** - пользователь, совершивший платеж
- **course** - курс, за который произведена оплата
- **amount** - сумма платежа
- **currency** - валюта (GEL по умолчанию)
- **status** - статус платежа
- **payment_method** - способ оплаты
- **transaction_id** - уникальный ID транзакции
- **extra_data** - дополнительные данные (JSON)
- **created_at** - дата создания
- **updated_at** - дата обновления

### Статусы платежей
- **pending** - Ожидает обработки
- **completed** - Успешно завершен
- **failed** - Ошибка платежа
- **refunded** - Возвращен

### Методы оплаты
- **card** - Банковская карта
- **paypal** - PayPal
- **stripe** - Stripe
- **manual** - Ручная оплата (admin)

## API Endpoints (планируется)

### Инициация платежа
```
POST   /api/payments/initiate
{
  "course_id": "uuid",
  "payment_method": "card"
}
```

### Проверка статуса
```
GET    /api/payments/{id}
```

### Webhook для шлюзов
```
POST   /api/payments/webhook
```

### История платежей
```
GET    /api/payments/history
```

### Возврат средств
```
POST   /api/payments/{id}/refund
```

## Views

### purchase_view
Страница покупки курса:
- GET: показывает форму оплаты
- POST: инициирует платеж
- Требует авторизации

## Процесс оплаты

### 1. Инициация
```
Студент → Страница курса → Кнопка "Купить" → purchase_view
```

### 2. Обработка
```
purchase_view → Payment Gateway API → Redirect к шлюзу
```

### 3. Подтверждение
```
Gateway → Webhook → Update Payment status → Enroll student
```

### 4. Зачисление
```
Payment.status = 'completed' → Добавление к Course.students
```

## Интеграция с шлюзами

### Stripe (планируется)
```python
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY
intent = stripe.PaymentIntent.create(...)
```

### PayPal (планируется)
```python
from paypalrestsdk import Payment
payment = Payment({...})
```

## Безопасность

### Хранение данных
- ❌ НЕ храним данные карт
- ✅ Храним только transaction_id
- ✅ Логируем все операции
- ✅ Шифруем sensitive данные в extra_data

### Валидация webhook
```python
def verify_webhook_signature(payload, signature):
    # Проверка подписи от платежного шлюза
    ...
```

## Admin панель

Планируемый функционал:
- Просмотр всех платежей
- Фильтры по статусу, методу, дате
- Цветные индикаторы статусов
- Экспорт в CSV/Excel
- Статистика по платежам
- Только чтение (изменения через API)

## Уведомления

При изменении статуса:
- Email пользователю
- Уведомление в личном кабинете
- Webhook для внешних систем

## Тестирование

### Тестовые карты (Stripe)
```
4242 4242 4242 4242 - Success
4000 0000 0000 0002 - Decline
4000 0000 0000 9995 - Insufficient funds
```

### Запуск тестов
```bash
pytest payments/tests/ -v
```

## Мониторинг

### Метрики
- Количество успешных платежей
- Средний чек
- Конверсия оплат
- Частые ошибки

### Логирование
Все операции логируются в:
- `payments.log`
- Sentry для критических ошибок
- Admin panel для истории

## Связанные приложения

- **courses** - связь платежа с курсом
- **students** - зачисление после оплаты
- **notifications** - уведомления о статусе
- **certificates** - генерация после покупки (опционально)

## Настройки

В `settings.py`:
```python
# Payment settings
STRIPE_PUBLIC_KEY = env('STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = env('STRIPE_WEBHOOK_SECRET')

PAYPAL_CLIENT_ID = env('PAYPAL_CLIENT_ID')
PAYPAL_SECRET = env('PAYPAL_SECRET')

DEFAULT_CURRENCY = 'GEL'
```

## Авторы

Pyland Team, 2025
