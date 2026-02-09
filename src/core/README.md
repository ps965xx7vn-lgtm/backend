# Core Application

Базовое приложение платформы Pyland для управления основными функциями
сайта, публичными страницами и REST API.

## 📚 Документация

- **[Templates README](templates/README.md)** - HTML шаблоны и их структура
- **[Template Tags README](templatetags/README.md)** - Custom template tags и фильтры
- **[Tests README](tests/README.md)** - Юнит тесты и coverage (53 теста)

## 🎯 Обзор

Приложение `core` - это фундамент платформы Pyland с базовой функциональностью:

- **Публичные страницы**: Главная, Контакты, О нас, Юридические страницы
- **Формы**: Обратная связь, Подписка на рассылку
- **REST API**: 4 публичных эндпоинта (Django Ninja)
- **Context Processors**: Глобальные данные для футера
- **Template Tags**: Markdown фильтры, article tags
- **Роль-based редиректы**: Умная маршрутизация пользователей

### Основные возможности

✅ Главная страница с популярными курсами
✅ Форма обратной связи с валидацией
✅ Подписка на email рассылку
✅ Юридические страницы (Terms of Service, Privacy Policy)
✅ REST API для AJAX запросов
✅ Context processor для футера сайта
✅ Markdown поддержка в шаблонах
✅ Умные редиректы по ролям пользователей
✅ 53 юнит теста (покрытие API и схем)
✅ Логирование всех операций (logger)

## 📁 Структура приложения

```text
core/
├── __init__.py              # Инициализация приложения с подробным docstring
├── apps.py                  # Конфигурация приложения (CoreConfig)
├── api.py                   # REST API эндпоинты (4 endpoints) + logger + try-except
├── schemas.py               # Pydantic схемы для валидации (6 схем)
├── forms.py                 # Django формы (FeedbackForm, SubscriptionForm) + logger
├── views.py                 # Django представления (7 views) + logger + try-except
├── urls.py                  # URL маршруты (6 URL patterns)
├── context_processors.py    # Глобальный контекст для шаблонов
├── cache_utils.py           # ⭐ Утилиты кеширования (Redis) + logger
├── middleware.py            # ⭐ Rate limiting и security headers + logger
├── migrations/              # Миграции базы данных (нет своих моделей)
├── templates/               # HTML шаблоны
│   ├── README.md           # Документация шаблонов
│   └── core/
│       ├── home.html        # Главная страница
│       ├── contacts.html    # Страница контактов
│       ├── about.html       # О нас
│       ├── terms_of_service.html    # Условия использования
│       └── privacy_policy.html      # Политика конфиденциальности
├── templatetags/            # Custom template tags
│   ├── README.md           # Документация template tags
│   ├── markdown_filters.py  # Фильтры для Markdown
│   └── article_tags.py      # Теги для статей блога
└── tests/                   # Юнит тесты (53 теста)
    ├── README.md            # Документация тестов
    ├── test_api.py          # Тесты API эндпоинтов (15 тестов)
    ├── test_schemas.py      # Тесты Pydantic схем (28 тестов)
    └── test_response_validation.py  # Валидация ответов (10 тестов)
```text
**⭐ Новые модули (аналогично blog):**

- `cache_utils.py` - Кеширование страниц и API данных через Redis
- `middleware.py` - Rate limiting для API + security headers

**См. подробную документацию:**

- [Templates README](templates/README.md) - Документация шаблонов
- [Template Tags README](templatetags/README.md) - Custom template tags
- [Tests README](tests/README.md) - Документация тестов

**Модули с логированием:**

- `views.py` - Логирование форм обратной связи и подписок + обработка исключений
- `api.py` - Логирование API запросов (feedback, subscription) + обработка исключений
- `forms.py` - Логирование валидации форм
- `cache_utils.py` - Логирование операций кеша (HIT/MISS, инвалидация)
- `middleware.py` - Логирование rate limit превышений и ошибок

