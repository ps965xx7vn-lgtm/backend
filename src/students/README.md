# Students App - Модуль обучения студентов

## Обзор

**Students** — приложение для управления обучением студентов в Pyland. Включает:

- Dashboard с прогрессом обучения
- Доступ к курсам и урокам
- Статистику выполнения заданий
- API для мобильных приложений
- Middleware для защиты и мониторинга

---

## Структура приложения

```text
students/
├── __init__.py
├── admin.py                 # Админка для моделей студентов
├── api.py                   # Django Ninja REST API
├── apps.py                  # Конфигурация приложения
├── cache_utils.py          # Утилиты для кэширования прогресса
├── decorators.py           # Декораторы для защиты views
├── forms.py                # Формы для работы со студентами
├── middleware.py           # Rate limiting и кэш мониторинг
├── models.py               # Модели для студентов (если нужны)
├── schemas.py              # Pydantic схемы для API
├── tasks.py                # Celery задачи
├── urls.py                 # URL маршруты
├── views.py                # Django views для веб интерфейса
├── templates/              # Шаблоны для студентов
├── tests/                  # Юнит и интеграционные тесты
├── MIDDLEWARE_README.md    # Документация middleware
└── README.md               # Этот файл
```text
---

## Основные компоненты

### 1. API (api.py)

Django Ninja REST API для работы со студентами:

```python
from ninja import Router
from students.schemas import StudentProgressOut

router = Router()

@router.get("/progress/", response=StudentProgressOut)
def get_progress(request):
    """Получить прогресс текущего студента"""
    return {
        "completed_lessons": 15,
        "total_lessons": 50,
        "current_course": "Python Basics",
        "last_activity": "2025-01-01"
    }
```text
**Endpoints:**

- `GET /api/students/progress/` - прогресс обучения
- `GET /api/students/courses/` - доступные курсы
- `GET /api/students/dashboard/` - данные дашборда
- `POST /api/students/submit-homework/` - отправка домашних заданий

### 2. Views (views.py)

Django views для веб интерфейса:

```python
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    """Дашборд студента с прогрессом"""
    return render(request, 'students/dashboard.html', {
        'progress': get_user_progress(request.user),
        'courses': get_available_courses(request.user)
    })
```text
**Маршруты:**

- `/students/dashboard/` - главная страница студента
- `/students/courses/` - список курсов
- `/students/course/<id>/` - детали курса
- `/students/lesson/<id>/` - урок

### 3. Middleware (middleware.py)

Защита и мониторинг для студентских endpoints:

```python
MIDDLEWARE = [
    ...
    'students.middleware.StudentsRateLimitMiddleware',      # Rate limiting
    'students.middleware.StudentsSecurityHeadersMiddleware', # Security headers
    'students.middleware.ProgressCacheMiddleware',          # Cache headers
    'students.middleware.CacheHitCounterMiddleware',        # Cache logging
]
```text
**Возможности:**

- Rate limiting: 1000 req/hour для аутентифицированных, 100 для анонимных
- Security headers: защита от XSS, clickjacking, MIME-sniffing
- Cache monitoring: headers с информацией о кэше (debug режим)
- Graceful degradation: работа без Redis

Подробнее: [MIDDLEWARE_README.md](./MIDDLEWARE_README.md)

### 4. Cache Utils (cache_utils.py)

Утилиты для кэширования прогресса обучения:

```python
from students.cache_utils import ProgressCacheManager

manager = ProgressCacheManager()

# Сохранить прогресс

manager.set_progress(user.id, {
    'completed_lessons': 15,
    'current_course': 3
})

# Получить прогресс

progress = manager.get_progress(user.id)

# Инвалидировать при изменении

manager.invalidate_progress(user.id)
```text
**Фичи:**

- Автоматическое версионирование ключей
- TTL 1 час для прогресса
- Bulk операции для дашборда
- Graceful degradation

### 5. Schemas (schemas.py)

Pydantic схемы для валидации API:

```python
from ninja import Schema

class StudentProgressOut(Schema):
    completed_lessons: int
    total_lessons: int
    current_course: str
    last_activity: str
    completion_rate: float

class HomeworkSubmitIn(Schema):
    lesson_id: int
    answer: str
    files: list[str] | None = None
```text
---

## Установка и настройка

### 1. Добавить в INSTALLED_APPS

```python

# settings.py

INSTALLED_APPS = [
    ...
    'students',
]
```text
### 2. Настроить middleware

