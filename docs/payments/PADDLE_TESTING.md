# Paddle Testing Guide

## Описание

Руководство по тестированию Paddle Billing интеграции в Pyland.

## Sandbox Environment

### Конфигурация

```bash
# .env
PADDLE_API_KEY=pdl_sdbx_apikey_YOUR_SANDBOX_KEY_HERE
PADDLE_ENVIRONMENT=sandbox
```

### Особенности Sandbox
- ✅ Тестовые транзакции НЕ списывают реальные деньги
- ✅ Можно использовать тестовые карты
- ✅ Автоматическое завершение платежей (без webhook)
- ⚠️ Нет email уведомлений
- ⚠️ Некоторые функции недоступны (например, Retain)

## Сохранение карт при checkout

Paddle позволяет покупателям безопасно сохранять свои карты для будущих покупок.

### Включение функции сохранения карт

1. Перейдите в **Paddle > Checkout > Checkout settings**
2. На вкладке **General** отметьте:
   - ☑️ *Allow buyers to opt in to save their payment methods for future purchases*
3. Нажмите **Save** для применения изменений

**Результат:**
- При checkout покупатели увидят опцию "Save payment method for future purchases"
- Сохраненные карты можно использовать для последующих покупок
- Данные карт хранятся в Paddle (PCI DSS compliant), не в нашей БД

---

## Тестовые карты

> ⚠️ **Важно:** Используйте только тестовые карты в sandbox окружении.
> Реальные карты не будут работать с Paddle sandbox account.

### Полный список тестовых карт Paddle

| Тип карты | Номер карты | CVC | Описание |
|-----------|-------------|-----|----------|
| **Valid Visa debit card** | `4000 0566 5566 5556` | `100` | Успешный платеж (Visa debit) |
| **Valid card without 3DS** | `4242 4242 4242 4242` | `100` | Успешный платеж (без 3D Secure) |
| **Valid card with 3DS** | `4000 0038 0000 0446` | `100` | Успешный платеж с 3D Secure |
| **Declined card** | `4000 0000 0000 0002` | `100` | Отклоненная карта |
| **Mixed behavior card** | `4000 0027 6000 3184` | `100` | Первый платеж успешный, последующие отклоняются |

**Дополнительные требования:**
- **Срок действия:** Любая валидная дата в будущем (например, `12/28`)
- **Cardholder name:** Любое имя (например, `Test User`)
- **Почтовый индекс:** Любой (например, `12345` или `SW1A 1AA`)

### Примеры использования

#### 1. Обычный успешный платеж
```text
Card number:     4242 4242 4242 4242
Expiry date:     12/28
CVC:             100
Cardholder name: Test User
ZIP/Postal code: 12345
```

#### 2. Платеж с 3D Secure (требует подтверждения)
```text
Card number:     4000 0038 0000 0446
Expiry date:     12/28
CVC:             100
Cardholder name: Test User
```

#### 3. Тестирование отклоненного платежа
```text
Card number:     4000 0000 0000 0002
Expiry date:     12/28
CVC:             100
Cardholder name: Declined Test
```

#### 4. Тестирование recurring payments (первый успех, потом ошибка)
```text
Card number:     4000 0027 6000 3184
Expiry date:     12/28
CVC:             100
Cardholder name: Recurring Test
```
**Поведение:** Первая транзакция пройдет успешно, все последующие будут отклонены.
Используйте для тестирования подписок и повторных платежей.

## Manual Testing Scenarios

### Сценарий 1: Успешная покупка курса

**Шаги:**
1. Войдите в систему как student
2. Перейдите на страницу курса (например, `/courses/kubernetes-for-beginners/`)
3. Нажмите кнопку "Купить курс"
4. Выберите валюту (USD, EUR или RUB)
5. Нажмите "Оплатить"
6. Дождитесь загрузки Paddle overlay
7. Введите email (или оставьте автозаполненный)
8. Введите данные тестовой карты: `4242 4242 4242 4242`
9. Нажмите "Pay"
10. Дождитесь редиректа на страницу успеха

**Ожидаемый результат:**
- ✅ Платеж создается в БД со статусом "pending"
- ✅ Статус обновляется на "processing" после создания transaction
- ✅ Paddle overlay открывается с правильной суммой и валютой
- ✅ После успеха редирект на `/payments/success/<payment_id>/`
- ✅ В sandbox статус автоматически становится "completed"
- ✅ Student автоматически зачисляется на курс
- ✅ Курс появляется в dashboard студента

