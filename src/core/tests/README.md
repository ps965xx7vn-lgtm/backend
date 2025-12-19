# Core Tests

Юнит тесты для приложения core с полным покрытием API, схем и валидации.

## 🎯 Обзор

**Всего тестов:** 53
**Покрытие:** API эндпоинты, Pydantic схемы, валидация ответов

**Используемые инструменты:**

- `pytest` - фреймворк для тестирования
- `pytest-django` - плагин для Django
- `django.test.TestCase` - базовый класс для тестов
- `pydantic` - валидация схем

---

## 📁 Структура тестов

```text
tests/
├── __init__.py
├── test_api.py                     # 15 тестов API эндпоинтов
├── test_schemas.py                 # 28 тестов Pydantic схем
└── test_response_validation.py     # 10 тестов валидации ответов
```text
---

## 🔌 test_api.py

**15 тестов** для проверки REST API эндпоинтов.

### Fixture `api_client`

```python
@pytest.fixture
def api_client():
    """Клиент для тестирования API эндпоинтов."""
    from ninja.testing import TestClient
    from pyland.api import api
    return TestClient(api)
```text
---

### Feedback API Tests (6 тестов)

#### `test_create_feedback_success`

✅ Проверяет успешное создание заявки обратной связи.

**Тестирует:**

- POST `/api/core/feedback/`
- Валидный payload с всеми полями
- Статус 200
- Структура ответа (success, message, feedback_id)
- Создание записи в БД

**Код:**

```python
def test_create_feedback_success(self, api_client):
    payload = {
        "first_name": "Иван",
        "phone_number": "+79991234567",
        "email": "ivan@example.com",
        "message": "Хочу узнать больше о курсах Python",
        "agree_terms": True
    }

    response = api_client.post("/core/feedback/", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "feedback_id" in data
    assert Feedback.objects.filter(id=data["feedback_id"]).exists()
```text
---

#### `test_create_feedback_invalid_phone`

✅ Проверяет валидацию неправильного номера телефона.

**Тестирует:**

- Телефон без `+`
- Телефон с буквами
- Телефон слишком короткий/длинный
- Статус 422 (Validation Error)

---

#### `test_create_feedback_invalid_email`

✅ Проверяет валидацию email.

**Тестирует:**

- Email без `@`
- Email без домена
- Статус 422

---

#### `test_create_feedback_short_message`

✅ Проверяет минимальную длину сообщения.

**Тестирует:**

- Сообщение < 10 символов
- Статус 422
- Сообщение об ошибке

---

#### `test_create_feedback_without_consent`

✅ Проверяет обязательность согласия с условиями.

**Тестирует:**

- `agree_terms = False`
- Статус 422
- Требование согласия

---

#### `test_create_feedback_name_with_digits`

✅ Проверяет запрет цифр в имени.

**Тестирует:**

- Имя "Иван123"
- Кастомный валидатор
- Статус 422

---

### Subscription API Tests (4 теста)

#### `test_create_subscription_new`

✅ Проверяет создание новой подписки.

**Тестирует:**

- POST `/api/core/subscribe/`
- Новый email
- Создание записи Subscription
- `already_subscribed = False`

**Код:**

```python
def test_create_subscription_new(self, api_client):
    payload = {"email": "new@example.com"}

    response = api_client.post("/core/subscribe/", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["already_subscribed"] is False
    assert Subscription.objects.filter(email="new@example.com").exists()
```text
---

#### `test_create_subscription_already_exists`

✅ Проверяет обработку дубликата подписки.

**Тестирует:**

- Подписка с существующим email
- Сообщение "уже подписан"
- `already_subscribed = True`
- Не создает дубликат в БД

---

#### `test_reactivate_inactive_subscription`

✅ Проверяет реактивацию неактивной подписки.

**Тестирует:**

- Подписка с `is_active = False`
- Реактивация (`is_active = True`)
- Сообщение "снова активна"

---

#### `test_subscription_invalid_email`

✅ Проверяет валидацию email для подписки.