```python

# settings.py

MIDDLEWARE = [
    ...
    'students.middleware.StudentsRateLimitMiddleware',
    'students.middleware.StudentsSecurityHeadersMiddleware',
    'students.middleware.ProgressCacheMiddleware',
    'students.middleware.CacheHitCounterMiddleware',
]

# Опционально: изменить лимиты

STUDENTS_RATE_LIMIT_AUTHENTICATED = 1000  # запросов в час
STUDENTS_RATE_LIMIT_ANONYMOUS = 100       # запросов в час

# Опционально: кастомная CSP политика

STUDENTS_CSP_POLICY = "default-src 'self'; ..."
```text
### 3. Добавить URL маршруты

```python

# urls.py

from django.urls import path, include

urlpatterns = [
    ...
    path('students/', include('students.urls')),
    path('api/students/', students_api),  # Django Ninja
]
```text
### 4. Настроить Redis для кэша

```python

# settings.py

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
### 5. Запустить миграции

```bash
python manage.py migrate students
```text
---

## Использование

### Пример 1: Получение прогресса через API

```bash

# Аутентификация

curl -X POST <http://localhost:8000/api/auth/token/> \
  -H "Content-Type: application/json" \
  -d '{"username": "student", "password": "pass123"}'

# Получение прогресса

curl <http://localhost:8000/api/students/progress/> \
  -H "Authorization: Bearer YOUR_TOKEN"
```text
**Ответ:**

```json
{
  "completed_lessons": 15,
  "total_lessons": 50,
  "current_course": "Python Basics",
  "last_activity": "2025-01-01",
  "completion_rate": 30.0
}
```text
### Пример 2: Веб интерфейс

```python

# students/views.py

@login_required
def dashboard(request):
    """Дашборд студента"""
    cache_manager = ProgressCacheManager()

    # Попытка получить из кэша

    progress = cache_manager.get_progress(request.user.id)

    if not progress:

        # Загрузка из БД при cache miss

        progress = calculate_progress(request.user)
        cache_manager.set_progress(request.user.id, progress)

    return render(request, 'students/dashboard.html', {
        'progress': progress,
        'courses': get_available_courses(request.user)
    })
```text
### Пример 3: Rate Limiting

```python

# Rate limit автоматически применяется к /students/* маршрутам

@login_required
def submit_homework(request, lesson_id):
    """Отправка домашнего задания"""

    # При превышении лимита middleware вернет 429 до вызова view

    homework = Homework.objects.create(
        student=request.user,
        lesson_id=lesson_id,
        answer=request.POST['answer']
    )

    # Инвалидировать кэш прогресса

    cache_manager = ProgressCacheManager()
    cache_manager.invalidate_progress(request.user.id)

    return redirect('students:dashboard')
```text
---

## Интеграция с другими приложениями

### С Authentication

```python

# Используем модели из students

from students.models import Student

def get_student_profile(user) -> Student:
    """Получить профиль студента"""
    return user.student
```text
### С Courses

```python

# Доступ к курсам из students

from courses.models import Course, Lesson

def get_available_courses(user: User) -> list[Course]:
    """Получить доступные курсы для студента"""
    return Course.objects.filter(
        is_published=True,
        students=user
    )
```text
### С Notifications

```python

# Уведомления о прогрессе

from notifications.utils import send_notification

def notify_course_completion(user: User, course: Course):
    """Уведомить о завершении курса"""
    send_notification(
        user=user,
        title=f"Поздравляем! Курс '{course.title}' завершен",
        message=f"Вы получили сертификат о прохождении курса"
    )
```text
---

## Тестирование

### Юнит тесты

```python

# students/tests/test_api.py

import pytest
from django.test import Client

@pytest.mark.django_db
def test_get_progress_authenticated():
    """Тест получения прогресса аутентифицированным пользователем"""
    client = Client()
    user = User.objects.create_user('student', 'test@test.com', 'pass123')
    client.force_login(user)

    response = client.get('/api/students/progress/')

    assert response.status_code == 200
    assert 'completed_lessons' in response.json()

@pytest.mark.django_db
def test_rate_limit():
    """Тест rate limiting для анонимных пользователей"""
    client = Client()

    # Первые 100 запросов должны пройти

    for i in range(100):
        response = client.get('/students/dashboard/')
        assert response.status_code in [200, 302]  # 302 redirect to login

    # 101-й запрос должен быть заблокирован

    response = client.get('/students/dashboard/')
    assert response.status_code == 429
```text
### Интеграционные тесты

```python

# students/tests/test_views.py

import pytest
from django.test import Client

