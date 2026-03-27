# Paddle Integration - Technical Documentation

## Описание

Полная техническая документация по интеграции Paddle Billing в Pyland.

## Установка и настройка

### 1. Установка SDK

```bash
poetry add paddle-python-sdk
```

### 2. Конфигурация

#### Environment Variables
```bash
# .env
PADDLE_API_KEY=pdl_sdbx_apikey_YOUR_SANDBOX_KEY_HERE
PADDLE_ENVIRONMENT=sandbox
```

#### Django Settings
```python
# pyland/settings.py
PADDLE_API_KEY = os.getenv("PADDLE_API_KEY")
PADDLE_ENVIRONMENT = os.getenv("PADDLE_ENVIRONMENT", "sandbox")

# CSP для Paddle.js
if "students.middleware.StudentsSecurityHeadersMiddleware" in MIDDLEWARE:
    # CSP настраивается автоматически через payments.constants
    pass
```

## Архитектура кода

### PaddleService (paddle_service.py)

Singleton-сервис для работы с Paddle Billing API.

#### Инициализация
```python
from payments.paddle_service import get_paddle_service

paddle_service = get_paddle_service()
```

#### Основные методы

##### 1. create_transaction()
Создает транзакцию в Paddle для покупки курса.

```python
def create_transaction(
    course_id: int | UUID,      # ID курса в БД
    course_name: str,            # Название курса
    amount: Decimal,             # Сумма в основной валюте
    currency: str,               # Код валюты (USD, EUR, RUB, GEL)
    user_email: str,             # Email пользователя
    user_id: int,                # ID пользователя в БД
    success_url: str | None,     # URL успеха
    cancel_url: str | None       # URL отмены
) -> dict[str, Any]
```

**Возвращает:**
```python
{
    "transaction_id": "txn_01kmmh1d4g0nx9tqpmkzcc23vq",
    "status": "ready",
    "client_token": "test_f36ae0bb16877cb...",
    "customer_id": "ctm_01kk7ranzwksaczcnwz4rpt55k",
    "amount": "15000.00",
    "currency": "USD",
    "product_id": "pro_01...",
    "price_id": "pri_01..."
}
```

**Процесс:**
1. Валидирует входные параметры через `_validate_transaction_inputs()`
2. Конвертирует сумму в центы (amount * 100)
3. Создает или находит Customer через `_get_or_create_customer()`
4. Создает или находит Product через `_get_or_create_product()`
5. Создает Price для Product через `_create_price()`
6. Создает Transaction с item (product + price)
7. Генерирует Client Token для Paddle.js через `_create_client_token()`

##### 2. _get_or_create_customer()
Находит существующего customer по email или создает нового.

**Логика:**
- Вызывает `_find_existing_customer(email)` - ищет через Paddle API
- Если находит - возвращает customer_id
- Если не находит - создает нового через `CreateCustomer()`
- При конфликте (409) - извлекает ID из ошибки через regex

```python
def _get_or_create_customer(self, email: str, user_id: int) -> str:
    # Сначала ищем существующего
    existing = self._find_existing_customer(email)
    if existing:
        return existing

    # Создаем нового
    customer = self.client.customers.create(
        CreateCustomer(
            email=email,
            custom_data={"user_id": str(user_id)}
        )
    )
    return customer.id
```

##### 3. _get_or_create_product()
Находит существующий product по названию курса или создает новый.

**Важно**: Это позволяет переиспользовать продукты и не создавать дубликаты!

```python
def _get_or_create_product(self, course_id: int | UUID, course_name: str) -> str:
    # Шаг 1: Ищем существующий active product по имени
    existing = self._find_existing_product(course_name)
    if existing:
        return existing

    # Шаг 2: Создаем новый
    product = self.client.products.create(
        CreateProduct(
            name=course_name,
            tax_category=TaxCategory.Standard,
            description=f"Курс {course_name}",
            custom_data={"course_id": str(course_id)}
        )
    )
    return product.id
```

##### 4. _find_existing_product()
Ищет active продукт по точному названию.

```python
def _find_existing_product(self, course_name: str) -> str | None:
    products = self.client.products.list(
        ListProducts(status=["active"])
    )

    for product in products:
        if product.name == course_name:
            return product.id

    return None
```

##### 5. _create_price()
Создает price для продукта в Paddle.

```python
def _create_price(
    self,
    product_id: str,
    amount_cents: str,  # "15000" для $150.00
    currency: str,      # "USD"
    description: str    # "Курс Kubernetes..."
) -> str:
    price = self.client.prices.create(
        CreatePrice(
            product_id=product_id,
            description=description,
            unit_price=Money(amount=amount_cents, currency_code=CurrencyCode(currency)),
            tax_mode=TaxMode.AccountSetting,
        )
    )
    return price.id
```

##### 6. _create_client_token()
Генерирует client token для Paddle.js checkout.

```python
def _create_client_token(
    self,
    transaction_id: str,
    course_name: str,
    user_email: str
) -> str | None:
    token = self.client.client_tokens.create(
        CreateClientToken(
            name=f"Checkout for transaction {transaction_id}",
            description=f"Client token for {course_name} purchase by {user_email}"
        )
    )
    return token.token
```