**Тестирует:**

- Невалидный email
- Статус 422
- Pydantic EmailStr валидация

---

### Contact Info API Tests (1 тест)

#### `test_get_contact_info`

✅ Проверяет получение контактной информации.

**Тестирует:**

- GET `/api/core/contact-info/`
- Статус 200
- Структура ответа (email, phone, address, etc.)
- Опциональные поля (social_links)

**Код:**

```python
def test_get_contact_info(self, api_client):
    response = api_client.get("/core/contact-info/")

    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert "phone" in data
    assert "working_hours" in data
    assert isinstance(data.get("social_links"), dict)
```text
---

### Stats API Tests (3 теста)

#### `test_get_stats_empty_db`

✅ Проверяет статистику при пустой БД.

**Тестирует:**

- GET `/api/core/stats/`
- Дефолтные значения (0 для счетчиков)
- Структура StatsSchema

---

#### `test_get_stats_with_data`

✅ Проверяет статистику с реальными данными.

**Тестирует:**

- Создание тестовых данных (User, Course, Lesson)
- Правильный подсчет
- Вычисление completion_rate

---

#### `test_stats_counts_all_courses`

✅ Проверяет подсчет всех курсов.

**Тестирует:**

- Создание нескольких курсов
- Правильное количество в ответе

---

### Integration Tests (1 тест)

#### `test_full_user_journey`

✅ Проверяет полный путь пользователя.

**Тестирует:**

1. Отправка feedback
2. Подписка на рассылку
3. Получение contact-info
4. Получение stats
5. Связь между действиями

---

## 📋 test_schemas.py

**28 тестов** для проверки Pydantic схем и валидаторов.

### FeedbackSchema Tests (10 тестов)

#### `test_valid_feedback`

✅ Проверяет валидный payload.

**Код:**

```python
def test_valid_feedback(self):
    data = {
        "first_name": "Иван",
        "phone_number": "+79991234567",
        "email": "ivan@example.com",
        "message": "Тестовое сообщение длиннее 10 символов",
        "agree_terms": True
    }

    schema = FeedbackSchema(**data)
    assert schema.first_name == "Иван"
    assert schema.phone_number == "+79991234567"
```text
---

#### `test_phone_without_plus`

✅ Проверяет валидацию телефона без `+`.

**Тестирует:**

- `phone_number = "79991234567"` (без +)
- ValidationError
- Сообщение об ошибке regex pattern

---

#### `test_phone_invalid_format`

✅ Проверяет неправильный формат телефона.

**Тестирует:**

- Буквы в номере
- ValidationError

---

#### `test_phone_too_short` / `test_phone_too_long`

✅ Проверяет границы длины телефона.

**Тестирует:**

- Меньше 9 цифр после `+`
- Больше 15 цифр после `+`

---

#### `test_name_with_digits`

✅ Проверяет кастомный валидатор имени.

**Тестирует:**

- `first_name = "Иван123"`
- Кастомный @field_validator
- Сообщение "не должно содержать цифры"

**Код валидатора:**

```python
@field_validator('first_name')
@classmethod
def validate_no_digits(cls, value: str) -> str:
    if any(char.isdigit() for char in value):
        raise ValueError("Имя не должно содержать цифры")
    return value
```text
---

#### `test_message_too_short`

✅ Проверяет минимальную длину сообщения.

**Тестирует:**

- `message = "abc"` (< 10 символов)
- Field constraint `min_length=10`

---

#### `test_disagree_terms`

✅ Проверяет обязательность согласия.

**Тестирует:**

- `agree_terms = False`
- Field constraint `const=True`

---

#### `test_invalid_email`

✅ Проверяет EmailStr валидацию.

**Тестирует:**

- Email без `@`
- Pydantic EmailStr тип

---

#### `test_missing_required_field`

✅ Проверяет обязательные поля.

**Тестирует:**

- Отсутствие `phone_number`
- ValidationError

---

### SubscriptionSchema Tests (3 теста)