@pytest.mark.django_db
def test_dashboard_with_cache():
    """Тест дашборда с использованием кэша"""
    client = Client()
    user = User.objects.create_user('student', 'test@test.com', 'pass123')
    client.force_login(user)

    # Первый запрос - cache miss

    response = client.get('/students/dashboard/')
    assert response.status_code == 200

    # Второй запрос - cache hit

    response = client.get('/students/dashboard/')
    assert response.status_code == 200

    # Проверяем headers в debug режиме

    if settings.DEBUG:
        assert 'X-Cache-Stats' in response
```text
---

## Performance

### Кэширование

- **Прогресс студента**: кэш 1 час, инвалидация при изменении
- **Список курсов**: кэш 30 минут, инвалидация при публикации нового курса
- **Статистика дашборда**: кэш 5 минут, агрегация по нескольким ключам

### Rate Limiting

- **Аутентифицированные**: 1000 req/hour (достаточно для активного использования)
- **Анонимные**: 100 req/hour (защита от скрапинга)
- **Overhead**: ~2-4ms на запрос (Redis latency)

### Оптимизация запросов

```python

# Используйте select_related для FK

courses = Course.objects.select_related('author').all()

# Используйте prefetch_related для M2M

courses = Course.objects.prefetch_related('lessons').all()

# Кэшируйте тяжелые вычисления

@cached(timeout=3600, key_prefix='course_stats')
def get_course_statistics(course_id):

    # Тяжелые вычисления

    pass
```text
---

## Мониторинг и логирование

### Логирование

```python

# settings.py

LOGGING = {
    'loggers': {
        'students': {
            'level': 'INFO',
            'handlers': ['console', 'file'],
            'propagate': False,
        },
        'students.middleware': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}
```text
### Метрики

```python

# Логи rate limiting

logger.warning(
    f"Rate limit exceeded for User:{user.id} "
    f"on {request.path}: {count}/{limit}"
)

# Логи кэша

logger.info(f"Cache HIT for key: progress_user_{user.id}")
logger.info(f"Cache MISS for key: dashboard_user_{user.id}")
```text
---

## Безопасность

### Защита endpoints

```python

# Используйте decorators для проверки прав доступа

from django.contrib.auth.decorators import login_required

@login_required
def student_only_view(request):
    """View только для студентов"""
    if not request.user.student.roles.filter(name='student').exists():
        return HttpResponseForbidden()

    return render(request, 'students/dashboard.html')
```text
### Rate Limiting

- Защита от DDoS атак
- Предотвращение credential stuffing
- Ограничение автоматизированных скраперов

### Валидация данных

```python

# Используйте Pydantic схемы для API

class HomeworkSubmitIn(Schema):
    lesson_id: int = Field(..., gt=0)
    answer: str = Field(..., min_length=1, max_length=10000)
    files: list[str] | None = Field(None, max_length=5)
```text
---

## Troubleshooting

### Проблема: Кэш не работает

**Решение:**

1. Проверьте подключение к Redis:

```bash
redis-cli ping
```text
2. Проверьте настройки кэша в settings.py
3. Включите логирование кэша для отладки

### Проблема: Rate limit слишком строгий

**Решение:**

```python

# settings.py

STUDENTS_RATE_LIMIT_AUTHENTICATED = 2000  # увеличить лимит
```text
### Проблема: Медленные запросы

**Решение:**

1. Используйте select_related/prefetch_related
2. Добавьте индексы в БД
3. Кэшируйте тяжелые вычисления
4. Проверьте медленные запросы в Django Debug Toolbar

---

## Roadmap

### v1.1 (Q1 2025)

- [ ] Добавить Prometheus метрики
- [ ] WebSocket для real-time обновлений прогресса
- [ ] GraphQL API как альтернатива REST

### v1.2 (Q2 2025)

- [ ] Gamification: badges, achievements, leaderboard
- [ ] Social features: follow students, study groups
- [ ] Mobile app SDK

### v2.0 (Q3 2025)

- [ ] AI-powered рекомендации курсов
- [ ] Adaptive learning paths
- [ ] Integration with LMS systems

---

## Дополнительные ресурсы

- [MIDDLEWARE_README.md](./MIDDLEWARE_README.md) - документация middleware
- [Django Ninja Documentation](https://django-ninja.rest-framework.com/)
- [Redis Caching Best Practices](https://redis.io/topics/lru-cache)
- [Rate Limiting Patterns](https://blog.cloudflare.com/rate-limiting-nginx-plus/)

---

**Автор**: Pyland Team
**Дата обновления**: 2025-01-01
**Версия**: 1.0
