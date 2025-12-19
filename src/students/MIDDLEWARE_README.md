# Students Middleware Documentation

## Обзор

Модуль `students.middleware` содержит четыре middleware компонента для
защиты, мониторинга и оптимизации студентских endpoints:

1. **StudentsRateLimitMiddleware** - защита от злоупотреблений через rate limiting
2. **StudentsSecurityHeadersMiddleware** - добавление security headers для
   защиты от XSS и других атак
3. **ProgressCacheMiddleware** - мониторинг производительности кэша (debug режим)
4. **CacheHitCounterMiddleware** - подсчет попаданий/промахов кэша для аналитики

---

## StudentsRateLimitMiddleware

### Назначение RateLimitMiddleware

Защищает студентские endpoints (`/students/*`) от злоупотреблений,
ограничивая количество запросов:

- **Аутентифицированные пользователи**: 1000 запросов/час
- **Анонимные пользователи**: 100 запросов/час

### Конфигурация RateLimitMiddleware

```python

# settings.py

MIDDLEWARE = [
    ...
    'students.middleware.StudentsRateLimitMiddleware',
    'students.middleware.StudentsSecurityHeadersMiddleware',
]

# Опционально: настройка лимитов

STUDENTS_RATE_LIMIT_AUTHENTICATED = 1000  # запросов в час
STUDENTS_RATE_LIMIT_ANONYMOUS = 100       # запросов в час
```text
### Поведение

**При нормальной работе:**

- Добавляет HTTP headers с информацией о лимитах:

  ```text
  X-RateLimit-Limit: 1000
  X-RateLimit-Remaining: 995
  X-RateLimit-Reset: 1704067200
  ```

**При превышении лимита:**

- Возвращает HTTP 429 Too Many Requests:

  ```json
  {
    "error": "Rate limit exceeded",
    "message": "Превышен лимит запросов. Попробуйте снова через 3600 секунд.",
    "retry_after": 3600,
    "limit": 1000,
    "window": 3600
  }
  ```

### Идентификация клиентов

- Аутентифицированные: по `user.id`
- Анонимные: по IP адресу (учитывает `X-Forwarded-For` для прокси)

### Хранилище

Использует Redis для хранения счетчиков с автоматическим TTL. Если Redis
недоступен, middleware gracefully degrade (пропускает запросы).

---

## StudentsSecurityHeadersMiddleware

### Назначение SecurityHeadersMiddleware

Добавляет security headers для защиты студентской зоны от XSS,
clickjacking, MIME-sniffing и других атак.

### Конфигурация SecurityHeadersMiddleware

```python

# settings.py

MIDDLEWARE = [
    ...
    'students.middleware.StudentsSecurityHeadersMiddleware',
]

# Опционально: кастомная CSP политика

STUDENTS_CSP_POLICY = (
    "default-src 'self'; "
    "img-src 'self' data: https:; "
    "style-src 'self' 'unsafe-inline'; "
    "script-src 'self'; "
    "frame-ancestors 'none';"
)
```text
### Добавляемые Headers

**X-Content-Type-Options: nosniff**

- Предотвращает MIME-sniffing в браузерах
- Защищает от атак через загрузку вредоносных файлов

**X-Frame-Options: DENY**

- Запрещает встраивание страниц в iframe
- Защищает от clickjacking атак
- Для студентской зоны установлен DENY (строже чем у blog)

**X-XSS-Protection: 1; mode=block**

- Включает XSS фильтр браузера
- При обнаружении атаки блокирует страницу

**Referrer-Policy: strict-origin-when-cross-origin**

- Контролирует передачу Referer header
- Защищает приватные URL от утечки

**Content-Security-Policy**

- Базовая защита от XSS
- Ограничивает источники скриптов, стилей, изображений
- `frame-ancestors 'none'` - дополнительная защита от iframe

### Отличия от других модулей

| Header | Blog | Core | Students |
|--------|------|------|----------|
| X-Frame-Options | SAMEORIGIN | DENY | DENY |
| script-src | 'unsafe-inline' 'unsafe-eval' | 'self' | 'self' |
| frame-ancestors | не указан | 'none' | 'none' |

**Почему Students строже:**

- Приватная зона с персональными данными
- Не требуется встраивание в iframe
- Минимум inline скриптов для безопасности

---