#### `test_valid_subscription`

✅ Валидный email для подписки.

---

#### `test_invalid_email`

✅ Невалидный email.

---

#### `test_missing_email`

✅ Отсутствующий email.

---

### ContactInfoSchema Tests (3 теста)

#### `test_full_contact_info`

✅ Полная контактная информация со всеми полями.

**Код:**

```python
def test_full_contact_info(self):
    data = {
        "email": "info@pyland.ru",
        "phone": "+7 (999) 123-45-67",
        "address": "г. Москва, ул. Примерная, д. 1",
        "working_hours": "Пн-Пт: 9:00-18:00",
        "social_links": {
            "telegram": "<https://t.me/pyland",>
            "vk": "<https://vk.com/pyland">
        }
    }

    schema = ContactInfoSchema(**data)
    assert schema.email == "info@pyland.ru"
    assert schema.social_links["telegram"] == "<https://t.me/pyland">
```text
---

#### `test_minimal_contact_info`

✅ Минимальная информация (только обязательные поля).

---

#### `test_empty_social_links`

✅ Пустые социальные ссылки.

---

### StatsSchema Tests (5 тестов)

#### `test_valid_stats`

✅ Валидная статистика.

---

#### `test_default_values`

✅ Значения по умолчанию (все 0).

**Код:**

```python
def test_default_values(self):
    schema = StatsSchema()
    assert schema.total_students == 0
    assert schema.total_courses == 0
    assert schema.completion_rate == 0.0
```text
---

#### `test_completion_rate_boundaries`

✅ Границы completion_rate (0-100).

**Тестирует:**

- `completion_rate = -1` → ValidationError
- `completion_rate = 101` → ValidationError
- `completion_rate = 0` → ✅
- `completion_rate = 100` → ✅

---

#### `test_negative_values`

✅ Запрет отрицательных значений для счетчиков.

**Тестирует:**

- `total_students = -1` → ValidationError
- Field constraint `ge=0` (greater or equal)

---

#### `test_feedback_response`

✅ FeedbackResponseSchema.

---

### Response Schemas Tests (7 тестов)

Проверка схем ответов API.

---

## ✅ test_response_validation.py

**10 тестов** для проверки валидации ответов API через Pydantic.

### Tests

#### `test_feedback_response_validates_success_field`

✅ Проверяет обязательность поля `success`.

---

#### `test_feedback_response_validates_feedback_id`

✅ Проверяет тип `feedback_id` (int).

---

#### `test_subscription_response_validates_already_subscribed`

✅ Проверяет поле `already_subscribed` (bool).

---

#### `test_contact_info_validates_social_links`

✅ Проверяет тип `social_links` (dict).

---

#### `test_stats_validates_numeric_fields`

✅ Проверяет числовые типы в статистике.

---

#### `test_stats_validates_completion_rate_bounds`

✅ Проверяет границы 0-100 для completion_rate.

---

#### `test_contact_info_requires_email_and_phone`

✅ Проверяет обязательные поля.

---

#### `test_response_schemas_are_immutable_after_creation`

✅ Проверяет неизменяемость Pydantic моделей.

**Код:**

```python
def test_response_schemas_are_immutable_after_creation(self):
    response = FeedbackResponseSchema(
        success=True,
        message="Test",
        feedback_id=1
    )

    with pytest.raises(ValidationError):
        response.success = False  # Должна быть ошибка
```text
---

#### `test_pydantic_models_can_be_serialized_to_dict`

✅ Проверяет сериализацию в dict.

**Код:**

```python
def test_pydantic_models_can_be_serialized_to_dict(self):
    schema = StatsSchema(
        total_students=100,
        total_courses=10,
        total_lessons=150,
        completion_rate=75.5
    )

    data = schema.model_dump()
    assert isinstance(data, dict)
    assert data["total_students"] == 100
```text
---

#### `test_pydantic_models_can_be_serialized_to_json`

✅ Проверяет сериализацию в JSON.

---

## 🚀 Запуск тестов