## 🔌 API эндпоинты

### Базовый URL

```text
/api/core/
```text
Все эндпоинты публичные (не требуют аутентификации).

### 1. Отправка обратной связи

**POST** `/api/core/feedback/`

Создает новую заявку обратной связи от пользователя.

**Request Body:**

```json
{
  "first_name": "Иван",
  "phone_number": "+79991234567",
  "email": "ivan@example.com",
  "message": "Хочу узнать больше о курсах Python",
  "agree_terms": true
}
```text
**Validation:**

- `first_name`: не должно содержать цифры
- `phone_number`: формат `+XXXXXXXXX` (9-15 цифр после +)
- `email`: валидный email адрес
- `message`: минимум 10 символов
- `agree_terms`: должно быть `true`

**Response 200:**

```json
{
  "success": true,
  "message": "Спасибо! Мы получили ваше сообщение и свяжемся с вами в ближайшее время.",
  "feedback_id": 42
}
```text
---

### 2. Подписка на рассылку

**POST** `/api/core/subscribe/`

Подписывает email на рассылку новостей платформы.

**Request Body:**

```json
{
  "email": "user@example.com"
}
```text
**Response 200 (новая подписка):**

```json
{
  "success": true,
  "message": "Вы успешно подписаны на рассылку!",
  "already_subscribed": false
}
```text
**Response 200 (уже подписан):**

```json
{
  "success": true,
  "message": "Этот email уже подписан на рассылку.",
  "already_subscribed": true
}
```text
**Response 200 (реактивация):**

```json
{
  "success": true,
  "message": "Ваша подписка снова активна!",
  "already_subscribed": false
}
```text
---

### 3. Получение контактной информации

**GET** `/api/core/contact-info/`

Возвращает контактную информацию компании.

**Response 200:**

```json
{
  "email": "pylandschool@gmail.com",
  "phone": "+7 (999) 123-45-67",
  "address": "г. Москва, ул. Примерная, д. 1",
  "working_hours": "Пн-Пт: 9:00-18:00",
  "social_links": {
    "telegram": "<https://t.me/pyland",>
    "vk": "<https://vk.com/pyland",>
    "youtube": "<https://youtube.com/@pyland">
  }
}
```text
---

### 4. Получение статистики платформы

**GET** `/api/core/stats/`

Возвращает общую статистику платформы.

**Response 200:**

```json
{
  "total_students": 1250,
  "total_courses": 15,
  "total_lessons": 342,
  "completion_rate": 78.5
}
```text
---

## 📄 Представления (Views)

### Function-Based Views

Все представления используют функциональный подход для простоты.

#### `home(request)`

Главная страница платформы.

**Отображает:**

- Популярные курсы (аннотированные количеством студентов)
- Статистику платформы
- SEO мета-теги

**URL:** `/`
**Template:** `core/home.html`

---

#### `contacts(request)`

Страница контактов с формой обратной связи.

**Функциональность:**

- Отображение формы `FeedbackForm`
- Обработка POST запросов
- Сохранение заявок в модель `Feedback` (из приложения `manager`)
- Flash messages об успехе/ошибках

**URL:** `/contacts/`
**Template:** `core/contacts.html`

---

#### `about(request)`

Страница "О нас" с информацией о платформе.

**URL:** `/about/`
**Template:** `core/about.html`

---

#### `subscribe(request)`

Обработка подписки на email рассылку.

**Функциональность:**

- Валидация email через `SubscriptionForm`
- Создание записи в модель `Subscription` (notifications app)
- Обработка дубликатов подписок
- Редирект на главную с flash message

**URL:** `/subscribe/` (POST)
**Redirect:** `/`

---

#### `terms_of_service(request)`

Страница условий использования (юридическая).

**URL:** `/terms-of-service/`
**Template:** `core/terms_of_service.html`

---