## ProgressCacheMiddleware

### Назначение ProgressCacheMiddleware

Добавляет HTTP headers с информацией о кэше в DEBUG режиме для мониторинга производительности.

### Конфигурация ProgressCacheMiddleware

```python

# settings.py

MIDDLEWARE = [
    ...
    'students.middleware.ProgressCacheMiddleware',
]
```text
### Поведение

**Только в DEBUG=True:**
Добавляет headers с информацией о кэше:

```text
X-Cache-Stats: 5/10 cached (50.0%)
X-Cache-Performance: 0.123s
```text
**В Production (DEBUG=False):**

- Headers не добавляются (для безопасности)

### Применение

Позволяет разработчикам видеть эффективность кэша:

- Сколько данных кэшировано
- Время ответа сервера
- Процент попаданий в кэш

---

## CacheHitCounterMiddleware

### Назначение CacheHitCounterMiddleware

Подсчитывает и логирует попадания/промахи кэша для аналитики производительности.

### Конфигурация CacheHitCounterMiddleware

```python

# settings.py

MIDDLEWARE = [
    ...
    'students.middleware.CacheHitCounterMiddleware',
]
```text
### Поведение

**Мониторинг ключей:**

- `progress_*` - прогресс обучения студентов
- `dashboard_*` - данные дашборда
- `courses_stats_*` - статистика курсов

**Логирование:**

```python
logger.info("Cache HIT for key: progress_user_123 (from get)")
logger.info("Cache MISS for key: dashboard_user_456 (from get)")
```text
### Обернутые методы

- `cache.get()`
- `cache.get_many()`
- `cache.set()`
- `cache.set_many()`

---

## Вспомогательные функции

### cache_key_versioning()

Генерирует версионированные ключи кэша:

```python
from students.middleware import cache_key_versioning

# Генерация ключа

key = cache_key_versioning('user', user.id, version='v1')

# Результат: 'v1_user_123'

# Использование

cache.set(key, data, timeout=3600)
```text
**Параметры:**

- `prefix` (str): Префикс ключа (например, 'user', 'dashboard')
- `identifier` (int/str): Уникальный идентификатор
- `version` (str): Версия данных (по умолчанию 'v1')

**Преимущества:**

- Легко инвалидировать кэш через изменение версии
- Предотвращает конфликты ключей
- Читаемые имена ключей

---

### get_cache_settings()

Возвращает рекомендуемые настройки Redis для прогресса студентов:

```python
from students.middleware import get_cache_settings

settings = get_cache_settings()
print(settings)

# {

#     'BACKEND': 'django.core.cache.backends.redis.RedisCache'

#     'LOCATION': 'redis://127.0.0.1:6379/1'

#     'OPTIONS': {

#         'CLIENT_CLASS': 'django_redis.client.DefaultClient'

#         'PARSER_CLASS': 'redis.connection.HiredisParser'

#         'CONNECTION_POOL_CLASS': 'redis.connection.BlockingConnectionPool'

#         'SOCKET_CONNECT_TIMEOUT': 5

#         'SOCKET_TIMEOUT': 5

#         'CONNECTION_POOL_KWARGS': {...}

#     }

#     'KEY_PREFIX': 'pyland_students'

#     'TIMEOUT': 3600

# }

```text
**Настройки:**

- DB 1 для изоляции от других кэшей
- Connection pooling для производительности
- Автоматические retry и health checks
- Тайм-ауты для защиты от зависаний

---

### cache_context_processor()

Контекстный процессор для передачи статистики кэша в шаблоны:

```python

# settings.py

TEMPLATES = [
    {
        ...
        'OPTIONS': {
            'context_processors': [
                ...
                'students.middleware.cache_context_processor',
            ],
        },
    },
]
```text
**В шаблонах:**

```django
{% if cache_available %}
    <p>Cache Status: {{ cache_status }}</p>
    <p>Backend: {{ cache_backend }}</p>
{% endif %}
```text
**Переменные:**

- `cache_available` (bool): Доступен ли кэш
- `cache_status` (str): Состояние подключения
- `cache_backend` (str): Используемый backend

---

## Примеры использования

### Пример 1: Проверка rate limit в API