**Проверка в БД:**
```python
poetry run python src/manage.py shell

from payments.models import Payment
payment = Payment.objects.last()

print(payment.status)  # "completed"
print(payment.transaction_id)  # "txn_..."
print(payment.course.student_enrollments.filter(id=payment.user.student.id).exists())  # True
```

### Сценарий 2: Отмена платежа

**Шаги:**
1. Повторите шаги 1-6 из Сценария 1
2. В Paddle overlay нажмите кнопку закрытия (X) или ESC
3. Дождитесь редиректа на страницу отмены

**Ожидаемый результат:**
- ✅ Редирект на `/payments/cancel/<payment_id>/`
- ✅ Статус платежа обновляется на "cancelled"
- ✅ Показывается сообщение "Платеж отменен"
- ✅ Есть кнопка "Попробовать снова"

### Сценарий 3: Отклоненная карта

**Шаги:**
1. Повторите шаги 1-7 из Сценария 1
2. Введите карту `4000 0000 0000 0002` (declined card)
3. Нажмите "Pay"

**Ожидаемый результат:**
- ✅ Paddle показывает ошибку "Card declined"
- ✅ Можно попробовать другую карту
- ✅ Статус платежа остается "processing" до успешной оплаты

### Сценарий 4: Конвертация валют

**Шаги:**
1. Откройте страницу checkout курса
2. Курс стоит $150.00 (базовая цена в USD)
3. Переключите валюту на EUR
4. Проверьте что цена стала €139.50 (150 * 0.93)
5. Переключите на RUB
6. Проверьте что цена стала ₽13,500 (150 * 90)

**Ожидаемый результат:**
- ✅ Цены конвертируются правильно
- ✅ Форматирование соответствует выбранной валюте
- ✅ В Paddle overlay отображается правильная сумма

### Сценарий 5: Переиспользование продуктов

**Цель**: Убедиться что не создаются дубликаты продуктов в Paddle.

**Шаги:**
1. Войдите в Paddle Dashboard (sandbox)
2. Перейдите в Catalog → Products
3. Запомните количество продуктов
4. Проведите покупку курса "Kubernetes для начинающих"
5. Вернитесь в Paddle Dashboard
6. Проверьте что количество продуктов НЕ увеличилось
7. Проведите еще одну покупку того же курса
8. Снова проверьте количество продуктов

**Ожидаемый результат:**
- ✅ При первой покупке нового курса создается 1 продукт
- ✅ При повторных покупках того же курса продукт переиспользуется
- ✅ В логах видно: "Using existing product: pro_01..."

**Проверка в логах:**
```bash
tail -f src/logs/pyland.log | grep "existing product"
```

### Сценарий 6: Race Condition с Customer

**Цель**: Проверить что дублирование email обрабатывается корректно.

**Шаги:**
1. Откройте 2 вкладки браузера
2. В обеих вкладках начните процесс покупки НОВОГО курса одновременно
3. Быстро нажмите "Оплатить" в обеих вкладках (разница ~1 секунда)
4. Проверьте что обе транзакции обработались успешно

**Ожидаемый результат:**
- ✅ Обе транзакции создаются
- ✅ Используется один и тот же customer_id
- ✅ В логах может быть warning "Duplicate customer detected" (это нормально)
- ✅ Из ошибки 409 извлекается существующий customer_id через regex

## Automated Testing (Future)

### Unit Tests Structure

```python
# src/payments/tests/test_paddle_service.py
import pytest
from decimal import Decimal
from payments.paddle_service import PaddleService
from payments.exceptions import TransactionCreationError

@pytest.fixture
def paddle_service():
    return PaddleService()

class TestPaddleService:

    def test_create_transaction_valid_data(self, paddle_service, user, course):
        """Тест успешного создания транзакции"""
        result = paddle_service.create_transaction(
            course_id=course.id,
            course_name=course.title,
            amount=Decimal("150.00"),
            currency="USD",
            user_email=user.email,
            user_id=user.id,
            success_url="http://test.com/success",
            cancel_url="http://test.com/cancel"
        )

        assert result["transaction_id"].startswith("txn_")
        assert result["customer_id"].startswith("ctm_")
        assert result["client_token"] is not None

    def test_create_transaction_invalid_amount(self, paddle_service, user, course):
        """Тест с невалидной суммой"""
        with pytest.raises(TransactionCreationError):
            paddle_service.create_transaction(
                course_id=course.id,
                course_name=course.title,
                amount=Decimal("-10.00"),  # Отрицательная сумма
                currency="USD",
                user_email=user.email,
                user_id=user.id
            )

    def test_find_existing_product(self, paddle_service, course):
        """Тест поиска существующего продукта"""
        # Создаем продукт
        product_id1 = paddle_service._get_or_create_product(
            course.id,
            course.title
        )

        # Проверяем что при повторном вызове возвращается тот же ID
        product_id2 = paddle_service._get_or_create_product(
            course.id,
            course.title
        )

        assert product_id1 == product_id2
```