#### `privacy_policy(request)`

Страница политики конфиденциальности (юридическая).

**URL:** `/privacy-policy/`
**Template:** `core/privacy_policy.html`

---

#### `home_redirect(request)`

Умный редирект пользователей по их ролям.

**Логика маршрутизации:**

- **Неаутентифицированные** → главная страница (`core:home`)
- **Mentor** → `mentor:mentor_dashboard`
- **Student** → `account:account_dashboard`
- **Manager** → `manager:manager_dashboard`
- **Reviewer** → `reviewer:reviewer_dashboard`
- **Без ролей** → главная страница

**URL:** `/` (если настроен как root redirect)

---

## 📝 Формы

### FeedbackForm

Форма обратной связи для страниц контактов и главной.

**Поля:**

- `first_name` - Имя отправителя (макс 100 символов)
- `phone_number` - Номер телефона (+1234567890)
- `email` - Email адрес
- `message` - Текст сообщения (обязательное, textarea)
- `agree_terms` - Согласие с условиями (checkbox)

**Валидация:**

- Имя не должно содержать цифры
- Телефон должен начинаться с `+` и содержать 9-15 цифр
- Email должен соответствовать стандартному формату
- Обязательно согласие с условиями

**Использование:**

```python
form = FeedbackForm(request.POST)
if form.is_valid():
    name = form.cleaned_data['first_name']
    Feedback.objects.create(**form.cleaned_data)
```text
---

### SubscriptionForm

Форма подписки на email рассылку.

**Поля:**

- `email` - Email адрес для подписки

**Валидация:**

- Email должен быть валидным

**Использование:**

```python
form = SubscriptionForm(request.POST)
if form.is_valid():
    email = form.cleaned_data['email']
    Subscription.objects.get_or_create(email=email)
```text
---

## 🔍 Схемы (Pydantic)

### Input Schemas

#### FeedbackSchema

Валидация входящих данных для обратной связи.

```python
class FeedbackSchema(Schema):
    first_name: str = Field(..., min_length=1, max_length=100)
    phone_number: str = Field(..., pattern=r'^\+\d{9,15}$')
    email: EmailStr
    message: str = Field(..., min_length=10)
    agree_terms: bool = Field(..., const=True)

    @field_validator('first_name')
    @classmethod
    def validate_no_digits(cls, value: str) -> str:
        if any(char.isdigit() for char in value):
            raise ValueError("Имя не должно содержать цифры")
        return value
```text
---

#### SubscriptionSchema

Валидация email для подписки.

```python
class SubscriptionSchema(Schema):
    email: EmailStr
```text
---

### Output Schemas

#### FeedbackResponseSchema

Ответ после создания заявки обратной связи.

```python
class FeedbackResponseSchema(Schema):
    success: bool
    message: str
    feedback_id: int
```text
---

#### SubscriptionResponseSchema

Ответ после подписки на рассылку.

```python
class SubscriptionResponseSchema(Schema):
    success: bool
    message: str
    already_subscribed: bool
```text
---

#### ContactInfoSchema

Контактная информация компании.

```python
class ContactInfoSchema(Schema):
    email: str
    phone: str
    address: Optional[str] = None
    working_hours: Optional[str] = None
    social_links: Optional[Dict[str, str]] = None
```text
---

#### StatsSchema

Общая статистика платформы.

```python
class StatsSchema(Schema):
    total_students: int = Field(default=0, ge=0)
    total_courses: int = Field(default=0, ge=0)
    total_lessons: int = Field(default=0, ge=0)
    completion_rate: float = Field(default=0.0, ge=0.0, le=100.0)
```text
---

## 🌐 Context Processors

### footer_data(request)

Добавляет глобальные данные в контекст всех шаблонов.

**Возвращает:**

```python
{
    'footer_data': {
        'popular_courses': QuerySet[Course],  # 3 популярных курса
        'stats': {
            'total_students': int,
            'total_courses': int,
            'total_lessons': int,
            'completion_rate': float
        }
    }
}
```text
**Использование в шаблоне:**