### Все тесты core

```bash
pytest src/core/tests/ -v
```text
### Конкретный файл

```bash
pytest src/core/tests/test_api.py -v
pytest src/core/tests/test_schemas.py -v
pytest src/core/tests/test_response_validation.py -v
```text
### Конкретный тест

```bash
pytest src/core/tests/test_api.py::TestFeedbackAPI::test_create_feedback_success -v
```text
### С output

```bash
pytest src/core/tests/ -v -s
```text
### Параллельный запуск

```bash
pytest src/core/tests/ -n auto
```text
---

## 📊 Coverage

### Запуск с coverage

```bash
pytest src/core/tests/ --cov=core --cov-report=html
```text
### Просмотр отчета

```bash
open htmlcov/index.html
```text
### Coverage по модулям

```bash
pytest src/core/tests/ --cov=core --cov-report=term-missing
```text
**Ожидаемое покрытие:**

- `api.py` - 95%+
- `schemas.py` - 100%
- `forms.py` - 90%+
- `views.py` - 85%+

---

## 🔧 Конфигурация pytest

### pytest.ini (в корне проекта)

```ini
[tool:pytest]
DJANGO_SETTINGS_MODULE = pyland.settings
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --strict-markers
    --tb=short
    --cov-report=term-missing
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
```text
---

## 🧪 Fixtures

### Общие fixtures (conftest.py)

```python
import pytest
from django.test import Client
from ninja.testing import TestClient

@pytest.fixture
def api_client():
    """API клиент для тестирования эндпоинтов."""
    from pyland.api import api
    return TestClient(api)

@pytest.fixture
def django_client():
    """Django клиент для тестирования views."""
    return Client()

@pytest.fixture
def sample_user(django_user_model):
    """Создает тестового пользователя."""
    return django_user_model.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )

@pytest.fixture
def sample_feedback():
    """Создает тестовую заявку feedback."""
    return Feedback.objects.create(
        first_name="Тест",
        phone_number="+79991234567",
        email="test@example.com",
        message="Тестовое сообщение"
    )
```text
---

## 📝 Best Practices

### 1. Именование тестов

```python
def test_<what_is_tested>_<expected_result>():

    # test_create_feedback_success

    # test_invalid_phone_raises_error

    pass
```text
### 2. AAA Pattern (Arrange, Act, Assert)

```python
def test_create_subscription_new(self):

    # Arrange - подготовка данных

    payload = {"email": "new@example.com"}

    # Act - выполнение действия

    response = api_client.post("/core/subscribe/", json=payload)

    # Assert - проверка результата

    assert response.status_code == 200
    assert data["success"] is True
```text
### 3. Используйте fixtures

```python
@pytest.fixture
def valid_feedback_data():
    return {
        "first_name": "Иван",
        "phone_number": "+79991234567",

        #

    }

def test_create_feedback(api_client, valid_feedback_data):
    response = api_client.post("/core/feedback/", json=valid_feedback_data)
    assert response.status_code == 200
```text
### 4. Тестируйте edge cases

```python

# Границы

test_phone_minimum_length()  # +123456789 (9 цифр)
test_phone_maximum_length()  # +123456789012345 (15 цифр)

# Ошибочные данные

test_empty_string()
test_none_value()
test_special_characters()
```text
---

## 🐛 Debugging тестов

### pdb debugger

```python
def test_something():
    import pdb; pdb.set_trace()

    # Тест остановится здесь

    assert something
```text
### pytest с print

```bash
pytest tests/test_api.py -v -s
```text
### Только failed тесты

```bash
pytest --lf  # last failed
pytest --ff  # failed first
```text
---

## 📚 Связанная документация

- [API Documentation](../api.py)
- [Schemas Documentation](../schemas.py)
- [Forms Documentation](../forms.py)
- [Views Documentation](../views.py)
- [Pytest Documentation](https://docs.pytest.org/)
- [Django Testing](https://docs.djangoproject.com/en/stable/topics/testing/)
