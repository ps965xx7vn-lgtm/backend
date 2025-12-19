# Manager Application

Административное приложение для управления платформой Pyland.

## 📋 Содержание

- [Обзор](#обзор)
- [Модели](#модели)
- [API Endpoints](#api-endpoints)
- [Кеширование](#кеширование)
- [Middleware](#middleware)
- [Использование](#использование)

## 🎯 Обзор

Manager - это полнофункциональное административное приложение для управления:

- **Обратной связью** от пользователей
- **Системными логами** и событиями
- **Настройками платформы**

### Особенности

- ✅ REST API на Django Ninja
- ✅ Кеширование в Redis (TTL: 5-10 минут)
- ✅ Rate limiting (50/200 req/час)
- ✅ Security headers
- ✅ Полные русские докстринги
- ✅ Type hints везде
- ✅ Индексы БД для производительности

## 📊 Модели

### Feedback

Модель для хранения обращений пользователей.

```python
from manager.models import Feedback

# Создание обращения

feedback = Feedback.objects.create(
    first_name='Иван',
    phone_number='+79001234567',
    email='ivan@example.com',
    message='У меня вопрос по курсам'
)

# Получение необработанных

unprocessed = Feedback.objects.filter(is_processed=False)

# Отметить как обработанное

feedback.is_processed = True
feedback.processed_by = request.user
feedback.processed_at = timezone.now()
feedback.save()
```text
**Поля:**

- `first_name` - Имя пользователя (max 50)
- `phone_number` - Номер телефона (max 16)
- `email` - Email адрес (indexed)
- `message` - Текст сообщения
- `registered_at` - Дата создания (indexed, auto)
- `is_processed` - Флаг обработки (indexed)
- `processed_by` - FK к User
- `processed_at` - Дата обработки
- `admin_notes` - Заметки администратора

### SystemLog

Модель для логирования административных действий.

```python
from manager.models import SystemLog

# Логирование события

SystemLog.objects.create(
    level='INFO',
    action_type='USER_LOGIN',
    user=request.user,
    ip_address='192.168.1.100',
    user_agent=request.META.get('HTTP_USER_AGENT'),
    message='Успешный вход в систему',
    details={'method': 'password'}
)

# Получение критических ошибок

critical_logs = SystemLog.objects.filter(
    level='CRITICAL',
    created_at__gte=hour_ago
)
```text
**Уровни логов:**

- `DEBUG` - Отладочная информация
- `INFO` - Информационные сообщения
- `WARNING` - Предупреждения
- `ERROR` - Ошибки
- `CRITICAL` - Критические ошибки

**Типы действий:**

- `USER_LOGIN/LOGOUT/REGISTERED/UPDATED/DELETED`
- `FEEDBACK_CREATED/UPDATED/DELETED`
- `SETTINGS_UPDATED`
- `COURSE_CREATED/UPDATED/DELETED`
- `PAYMENT_PROCESSED`
- `ERROR_OCCURRED`
- `SECURITY_EVENT`

### SystemSettings

Модель для динамических настроек платформы.

```python
from manager.models import SystemSettings

# Создание настройки

setting = SystemSettings.objects.create(
    key='max_upload_size',
    value='10485760',  # 10 MB
    value_type='integer',
    description='Максимальный размер файла',
    is_public=False
)

# Получение типизированного значения

max_size = setting.get_typed_value()  # int: 10485760

# Получение публичных настроек

public_settings = SystemSettings.objects.filter(is_public=True)
```text
**Типы значений:**

- `string` - Строки
- `integer` - Целые числа
- `boolean` - Логические (true/false)
- `json` - JSON структуры

## 🌐 API Endpoints

**ВАЖНО:** Все эндпоинты требуют `@staff_member_required` (права администратора).

### Как увидеть в Swagger UI (/api/docs)

Manager endpoints видны только авторизованным staff пользователям:

1. **Создать superuser:**

   ```bash
   cd src
   poetry run python manage.py createsuperuser
   ```

2. **Запустить сервер:**

   ```bash
   poetry run python manage.py runserver
   ```

3. **Авторизоваться:**
   - Откройте <http://127.0.0.1:8000/admin/>
   - Войдите под admin учетными данными

4. **Открыть Swagger UI:**
   - Перейдите на <http://127.0.0.1:8000/api/docs>
   - Найдите секцию "Manager" в списке tags
   - Swagger автоматически использует вашу admin сессию

### Список эндпоинтов

### GET /api/managers/feedback/

Получить список обращений с пагинацией.

**Query параметры:**

- `page` (int, default=1) - Номер страницы
- `page_size` (int, default=20) - Размер страницы
- `search` (str, optional) - Поиск по имени, email, сообщению

**Пример запроса:**

```bash
curl -H "Authorization: Bearer <token>" \
  "<http://localhost:8000/api/managers/feedback/?page=1&page_size=20&search=иван">
```text
**Пример ответа:**

```json
{
  "items": [
    {
      "id": 1,
      "first_name": "Иван",
      "email": "ivan@example.com",
      "phone_number": "+79001234567",
      "message": "Вопрос по курсам",
      "registered_at": "2025-01-15T10:30:45Z",
      "is_processed": false
    }
  ],
  "total": 42,
  "page": 1,
  "page_size": 20,
  "total_pages": 3
}
```text
### GET /api/managers/feedback/{id}/

Получить детали одного обращения.

**Пример запроса:**

```bash
curl -H "Authorization: Bearer <token>" \
  "<http://localhost:8000/api/managers/feedback/1/">
```text
**Пример ответа:**

```json
{
  "id": 1,
  "first_name": "Иван",
  "email": "ivan@example.com",
  "phone_number": "+79001234567",
  "message": "Вопрос по курсам Python",
  "registered_at": "2025-01-15T10:30:45Z",
  "is_processed": false
}
```text
### DELETE /api/managers/feedback/{id}/

Удалить обращение (только staff).

**Пример запроса:**

```bash
curl -X DELETE \
  -H "Authorization: Bearer <token>" \
  "<http://localhost:8000/api/managers/feedback/1/">
```text
**Пример ответа:**

```json
{
  "success": true,
  "message": "Обращение успешно удалено",
  "id": 1
}
```text
### GET /api/managers/feedback/stats/

Получить статистику по обращениям.

**Query параметры:**

- `recent_count` (int, default=5) - Количество последних обращений

**Пример запроса:**

```bash
curl -H "Authorization: Bearer <token>" \
  "<http://localhost:8000/api/managers/feedback/stats/?recent_count=10">
```text
**Пример ответа:**

```json
{
  "total_feedback": 142,
  "today_feedback": 5,
  "this_week_feedback": 23,
  "this_month_feedback": 87,
  "average_per_day": 4.7,
  "most_active_day": "понедельник",
  "recent_feedback": [
    {
      "id": 1,
      "first_name": "Иван",
      "email": "ivan@example.com",
      "registered_at": "2025-01-15T10:30:45Z"
    }
  ]
}
```text
## 💾 Кеширование

### Конфигурация

Redis используется для всех кеш операций:

```python

# settings.py

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://localhost:6379/1',
        'KEY_PREFIX': 'pyland',
        'TIMEOUT': 300,  # 5 минут
    }
}
```text
### TTL (Time To Live)

- **Статистика обратной связи:** 600 сек (10 минут)
- **Список обращений:** 300 сек (5 минут)

### Использование

```python
from manager.cache_utils import (
    get_cached_feedback_stats,
    invalidate_feedback_cache,
    warm_feedback_cache
)

# Получить кешированную статистику

stats = get_cached_feedback_stats(recent_count=10)

# Инвалидировать кеш после изменений

invalidate_feedback_cache()

# Прогрев кеша

warm_feedback_cache()
```text
### Паттерны ключей

- `manager:feedback_stats:recent_count=<N>` - Статистика
- `manager:feedback_list:page=<N>&page_size=<M>&search=<Q>` - Списки

### MD5 хеширование

Длинные ключи (>200 символов) автоматически хешируются:

```python
from manager.cache_utils import get_cache_key

key = get_cache_key('manager', 'feedback_list',
                    page=1, page_size=20, search='очень длинный поисковый запрос')

# Результат: "manager:feedback_list:a1b2c3d4..." (MD5 хеш параметров)

```text
## 🛡️ Middleware

### ManagerRateLimitMiddleware

Ограничивает частоту запросов к `/api/managers/*` эндпоинтам.

**Лимиты:**

- Анонимные: 50 запросов/час
- Авторизованные: 200 запросов/час
- Staff: без ограничений

**Активация:**

```python

# settings.py

MIDDLEWARE = [
    ...
    'manager.middleware.ManagerRateLimitMiddleware',
]
```text
**Пример ответа при превышении:**

```json
{
  "error": "Rate limit exceeded",
  "detail": "Максимум 50 запросов в час",
  "retry_after": 3600
}
```text
### ManagerSecurityHeadersMiddleware

Добавляет заголовки безопасности к ответам `/api/managers/*` и `/managers/*`.

**Заголовки:**

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`

**Активация:**

```python

# settings.py

MIDDLEWARE = [
    ...
    'manager.middleware.ManagerSecurityHeadersMiddleware',
]
```text
## 🚀 Использование

### Настройка

1. **Добавить в INSTALLED_APPS:**

```python

# settings.py

INSTALLED_APPS = [
    ...
    'manager',
]
```text
2. **Подключить middleware:**

```python

# settings.py

MIDDLEWARE = [
    ...
    'manager.middleware.ManagerRateLimitMiddleware',
    'manager.middleware.ManagerSecurityHeadersMiddleware',
]
```text
3. **Подключить URLs:**

```python

# pyland/urls.py

from manager.api import router as manager_router

urlpatterns = [
    ...
    path('api/', manager_router.urls),
]
```text
4. **Применить миграции:**

```bash
poetry run python manage.py migrate manager
```text
5. **Запустить Redis:**

```bash
redis-server --daemonize yes
```text
### Создание superuser

```bash
poetry run python manage.py createsuperuser
```text
### Тестирование

```bash

# Запустить тесты middleware

poetry run python test_manager_middleware.py

# Запустить unit tests

poetry run pytest managers/tests/
```text
### Производственное развертывание

1. **Настроить Redis cluster:**

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': [
            'redis://redis-1:6379/1',
            'redis://redis-2:6379/1',
        ],
    }
}
```text
2. **Настроить rate limits:**

```python

# Увеличить лимиты для production

MANAGER_RATE_LIMITS = {
    'anonymous': {'limit': 100, 'window': 3600},
    'authenticated': {'limit': 500, 'window': 3600},
}
```text
3. **Настроить логирование:**

```python
LOGGING = {
    'loggers': {
        'manager': {
            'handlers': ['file', 'sentry'],
            'level': 'INFO',
        },
    },
}
```text
## 📝 Примеры использования

### Работа с обратной связью в коде

```python
from manager.models import Feedback
from django.utils import timezone

# Получить все необработанные

unprocessed = Feedback.objects.filter(is_processed=False)

# Массовое обновление

Feedback.objects.filter(
    is_processed=False,
    registered_at__lt=timezone.now() - timedelta(days=7)
).update(
    is_processed=True,
    processed_by=admin_user,
    admin_notes='Автоматическая обработка старых обращений'
)
```text
### Логирование событий

```python
from manager.models import SystemLog

def my_view(request):

    # Ваш код

    result = perform_action()

    # Логирование

    SystemLog.objects.create(
        level='INFO',
        action_type='CUSTOM_ACTION',
        user=request.user,
        ip_address=get_client_ip(request),
        message=f'Выполнено действие: {result}',
        details={'result': result, 'duration': 1.5}
    )
```text
### Управление настройками

```python
from manager.models import SystemSettings

# Получить настройку

try:
    setting = SystemSettings.objects.get(key='maintenance_mode')
    is_maintenance = setting.get_typed_value()  # bool
except SystemSettings.DoesNotExist:
    is_maintenance = False

# Обновить настройку

setting.value = 'true'
setting.updated_by = request.user
setting.save()
```text
## 🔧 Разработка

### Структура файлов

```text
managers/
├── __init__.py
├── admin.py              # Django admin конфигурация
├── api.py                # REST API endpoints (Django Ninja)
├── apps.py               # App конфигурация
├── cache_utils.py        # Утилиты кеширования
├── forms.py              # Django формы
├── middleware.py         # Rate limiting и security
├── models.py             # Модели данных
├── schemas.py            # Pydantic схемы
├── urls.py               # URL routing (Django views)
├── views.py              # Django views (dashboard)
├── migrations/           # Миграции БД
├── templates/            # HTML шаблоны
├── tests/                # Unit tests
└── README.md             # Документация
```text
### Стиль кода

- ✅ Русские докстринги в стиле Poetry
- ✅ Type hints везде
- ✅ PEP 8 compliant
- ✅ Примеры в докстрингах

### Добавление нового эндпоинта

1. Создать Pydantic схему в `schemas.py`
2. Добавить endpoint в `api.py` с декоратором `@staff_member_required`
3. Добавить кеширование в `cache_utils.py` при необходимости
4. Написать тесты

## 📚 Связанные модули

- **core** - Использует `Feedback` для публичной формы обратной связи
- **blog** - Может логировать события через `SystemLog`
- **account** - Связь через `User` модель

## 🐛 Отладка

### Проверка кеша

```bash

# Подключиться к Redis

redis-cli

# Посмотреть все ключи manager

KEYS pyland:manager:*

# Получить значение

GET pyland:manager:feedback_stats:recent_count=5

# Очистить кеш manager

DEL pyland:manager:feedback_stats:*
```text
### Проверка rate limits

```bash

# Посмотреть текущие лимиты

redis-cli KEYS pyland:manager:rate_limit:*

# Сбросить лимит для пользователя

redis-cli DEL pyland:manager:rate_limit:user_123
```text
## 📄 Лицензия

Pyland Internal - 2025

## 👥 Авторы

Pyland Team