```django
{% for course in footer_data.popular_courses %}
    <a href="{{ course.get_absolute_url }}">{{ course.title }}</a>
{% endfor %}

<p>Студентов: {{ footer_data.stats.total_students }}</p>
```text
**Настройка в settings.py:**

```python
TEMPLATES = [
    {
        'OPTIONS': {
            'context_processors': [

                #

                'core.context_processors.footer_data',
            ],
        },
    },
]
```text
---

## 🏷️ Template Tags

### Markdown Filters

**Файл:** `templatetags/markdown_filters.py`

#### `markdown_format`

Конвертирует Markdown текст в HTML.

```django
{% load markdown_filters %}

{{ article.content|markdown_format|safe }}
```text
#### `get_item`

Получает элемент из словаря по ключу.

```django
{{ my_dict|get_item:"key_name" }}
```text
#### `clean_markdown`

Удаляет Markdown разметку, оставляя только текст.

```django
{{ article.content|clean_markdown }}
```text
#### `smart_excerpt`

Создает умную выдержку из текста (первые 150 символов).

```django
{{ article.content|smart_excerpt:150 }}
```text
---

### Article Tags

**Файл:** `templatetags/article_tags.py`

#### `pluralize_articles`

Склонение слова "статья" в зависимости от количества.

```django
{% load article_tags %}

{{ count }} {{ count|pluralize_articles }}

<!-- Вывод:
1 статья
2 статьи
5 статей
-->
```text
---

## 🧪 Тестирование

### Структура тестов

```text
tests/
├── test_api.py                     # 15 тестов
├── test_schemas.py                 # 28 тестов
└── test_response_validation.py     # 10 тестов
```text
**Всего: 53 теста** ✅

---

### test_api.py (15 тестов)

Тестирование API эндпоинтов:

**Feedback API (6 тестов):**

- ✅ `test_create_feedback_success` - успешное создание заявки
- ✅ `test_create_feedback_invalid_phone` - валидация телефона
- ✅ `test_create_feedback_invalid_email` - валидация email
- ✅ `test_create_feedback_short_message` - проверка минимальной длины
- ✅ `test_create_feedback_without_consent` - обязательность согласия
- ✅ `test_create_feedback_name_with_digits` - имя без цифр

**Subscription API (4 теста):**

- ✅ `test_create_subscription_new` - новая подписка
- ✅ `test_create_subscription_already_exists` - дубликат подписки
- ✅ `test_reactivate_inactive_subscription` - реактивация
- ✅ `test_subscription_invalid_email` - валидация email

**Contact Info API (1 тест):**

- ✅ `test_get_contact_info` - получение контактов

**Stats API (3 теста):**

- ✅ `test_get_stats_empty_db` - статистика пустой БД
- ✅ `test_get_stats_with_data` - статистика с данными
- ✅ `test_stats_counts_all_courses` - подсчет курсов

**Integration (1 тест):**

- ✅ `test_full_user_journey` - полный путь пользователя

---

### test_schemas.py (28 тестов)

Тестирование Pydantic схем:

**FeedbackSchema (10 тестов):**

- ✅ Валидация валидных данных
- ✅ Телефон без `+`
- ✅ Телефон с неверным форматом
- ✅ Телефон слишком короткий/длинный
- ✅ Имя с цифрами
- ✅ Сообщение слишком короткое
- ✅ Отказ от согласия
- ✅ Неверный email
- ✅ Пропущенные обязательные поля

**SubscriptionSchema (3 теста):**

- ✅ Валидный email
- ✅ Невалидный email
- ✅ Пропущенный email

**ContactInfoSchema (3 теста):**

- ✅ Полная информация
- ✅ Минимальная информация
- ✅ Пустые социальные ссылки