### Константы и Enums

#### PaddleEnvironment
```python
class PaddleEnvironment(str, Enum):
    SANDBOX = "sandbox"
    PRODUCTION = "production"
```

#### Константы
```python
CLIENT_TOKEN_NAME_MAX_LENGTH: Final[int] = 200
CUSTOMER_ID_PATTERN: Final[str] = r'ctm_[a-z0-9]+'
AMOUNT_TO_CENTS_MULTIPLIER: Final[int] = 100
CLIENT_TOKEN_LOG_LENGTH: Final[int] = 20
```

### Исключения

#### Иерархия
```python
PaddleError (базовое)
├── CustomerCreationError
├── TransactionCreationError
└── ProductCreationError
```

#### Использование
```python
try:
    paddle_data = paddle_service.create_transaction(...)
except TransactionCreationError as e:
    logger.error(f"Transaction failed: {e}")
    # Handle error
except CustomerCreationError as e:
    logger.error(f"Customer creation failed: {e}")
    # Handle error
```

## Django Views

### checkout_view()
```python
@login_required
@require_http_methods(["GET", "POST"])
def checkout_view(request: HttpRequest, course_slug: str) -> HttpResponse
```

**GET**: Отображает форму с выбором валюты и ценами.

**POST**:
1. Валидирует форму
2. Создает Payment в БД (status="pending")
3. Вызывает `paddle_service.create_transaction()`
4. Обновляет Payment (status="processing", transaction_id)
5. Рендерит `paddle_redirect.html` с client_token

### payment_success_view()
```python
@login_required
def payment_success_view(request: HttpRequest, payment_id: str) -> HttpResponse
```

- В **sandbox**: автоматически вызывает `payment.mark_as_completed()`
- В **production**: показывает "processing", ждет webhook

### payment_cancel_view()
```python
@login_required
def payment_cancel_view(request: HttpRequest, payment_id: str) -> HttpResponse
```

- Обновляет статус на "cancelled"
- Показывает страницу с предложением попробовать снова

## Frontend Integration

### paddle_redirect.html

Страница инициализации Paddle.js checkout.

**Data Attributes:**
```html
<div id="paddle-checkout-container"
     data-transaction-id="{{ transaction_id }}"
     data-client-token="{{ client_token }}"
     data-paddle-env="{{ paddle_env }}"
     data-success-url="{{ success_url }}"
     data-cancel-url="{{ cancel_url }}"
     data-customer-email="{{ payment.user.email }}"
     data-has-token="true">
```

### paddle_checkout.js

JavaScript модуль для работы с Paddle.js.

**Структура:**
```javascript
(function() {
    'use strict';

    function getPaddleConfig() { }      // Читает data-атрибуты
    function updateStatus(html) { }     // Обновляет UI
    function handlePaddleEvent(event) { } // Обработка событий
    function openCheckout(config) { }   // Открывает overlay
    function initializePaddle() { }     // Главная функция

    // Auto-init on DOMContentLoaded
})();
```

**Paddle.js События:**
- `checkout.loaded` - форма загружена
- `checkout.completed` - платеж успешен → redirect на success_url
- `checkout.closed` - форма закрыта → redirect на cancel_url
- `checkout.error` - ошибка → показать сообщение

### CSP Configuration

**students/middleware.py:**
```python
from payments.constants import get_full_paddle_csp

csp = get_full_paddle_csp(
    include_unsafe_inline_styles=True,  # Для inline styles
    include_unsafe_eval_scripts=False,  # Безопасность
    include_data_images=True            # Для base64 images
)
response["Content-Security-Policy"] = csp
```

**payments/constants.py:**
```python
PADDLE_SCRIPT_SRC: Final[tuple[str, ...]] = (
    "https://cdn.paddle.com",
    "https://sandbox-cdn.paddle.com",
)

PADDLE_STYLE_SRC: Final[tuple[str, ...]] = (
    "https://cdn.paddle.com",
    "https://sandbox-cdn.paddle.com",
)

PADDLE_CONNECT_SRC: Final[tuple[str, ...]] = (
    "https://api.paddle.com",
    "https://sandbox-api.paddle.com",
    "https://cdn.paddle.com",
    "https://sandbox-cdn.paddle.com",
)

PADDLE_FRAME_SRC: Final[tuple[str, ...]] = (
    "https://checkout.paddle.com",
    "https://sandbox-checkout.paddle.com",
    "https://buy.paddle.com",
    "https://sandbox-buy.paddle.com",
)
```

## Payment Model

### Поля
```python
class Payment(models.Model):
    id = models.UUIDField(primary_key=True)
    user = models.ForeignKey(User)
    course = models.ForeignKey(Course)
    amount = models.DecimalField()
    currency = models.CharField(max_length=3)  # USD, EUR, RUB, GEL
    status = models.CharField()                # pending, processing, completed...
    payment_method = models.CharField()        # всегда "paddle"
    transaction_id = models.CharField()        # Paddle transaction ID
    payment_url = models.URLField()
    payment_date = models.DateTimeField()
    extra_data = models.JSONField()            # Ответ от Paddle
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
```