### Integration Tests

```python
# src/payments/tests/test_views.py
import pytest
from django.urls import reverse
from payments.models import Payment

@pytest.mark.django_db
class TestCheckoutView:

    def test_checkout_get(self, client, user, course):
        """Тест GET запроса на checkout"""
        client.force_login(user)
        url = reverse('payments:checkout', args=[course.slug])
        response = client.get(url)

        assert response.status_code == 200
        assert 'form' in response.context
        assert course.title in str(response.content)

    def test_checkout_post_creates_payment(self, client, user, course):
        """Тест что POST создает Payment в БД"""
        client.force_login(user)
        url = reverse('payments:checkout', args=[course.slug])

        response = client.post(url, {
            'currency': 'USD',
            'payment_method': 'paddle'
        })

        # Должен быть редирект на paddle_redirect
        assert response.status_code == 200
        assert 'paddle_redirect.html' in [t.name for t in response.templates]

        # Проверяем что Payment создан
        payment = Payment.objects.filter(
            user=user,
            course=course,
            status='processing'
        ).first()

        assert payment is not None
        assert payment.transaction_id is not None
```

### API Tests

```python
# src/payments/tests/test_api.py
import pytest
from ninja.testing import TestClient
from pyland.api import api

@pytest.mark.django_db
class TestPaymentAPI:

    def test_payment_history(self, user, payment):
        """Тест получения истории платежей"""
        client = TestClient(api)
        client.force_authenticate(user)

        response = client.get('/api/payments/history/')

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]['id'] == str(payment.id)
```

## Testing Checklist

### Pre-Checkout
- [ ] Course page загружается корректно
- [ ] Кнопка "Купить курс" отображается для незачисленных студентов
- [ ] Для зачисленных студентов показывается "Перейти к обучению"

### Checkout Form
- [ ] Форма отображает все 3 валюты (USD, EUR, RUB)
- [ ] Цены конвертируются правильно
- [ ] Форма валидирует обязательные поля
- [ ] Показывается информация о Paddle Billing

### Paddle Integration
- [ ] Paddle.js загружается (проверить в DevTools → Network)
- [ ] CSP не блокирует Paddle домены (проверить Console)
- [ ] Client token генерируется и передается в frontend
- [ ] Transaction ID корректный (формат `txn_...`)

### Payment Flow
- [ ] Overlay открывается при клике "Оплатить"
- [ ] Email пользователя автозаполняется
- [ ] Сумма и валюта отображаются правильно
- [ ] Тестовая карта 4242... принимается
- [ ] После успеха redirect на success page
- [ ] При закрытии overlay redirect на cancel page

### Post-Payment
- [ ] Payment.status обновляется на "completed" (sandbox)
- [ ] Student зачисляется на курс автоматически
- [ ] Курс появляется в dashboard студента
- [ ] Показывается сообщение об успехе
- [ ] Email confirmation отправляется (production only)

### Database
- [ ] Payment создается со всеми полями
- [ ] transaction_id сохраняется
- [ ] extra_data содержит ответ от Paddle
- [ ] Нет дублирующихся платежей

### Paddle Dashboard
- [ ] Transaction появляется в Transactions
- [ ] Customer создается или переиспользуется
- [ ] Product переиспользуется (нет дубликатов)
- [ ] Price создается корректно

### Logging
- [ ] Все операции логируются с контекстом
- [ ] Ошибки логируются с full traceback
- [ ] Чувствительные данные (client_token) обрезаются в логах

### Error Handling
- [ ] Declined card показывает понятную ошибку
- [ ] Network error обрабатывается gracefully
- [ ] Invalid currency показывает validation error
- [ ] Missing client token не падает с 500

## Performance Testing