```python
from ninja import Router
from django.http import HttpRequest

router = Router()

@router.get("/courses/")
def get_courses(request: HttpRequest):

    # Rate limit автоматически проверяется middleware

    # При превышении вернется 429 до вызова view

    courses = Course.objects.all()
    return {"courses": list(courses.values())}
```text
**Ответ при превышении лимита:**

```bash
curl -i <http://localhost:8000/students/courses/>
HTTP/1.1 429 Too Many Requests
Content-Type: application/json

{
  "error": "Rate limit exceeded",
  "retry_after": 3600,
  "limit": 1000
}
```text
### Пример 2: Мониторинг кэша в development

```bash

# Запрос с headers в debug режиме

curl -i <http://localhost:8000/students/dashboard/>

HTTP/1.1 200 OK
X-Cache-Stats: 8/12 cached (66.7%)
X-Cache-Performance: 0.045s
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
```text
### Пример 3: Использование версионированных ключей

```python
from students.middleware import cache_key_versioning
from django.core.cache import cache

# Создание ключа

progress_key = cache_key_versioning('progress', user.id, version='v2')

# Сохранение прогресса

cache.set(progress_key, {
    'completed_lessons': 15,
    'current_course': 3,
    'last_activity': '2025-01-01'
}, timeout=3600)

# Получение прогресса

progress = cache.get(progress_key)
```text
---

## Graceful Degradation

Все middleware компоненты поддерживают graceful degradation при недоступности Redis:

```python
try:
    current_requests = cache.get(user_key, 0)
except Exception:

    # Redis недоступен - пропускаем rate limiting

    return self.get_response(request)
```text
**Поведение при отказе Redis:**

- `StudentsRateLimitMiddleware`: пропускает все запросы
- `ProgressCacheMiddleware`: не добавляет headers
- `CacheHitCounterMiddleware`: не логирует операции

**Преимущества:**

- Сайт работает даже без Redis
- Нет падений при проблемах с кэшем
- Логи содержат информацию об ошибках

---

## Тестирование

### Тест rate limiting

```python
import pytest
from django.test import RequestFactory
from students.middleware import StudentsRateLimitMiddleware

def test_rate_limit_authenticated():
    """Тест лимита для аутентифицированных пользователей"""
    factory = RequestFactory()
    middleware = StudentsRateLimitMiddleware(lambda r: HttpResponse())

    request = factory.get('/students/courses/')
    request.user = user_fixture

    # Первые 1000 запросов должны пройти

    for i in range(1000):
        response = middleware(request)
        assert response.status_code == 200

    # 1001-й запрос должен быть заблокирован

    response = middleware(request)
    assert response.status_code == 429
    assert 'retry_after' in response.json()
```text
### Тест кэш headers

```python
def test_cache_headers_in_debug(settings):
    """Тест headers в DEBUG режиме"""
    settings.DEBUG = True

    factory = RequestFactory()
    middleware = ProgressCacheMiddleware(lambda r: HttpResponse())

    request = factory.get('/students/dashboard/')
    response = middleware(request)

    assert 'X-Cache-Stats' in response
    assert 'X-Cache-Performance' in response
```text
---

## Мониторинг и метрики

### Логирование rate limit

```python

# Логи при превышении лимита

logger.warning(
    "Rate limit exceeded for User:123 on /students/courses/: 1001/1000"
)
```text
### Логирование кэша

```python

# Логи операций с кэшем

logger.info("Cache HIT for key: progress_user_123 (from get)")
logger.info("Cache MISS for key: dashboard_user_456 (from get)")
```text
### Prometheus метрики (будущее улучшение)

```python
from prometheus_client import Counter, Histogram

rate_limit_exceeded = Counter(
    'students_rate_limit_exceeded_total',
    'Number of rate limit exceeded responses',
    ['user_type']
)

cache_hit_ratio = Histogram(
    'students_cache_hit_ratio',
    'Cache hit ratio for students endpoints',
    ['key_prefix']
)
```text
---

## Безопасность

### Rate Limiting

- Предотвращает DDoS атаки на студентские endpoints
- Защищает от credential stuffing
- Ограничивает автоматизированные скраперы

### Headers в Production

- `ProgressCacheMiddleware` не добавляет headers в production (DEBUG=False)
- Информация о кэше доступна только в development
- Rate limit headers безопасны (стандарт RFC 6585)

### IP Spoofing Protection