**StatsSchema (5 тестов):**

- ✅ Валидная статистика
- ✅ Значения по умолчанию
- ✅ Границы completion_rate (0-100)
- ✅ Отрицательные значения (недопустимы)
- ✅ FeedbackResponseSchema

**Response Schemas (7 тестов):**

- ✅ FeedbackResponseSchema
- ✅ SubscriptionResponseSchema
- ✅ Все поля присутствуют

---

### test_response_validation.py (10 тестов)

Тестирование валидации ответов API:

- ✅ `test_feedback_response_validates_success_field`
- ✅ `test_feedback_response_validates_feedback_id`
- ✅ `test_subscription_response_validates_already_subscribed`
- ✅ `test_contact_info_validates_social_links`
- ✅ `test_stats_validates_numeric_fields`
- ✅ `test_stats_validates_completion_rate_bounds`
- ✅ `test_contact_info_requires_email_and_phone`
- ✅ `test_response_schemas_are_immutable_after_creation`
- ✅ `test_pydantic_models_can_be_serialized_to_dict`
- ✅ `test_pydantic_models_can_be_serialized_to_json`

---

### Запуск тестов

```bash

# Все тесты core

pytest src/core/tests/ -v

# Только API тесты

pytest src/core/tests/test_api.py -v

# Только тесты схем

pytest src/core/tests/test_schemas.py -v

# С покрытием кода

pytest src/core/tests/ --cov=core --cov-report=html
```text
---

## 💡 Использование

### Интеграция в проект

1. **Добавить в INSTALLED_APPS:**

```python
INSTALLED_APPS = [

    #

    'core',
]
```text
2. **Подключить URL:**

```python
from django.urls import path, include

urlpatterns = [
    path('', include('core.urls')),
]
```text
3. **Добавить context processor:**

```python
TEMPLATES = [
    {
        'OPTIONS': {
            'context_processors': [
                'core.context_processors.footer_data',
            ],
        },
    },
]
```text
4. **Подключить API к главному роутеру:**

```python

# pyland/api.py

from core.api import router as core_router

api = NinjaAPI()
api.add_router("/core/", core_router)
```text
---

### Примеры использования

#### Отправка обратной связи (AJAX)

```javascript
fetch('/api/core/feedback/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken()
    },
    body: JSON.stringify({
        first_name: 'Иван',
        phone_number: '+79991234567',
        email: 'ivan@example.com',
        message: 'Хочу узнать о курсах',
        agree_terms: true
    })
})
.then(response => response.json())
.then(data => {
    console.log('Заявка создана:', data.feedback_id);
});
```text
---

#### Подписка на рассылку

```javascript
fetch('/api/core/subscribe/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        email: 'user@example.com'
    })
})
.then(response => response.json())
.then(data => {
    if (data.already_subscribed) {
        alert('Вы уже подписаны!');
    } else {
        alert(data.message);
    }
});
```text
---

#### Использование в шаблонах

```django
{% extends "base.html" %}
{% load markdown_filters %}
{% load article_tags %}

{% block content %}
    <!-- Футер данные (из context processor) -->
    <div class="footer">
        <h3>Популярные курсы</h3>
        {% for course in footer_data.popular_courses %}
            <a href="{{ course.get_absolute_url }}">{{ course.title }}</a>
        {% endfor %}

        <p>Всего студентов: {{ footer_data.stats.total_students }}</p>
    </div>

    <!-- Markdown контент -->
    <div class="article-content">
        {{ content|markdown_format|safe }}
    </div>

    <!-- Склонение слова "статья" -->
    <p>Найдено: {{ count }} {{ count|pluralize_articles }}</p>
{% endblock %}
```text
---

---

## � Логирование

### Настройка logger

Все модули используют централизованное логирование:

```python
import logging

logger = logging.getLogger(__name__)
```text
### Уровни логирования

**В views.py:**

