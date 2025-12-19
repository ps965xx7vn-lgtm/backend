# Students Middleware - Quick Setup Guide

## 🚀 Быстрая установка

### 1. Добавить middleware в settings.py

```python

# pyland/settings.py

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # ... другие middleware

    # Students middleware - добавить в конец

    'students.middleware.StudentsRateLimitMiddleware',         # Rate limiting
    'students.middleware.StudentsSecurityHeadersMiddleware',   # Security headers
    'students.middleware.ProgressCacheMiddleware',             # Cache monitoring
    'students.middleware.CacheHitCounterMiddleware',           # Cache logging
]
```text
### 2. Настроить rate limits (опционально)

```python

# pyland/settings.py

# Лимиты для аутентифицированных пользователей (по умолчанию 1000)

STUDENTS_RATE_LIMIT_AUTHENTICATED = 1000  # запросов в час

# Лимиты для анонимных пользователей (по умолчанию 100)

STUDENTS_RATE_LIMIT_ANONYMOUS = 100       # запросов в час
```text
### 3. Настроить Redis для кэша (если не настроен)

```python

# pyland/settings.py

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'pyland_students',
        'TIMEOUT': 3600,
    }
}
```text
### 4. Настроить логирование (опционально)

```python

# pyland/settings.py

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'students.middleware': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```text
---

## ✅ Проверка установки

### 1. Проверить Django конфигурацию

```bash
cd src
python manage.py check
```text
**Ожидаемый результат:**

```text
System check identified no issues (0 silenced).
```text
### 2. Проверить Redis подключение

```bash
redis-cli ping
```text
**Ожидаемый результат:**

```text
PONG
```text
### 3. Тестовый запрос

```bash

# Запустить сервер

python manage.py runserver

# В другом терминале

curl -i <http://localhost:8000/students/dashboard/>
```text
**Ожидаемые headers:**

```text
HTTP/1.1 302 Found  (redirect to login)
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1704067200
```text
### 4. Проверка rate limiting

```bash

# Скрипт для теста rate limit (100 запросов)

for i in {1..101}; do
    curl -s -o /dev/null -w "Request $i: %{http_code}\n" \
         <http://localhost:8000/students/dashboard/>
done
```text
**Ожидаемый результат:**

- Первые 100 запросов: `302` (или `200` если авторизован)
- 101-й запрос: `429` (Too Many Requests)

---

## 🎯 Функциональность

### ✅ StudentsRateLimitMiddleware

**Что делает:**

- Защищает `/students/*` endpoints от злоупотреблений
- Лимит: 1000 req/hour для аутентифицированных, 100 для анонимных
- Возвращает HTTP 429 при превышении

**Проверка работы:**

```bash

# Смотрим headers

curl -i <http://localhost:8000/students/dashboard/>

# Ищем

X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
```text
### ✅ StudentsSecurityHeadersMiddleware

**Что делает:**

- Добавляет security headers для защиты от XSS, clickjacking, MIME-sniffing
- X-Frame-Options: DENY (студенческая зона не должна встраиваться)
- Content-Security-Policy: строгая политика для приватной зоны

**Проверка работы:**

```bash
curl -i <http://localhost:8000/students/dashboard/>

# Ищем

X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Content-Security-Policy: default-src 'self'; ...
```text
### ✅ ProgressCacheMiddleware

**Что делает:**

- Добавляет headers с информацией о кэше (только в DEBUG=True)
- Показывает статистику кэширования и время ответа

**Проверка работы:**

```bash

# В settings.py установить DEBUG = True

curl -i <http://localhost:8000/students/dashboard/>

# Ищем (только в DEBUG режиме)

X-Cache-Stats: 5/10 cached (50.0%)
X-Cache-Performance: 0.123s
```text
### ✅ CacheHitCounterMiddleware

**Что делает:**

- Логирует операции с кэшем (hits/misses)
- Помогает анализировать эффективность кэша

**Проверка работы:**

```bash

# Смотрим логи при запросах

tail -f logs/django.log | grep "Cache"

# Ожидаемые логи

Cache HIT for key: progress_user_123 (from get)
Cache MISS for key: dashboard_user_456 (from get)
```text
---

## 🔧 Настройка под проект

### Изменить лимиты для API

```python

# settings.py - для API endpoints увеличить лимиты

STUDENTS_RATE_LIMIT_AUTHENTICATED = 5000  # API users
STUDENTS_RATE_LIMIT_ANONYMOUS = 500       # Public API
```text
### Отключить кэш headers в production