- Использует `X-Forwarded-For` только за доверенным прокси
- Fallback на `REMOTE_ADDR` при отсутствии прокси
- Настройка `SECURE_PROXY_SSL_HEADER` в settings.py

---

## Performance Impact

### StudentsRateLimitMiddleware

- **Redis latency**: ~1-2ms на операцию (get + incr)
- **Overhead**: ~2-4ms на запрос
- **Рекомендации**: Используйте Redis в той же сети для минимальной latency

### ProgressCacheMiddleware

- **Overhead**: < 0.1ms (только чтение времени)
- **DEBUG only**: нет overhead в production

### CacheHitCounterMiddleware

- **Overhead**: < 0.1ms (logging асинхронный)
- **Рекомендации**: Используйте structured logging для анализа

---

## Troubleshooting

### Проблема: Rate limit не работает

**Проверки:**

1. Redis подключен и доступен

```bash
redis-cli ping
```text
2. Middleware зарегистрирован в settings.py

```python
MIDDLEWARE = [
    ...
    'students.middleware.StudentsRateLimitMiddleware',
]
```text
3. Путь начинается с `/students/`

```python
if not request.path.startswith('/students/'):
    return self.get_response(request)
```text
### Проблема: Headers не появляются

**Для ProgressCacheMiddleware:**

- Проверьте `DEBUG = True` в settings.py
- Headers добавляются только в debug режиме

**Для StudentsRateLimitMiddleware:**

- Headers всегда добавляются (X-RateLimit-*)
- Проверьте, что запрос к `/students/*` маршруту

### Проблема: Логи кэша не пишутся

**Проверки:**

1. Logging настроен в settings.py

```python
LOGGING = {
    'loggers': {
        'students.middleware': {
            'level': 'INFO',
            'handlers': ['console'],
        },
    },
}
```text
2. CacheHitCounterMiddleware активен

```python
MIDDLEWARE = [
    ...
    'students.middleware.CacheHitCounterMiddleware',
]
```text
---

## Интеграция с другими компонентами

### С authentication middleware

```python

# Порядок важен: сначала аутентификация, потом rate limit

MIDDLEWARE = [
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'students.middleware.StudentsRateLimitMiddleware',  # использует request.user
]
```text
### С CORS middleware

```python

# CORS должен быть раньше rate limit

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'students.middleware.StudentsRateLimitMiddleware',
]
```text
### С cache_utils

```python
from students.cache_utils import ProgressCacheManager
from students.middleware import cache_key_versioning

# Используйте одинаковое версионирование

manager = ProgressCacheManager()
key = cache_key_versioning('progress', user.id, version='v1')
manager.set(key, data)
```text
---

## Best Practices

1. **Rate Limiting**
   - Настройте лимиты на основе реального трафика
   - Используйте более высокие лимиты для API ключей
   - Логируйте превышения для мониторинга злоупотреблений

2. **Cache Monitoring**
   - Включайте ProgressCacheMiddleware только в development
   - Используйте структурированное логирование для анализа
   - Периодически анализируйте cache hit ratio

3. **Key Versioning**
   - Используйте версии для breaking changes в данных
   - Инвалидируйте кэш через изменение версии
   - Документируйте версии в коде

4. **Error Handling**
   - Всегда используйте graceful degradation
   - Логируйте ошибки Redis для мониторинга
   - Имейте fallback стратегию без кэша

---

## Changelog

### v1.0 (2025-01-01)

- Добавлен StudentsRateLimitMiddleware с поддержкой аутентифицированных и анонимных пользователей
- ProgressCacheMiddleware с headers в debug режиме
- CacheHitCounterMiddleware для мониторинга кэша
- Вспомогательные функции: cache_key_versioning, get_cache_settings, cache_context_processor
- Полная документация и примеры использования

---

## Дополнительные ресурсы

- [Django Middleware Documentation](https://docs.djangoproject.com/en/5.0/topics/http/middleware/)
- [Redis Cache Best Practices](https://redis.io/topics/lru-cache)
- [Rate Limiting Strategies](https://blog.cloudflare.com/rate-limiting-nginx-plus/)
- [RFC 6585 - HTTP Status Code 429](https://tools.ietf.org/html/rfc6585)

---

**Автор**: Pyland Team
**Дата обновления**: 2025-01-01
**Версия**: 1.0