### Методы

#### mark_as_completed()
```python
def mark_as_completed(self) -> None:
    self.status = "completed"
    self.payment_date = timezone.now()
    self.save()

    # Автоматически зачисляет на курс
    student = self.user.student
    if not self.course.student_enrollments.filter(id=student.id).exists():
        self.course.student_enrollments.add(student)
```

#### mark_as_failed()
```python
def mark_as_failed(self, error_message: str | None = None) -> None:
    self.status = "failed"
    if error_message:
        self.extra_data["error"] = error_message
    self.save()
```

## Конвертация валют

### EXCHANGE_RATES
```python
EXCHANGE_RATES: dict[str, Decimal] = {
    "USD": Decimal("1.00"),    # Базовая валюта
    "EUR": Decimal("0.93"),    # 1 USD = 0.93 EUR
    "RUB": Decimal("90.00"),   # 1 USD = 90 RUB
    "GEL": Decimal("2.65"),    # 1 USD = 2.65 GEL
}
```

### convert_currency()
```python
def convert_currency(amount: Decimal, from_currency: str, to_currency: str) -> Decimal:
    if from_currency == to_currency:
        return amount

    # Конвертируем через USD как базу
    usd_amount = amount / EXCHANGE_RATES[from_currency]
    result = usd_amount * EXCHANGE_RATES[to_currency]

    return result.quantize(Decimal("0.01"))
```

## Логирование

### Структурированные логи

```python
logger.info(
    "Paddle transaction created",
    extra={
        "transaction_id": transaction_id,
        "course_id": str(course_id),
        "amount": str(amount),
        "currency": currency,
        "user_email": user_email,
        "product_id": product_id,
        "price_id": price_id,
    }
)
```

### Уровни логов
- **INFO**: Успешные операции (transaction created, customer found)
- **WARNING**: Неожиданные ситуации (duplicate customer, product search failed)
- **ERROR**: Критические ошибки (transaction failed, customer creation error)

## Best Practices

### 1. Переиспользование продуктов
✅ **DO**: Ищите существующий product по названию
```python
existing = self._find_existing_product(course_name)
if existing:
    return existing
```

❌ **DON'T**: Создавайте новый product каждый раз

### 2. Обработка ошибок
✅ **DO**: Используйте специфичные исключения
```python
try:
    paddle_data = create_transaction(...)
except TransactionCreationError as e:
    logger.error(f"Transaction failed: {e}")
    messages.error(request, _("Ошибка создания платежа"))
```

❌ **DON'T**: Ловите общий Exception без логирования

### 3. Валидация входных данных
✅ **DO**: Валидируйте до вызова API
```python
self._validate_transaction_inputs(
    course_id, course_name, amount, currency, user_email, user_id
)
```

### 4. Client Token безопасность
✅ **DO**: Генерируйте client token на backend
```python
client_token = paddle_service._create_client_token(...)
# Передаем в template только token, не API key
```

❌ **DON'T**: Не храните API key в frontend коде

### 5. CSP Headers
✅ **DO**: Используйте централизованные константы
```python
from payments.constants import get_full_paddle_csp
csp = get_full_paddle_csp()
```

## Troubleshooting

### Проблема: "Client token not found"
**Причина**: Client token не создан или не передан в template.
**Решение**:
```python
if not paddle_data.get("client_token"):
    logger.error("Client token missing")
    # Handle error
```

### Проблема: CSP блокирует Paddle
**Причина**: Недостаточно доменов в Content-Security-Policy.
**Решение**: Добавьте все домены из `constants.py`:
- script-src: cdn.paddle.com
- frame-src: checkout.paddle.com, buy.paddle.com
- connect-src: api.paddle.com

### Проблема: Дублирующиеся продукты
**Причина**: Не работает `_find_existing_product()`.
**Решение**: Проверьте что названия курсов уникальны и совпадают точно.

### Проблема: TypeError with UUID
**Причина**: `course_id` передается как UUID, а ожидается int.
**Решение**: Используйте `int | UUID` в type hints:
```python
def create_transaction(course_id: int | UUID, ...)
```

## Миграция на Production

### Чеклист
- [ ] Получить production API key из Paddle Dashboard
- [ ] Установить `PADDLE_ENVIRONMENT=production` в .env
- [ ] Настроить webhook URL в Paddle Dashboard
- [ ] Реализовать webhook handler с проверкой подписи
- [ ] Убрать автоматическое завершение платежей (только через webhook)
- [ ] Настроить мониторинг и алерты
- [ ] Провести тестовую транзакцию с реальной картой
- [ ] Настроить Paddle Retain для улучшения конверсии

## Полезные ссылки

- [Paddle Developer Docs](https://developer.paddle.com/)
- [Paddle Python SDK](https://github.com/PaddleHQ/paddle-python-sdk)
- [Paddle Billing Guide](https://developer.paddle.com/billing)
- [Paddle Checkout](https://developer.paddle.com/paddlejs/overview)
- [Testing Guide](./PADDLE_TESTING.md)