```python
logger.info(f"Форма обратной связи отправлена: {form.cleaned_data['email']}")
logger.warning("Попытка подписаться с уже существующим email")
logger.error(f"Ошибка при сохранении feedback: {str(e)}")
```text
**В api.py:**

```python
logger.info(f"API: Создана заявка обратной связи #{feedback.id}")
logger.warning(f"API: Попытка повторной подписки для {email}")
logger.error(f"API: Ошибка при получении статистики: {str(e)}")
```text
**В forms.py:**

```python
logger.debug(f"Валидация телефона: {phone_number}")
logger.warning(f"Имя содержит цифры: {first_name}")
```text
### Конфигурация в settings.py

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/core.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'core': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```text
### Примеры логов

```text
INFO 2025-11-10 core.api API: Создана заявка обратной связи #42
INFO 2025-11-10 core.views Форма обратной связи отправлена: ivan@example.com
WARNING 2025-11-10 core.api API: Попытка повторной подписки для test@example.com
ERROR 2025-11-10 core.views Ошибка при сохранении feedback: Database error
```text
### Логирование в тестах

Тесты автоматически захватывают логи:

```python
import logging

def test_something(caplog):
    with caplog.at_level(logging.INFO):

        # Выполнить действие

        create_feedback(data)

    # Проверить логи

    assert "Создана заявка" in caplog.text
```text
---

## � Кеширование (cache_utils.py)

### Обзор

Модуль `cache_utils.py` предоставляет утилиты для кеширования данных через Redis, аналогично `blog.cache_utils`.

### Основные функции

#### get_cache_key(prefix, *args, **kwargs)

Генерирует уникальный ключ кеша:

```python
from core.cache_utils import get_cache_key

key = get_cache_key('contact_info', user_id=123)

# Результат: 'core:contact_info:a1b2c3d4e5f6'

```text
#### cache_page_data(timeout, key_prefix)

Декоратор для кеширования функций:

```python
from core.cache_utils import cache_page_data

@cache_page_data(timeout=300, key_prefix='contact_info')
def get_contact_info():

    # Тяжелая операция

    return expensive_data()
```text
#### invalidate_core_cache(patterns)

Инвалидирует кеш по паттернам:

```python
from core.cache_utils import invalidate_core_cache

# Инвалидировать конкретный кеш

invalidate_core_cache(['home_page'])

# Инвалидировать весь кеш core

invalidate_core_cache()
```text
### Готовые декораторы

```python
from core.cache_utils import (
    cache_home_page,      # 5 минут
    cache_contact_info,   # 30 минут
    cache_about_page,     # 1 час
    cache_stats,          # 10 минут
    cache_legal_page,     # 24 часа
)

@cache_home_page()
def get_home_data():
    return {'courses': courses, 'features': features}
```text
### Прогрев кеша

```python
from core.cache_utils import warm_cache

# Прогреть популярные данные

warm_cache()  # Кеширует топ курсы и статистику
```text
### Конфигурация в settings.py

```python

# Настройка таймаутов кеша

CACHE_TTL = {
    'home_page': 300,      # 5 минут
    'contact_info': 1800,  # 30 минут
    'about_page': 3600,    # 1 час
    'stats': 600,          # 10 минут
    'legal_page': 86400,   # 24 часа
}

# Redis настройки

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```text
---

## 🛡️ Middleware (middleware.py)

### CoreRateLimitMiddleware

Ограничивает частоту запросов к API для защиты от злоупотреблений.

#### Конфигурация

Добавьте в `settings.py`:

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Core middleware

    'core.middleware.CoreRateLimitMiddleware',  # ⭐ Rate limiting
    'core.middleware.CoreSecurityHeadersMiddleware',  # ⭐ Security headers
]
```text
#### Настройка лимитов