### Load Testing Script
```python
# locustfile.py
from locust import HttpUser, task, between

class PaymentUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        # Login
        self.client.post("/accounts/login/", {
            "username": "testuser",
            "password": "testpass123"
        })

    @task
    def view_course(self):
        self.client.get("/courses/kubernetes-for-beginners/")

    @task(3)
    def load_checkout(self):
        # Имитация загрузки checkout (не POST, только просмотр)
        self.client.get("/payments/checkout/kubernetes-for-beginners/")
```

**Запуск:**
```bash
pip install locust
locust -f locustfile.py
```

## Monitoring & Alerts

### Metrics to Track
- Transaction success rate
- Average payment time
- Customer creation errors
- Product creation errors
- Client token generation failures

### Dashboard Queries
```python
# Успешные платежи за последние 24 часа
Payment.objects.filter(
    status='completed',
    created_at__gte=timezone.now() - timedelta(days=1)
).count()

# Failed платежи
Payment.objects.filter(
    status='failed',
    created_at__gte=timezone.now() - timedelta(days=1)
).values('extra_data__error').annotate(count=Count('id'))

# Средняя сумма платежа
from django.db.models import Avg
Payment.objects.filter(status='completed').aggregate(Avg('amount'))
```

## Production Testing

### Pre-Production Checklist
- [ ] Получен production API key
- [ ] `PADDLE_ENVIRONMENT=production` в .env
- [ ] Webhook URL настроен в Paddle Dashboard
- [ ] Webhook handler реализован и протестирован
- [ ] SSL сертификат валидный
- [ ] CSP headers настроены
- [ ] Monitoring и alerts настроены

### Production Test Transaction
1. Используйте реальную карту с минимальной суммой
2. Проведите тестовую покупку
3. Убедитесь что webhook получен
4. Проверьте что email отправлен
5. Сделайте refund через Paddle Dashboard
6. Убедитесь что статус обновился

### A/B Testing Ideas
- Различные формулировки на кнопке "Купить"
- Отображение цены в нескольких валютах одновременно
- Добавление trust badges (SSL, Money back guarantee)
- Упрощение checkout flow (убрать лишние поля)

## Common Issues & Solutions

### Issue: "Client token not found"
**Solution**: Проверьте что `paddle_service.create_transaction()` вернул client_token и он передается в template.

### Issue: CSP блокирует Paddle
**Solution**:
```python
# Добавьте все домены из payments/constants.py
from payments.constants import get_full_paddle_csp
response["Content-Security-Policy"] = get_full_paddle_csp()
```

### Issue: Дублирующиеся продукты
**Solution**: Убедитесь что `_find_existing_product()` вызывается перед созданием нового продукта.

### Issue: TypeError with UUID
**Solution**: Используйте `str(course_id)` или измените type hint на `int | UUID`.

## Полезные команды

### Проверка статуса платежа
```bash
poetry run python src/manage.py shell

from payments.models import Payment
payment = Payment.objects.get(id='<uuid>')
print(f"Status: {payment.status}")
print(f"Transaction ID: {payment.transaction_id}")
print(f"Extra data: {payment.extra_data}")
```

### Просмотр логов
```bash
# Все логи платежей
tail -f src/logs/pyland.log | grep "paddle"

# Только ошибки
tail -f src/logs/pyland.log | grep "ERROR"

# Фильтр по transaction ID
tail -f src/logs/pyland.log | grep "txn_01kmmh1d4g0nx9tqpmkzcc23vq"
```

### Очистка тестовых данных
```bash
poetry run python src/manage.py shell

from payments.models import Payment
Payment.objects.filter(status='pending').delete()  # Удалить незавершенные
```

## Next Steps

1. **Unit Tests**: Создать factory fixtures для Payment, Course, User
2. **Integration Tests**: Протестировать full payment flow с mock Paddle API
3. **Webhook Tests**: Реализовать тесты для webhook handler
4. **Performance Tests**: Запустить load testing с Locust
5. **E2E Tests**: Добавить Selenium/Playwright тесты для UI
6. **Monitoring**: Настроить Sentry для отслеживания ошибок
7. **Analytics**: Интегрировать с Google Analytics для tracking conversions

## Полезные ссылки

- [Paddle Sandbox](https://sandbox-vendors.paddle.com/)
- [Test Cards](https://developer.paddle.com/concepts/payment-methods/credit-debit-card#test-card-numbers)
- [Paddle Testing Guide](https://developer.paddle.com/concepts/sell/testing)
- [pytest-django](https://pytest-django.readthedocs.io/)