```python

# settings.py

DEBUG = False  # ProgressCacheMiddleware автоматически не добавляет headers
```text
### Настроить whitelist IP

Создать custom middleware для whitelist:

```python

# students/middleware.py

class StudentsRateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.whitelist_ips = getattr(settings, 'RATE_LIMIT_WHITELIST_IPS', [])

    def __call__(self, request):

        # Пропустить whitelist IP

        client_ip = self._get_client_ip(request)
        if client_ip in self.whitelist_ips:
            return self.get_response(request)

        # Обычная проверка rate limit

        ...
```text
```python

# settings.py

RATE_LIMIT_WHITELIST_IPS = [
    '127.0.0.1',
    '10.0.0.5',  # Monitoring server
]
```text
---

## 🐛 Troubleshooting

### Проблема: "Redis connection error"

**Решение:**

1. Проверить, что Redis запущен:

```bash
redis-cli ping

# Должно вернуть: PONG

```text
2. Если Redis не установлен:

```bash

# macOS

brew install redis
brew services start redis

# Ubuntu

sudo apt-get install redis-server
sudo systemctl start redis
```text
3. Проверить CACHES в settings.py

### Проблема: Rate limit не работает

**Решение:**

1. Проверить, что middleware зарегистрирован:

```python

# settings.py

'students.middleware.StudentsRateLimitMiddleware' in MIDDLEWARE
```text
2. Проверить, что путь начинается с `/students/`:

```python

# Rate limit применяется только к /students/* маршрутам

```text
3. Проверить логи:

```bash
tail -f logs/django.log | grep "Rate limit"
```text
### Проблема: Headers не появляются

**Для X-Cache-* headers:**

- Проверить `DEBUG = True` (headers только в debug режиме)

**Для X-RateLimit-* headers:**

- Должны быть всегда, проверить запрос к `/students/*`

### Проблема: Middleware конфликтует с другими

**Решение:**
Порядок middleware важен:

```python
MIDDLEWARE = [
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # Сначала auth
    'students.middleware.StudentsRateLimitMiddleware',          # Потом rate limit
    'students.middleware.ProgressCacheMiddleware',              # Потом кэш
]
```text
---

## 📊 Мониторинг

### Логи rate limiting

```bash

# Смотреть превышения лимита

tail -f logs/django.log | grep "Rate limit exceeded"

# Ожидаемый формат

Rate limit exceeded for User:123 on /students/courses/: 1001/1000
```text
### Логи кэша

```bash

# Смотреть операции с кэшем

tail -f logs/django.log | grep "Cache"

# Ожидаемый формат

Cache HIT for key: progress_user_123 (from get)
Cache MISS for key: dashboard_user_456 (from get)
```text
### Метрики в реальном времени

```bash

# Подключиться к Redis и мониторить

redis-cli monitor | grep "students_rate_limit"

# Видеть операции

1704067200.123 [1 127.0.0.1:50123] "GET" "students_rate_limit_user_123"
1704067200.456 [1 127.0.0.1:50123] "INCR" "students_rate_limit_user_123"
```text
---

## 📚 Дополнительная информация

### Полная документация

- [MIDDLEWARE_README.md](./MIDDLEWARE_README.md) - детальная документация
- [README.md](./README.md) - общая информация о students app

### Примеры использования

```python

# Проверка оставшихся запросов

from django.core.cache import cache

user_key = f"students_rate_limit_user_{user.id}"
current_requests = cache.get(user_key, 0)
remaining = 1000 - current_requests

print(f"Remaining requests: {remaining}")
```text
### Best Practices

1. **В production отключить DEBUG** - ProgressCacheMiddleware не добавит лишние headers
2. **Мониторить логи** - следить за превышениями rate limit
3. **Настроить Redis для production** - connection pooling, persistence
4. **Использовать версионирование ключей** - легкая инвалидация кэша

---

## ✨ Готово

Middleware настроен и работает. Проверьте:

- ✅ Redis подключен и доступен
- ✅ Middleware зарегистрирован в settings.py
- ✅ Rate limiting работает (видны X-RateLimit-* headers)
- ✅ Логи пишутся корректно

**Вопросы?** См. [MIDDLEWARE_README.md](./MIDDLEWARE_README.md) для детальной информации.

---

**Автор**: Pyland Team
**Дата**: 2025-01-01