```python

# Лимиты для Core API (по умолчанию)

CORE_API_RATE_LIMITS = {
    'anonymous': {
        'requests': 50,   # 50 запросов
        'window': 3600    # в час
    },
    'authenticated': {
        'requests': 200,  # 200 запросов
        'window': 3600    # в час
    }
}

# Пути для проверки

CORE_RATE_LIMIT_PATHS = [
    '/api/core/feedback/',
    '/api/core/subscribe/',
]
```text
#### Ответ при превышении лимита

```json
HTTP 429 Too Many Requests
{
    "error": "Rate limit exceeded",
    "message": "Превышен лимит запросов. Попробуйте снова через 3456 секунд.",
    "retry_after": 3456,
    "limit": 50,
    "window": 3600
}
```text
#### Headers ответа

```text
X-RateLimit-Limit: 50
X-RateLimit-Remaining: 23
X-RateLimit-Reset: 1699876543
```text
### CoreSecurityHeadersMiddleware

Добавляет security headers ко всем ответам:

```text
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
```text
#### Использование

Middleware автоматически добавляет headers, дополнительная настройка не требуется.

### Логирование middleware

```python
import logging
logger = logging.getLogger('core.middleware')

# Логи при превышении лимита

logger.warning(
    f"Rate limit превышен для IP:192.168.1.1 "
    f"на /api/core/feedback/: 51/50"
)

# Логи ошибок

logger.error(f"Ошибка в CoreRateLimitMiddleware: {e}")
```text
---

## 🔄 Обработка исключений

### Views (views.py)

Все view функции обернуты в try-except блоки:

```python
def home(request):
    try:

        # Основная логика

        if request.method == "POST":
            try:
                feedback = Feedback.objects.create(**form.cleaned_data)
                logger.info(f"Форма отправлена: {email}")
            except Exception as e:
                logger.error(f"Ошибка создания feedback: {e}")
                messages.error(request, "Произошла ошибка...")

        # Получение курсов

        try:
            courses = Course.objects.annotate(...)[:4]
        except Exception as e:
            logger.error(f"Ошибка получения курсов: {e}")
            courses = []

    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        return render(request, template, fallback_context)
```text
### API (api.py)

Все API endpoints защищены:

```python
@router.post("/feedback/")
def create_feedback(request, data: FeedbackSchema):
    try:
        feedback = Feedback.objects.create(...)
        logger.info(f"API: Создана заявка #{feedback.id}")
        return FeedbackResponseSchema(success=True, ...)
    except Exception as e:
        logger.error(f"API: Ошибка создания: {e}")
        return FeedbackResponseSchema(
            success=False,
            message="Произошла ошибка...",
            feedback_id=None
        )
```text
### Преимущества

✅ Graceful degradation - сайт продолжает работать при ошибках
✅ Подробное логирование для отладки
✅ Понятные сообщения пользователю
✅ Fallback данные при сбоях БД
✅ Аналогично архитектуре blog приложения

---

## �📚 Дополнительная документация

**Core приложение:**

- [Templates README](templates/README.md) - HTML шаблоны (5 страниц)
- [Template Tags README](templatetags/README.md) - Custom tags (2 модуля)
- [Tests README](tests/README.md) - Юнит тесты (53 теста)

**Static файлы:**

- [CSS Architecture](../../static/css/core/README.md) - Архитектура стилей
- [JavaScript Documentation](../../static/js/core/README.md) - JS скрипты

**Другое:**

- [Legal Pages README](LEGAL_PAGES_REDESIGN.md) - Юридические страницы

---

## 🤝 Вклад в проект

При добавлении нового функционала в `core`:

1. ✅ Добавьте docstrings ко всем функциям/классам
2. ✅ Используйте type hints для всех параметров
3. ✅ Добавьте Pydantic схемы для API эндпоинтов
4. ✅ Напишите тесты для новой функциональности
5. ✅ Оберните код в try-except с логированием
6. ✅ Обновите этот README.md

---

## 📝 Лицензия

Pyland Platform © 2025
