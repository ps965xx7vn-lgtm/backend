# Архитектура Проекта

## Обзор

Pyland Backend - это полнофункциональная платформа онлайн-школы программирования, построенная на Django 5.2 с REST API через Django Ninja.

## Технологический Стек

### Backend

- **Django 5.2.3** - основной фреймворк
- **Django Ninja 1.4.3** - REST API framework (OpenAPI/Swagger)
- **Python 3.13+** - язык программирования
- **Poetry** - управление зависимостями

### База Данных

- **PostgreSQL 15+** - основная БД (production)
- **SQLite** - для разработки
- **Redis 7+** - кэширование и Celery broker

### Асинхронные Задачи

- **Celery 5.5.3** - обработка асинхронных задач
- **Redis** - message broker

### Аутентификация

- **JWT** (ninja-jwt) - токены доступа
- **Email verification** - подтверждение email
- **Social Auth** - OAuth (опционально)

### CI/CD

- **GitHub Actions** - автоматизация
- **Pre-commit** - локальные проверки
- **Poetry** - управление зависимостями

### Качество Кода

- **Ruff** - быстрый линтер
- **Black** - форматирование
- **isort** - сортировка импортов
- **MyPy** - проверка типов
- **Bandit** - security сканирование
- **Safety** - проверка уязвимостей
- **Radon** - анализ сложности

## Архитектура Приложений

### Модульная Структура

```text
src/
├── authentication/   # Аутентификация и управление пользователями
├── students/        # Студенческий дашборд и прогресс
├── courses/         # Курсы, уроки, шаги
├── reviewers/       # Система ревью и обратной связи
├── mentors/         # Менторская система
├── managers/        # Админ-панель менеджеров
├── blog/           # Блог с статьями
├── core/           # Общий функционал
├── payments/       # Платежная система
├── certificates/   # Сертификаты
├── notifications/  # Уведомления
└── support/        # Поддержка пользователей
```text
### Ролевая Система

**Модель:** One Role Per User (FK, не M2M)

Роли:

- `student` - студент (по умолчанию)
- `mentor` - ментор
- `reviewer` - ревьюер
- `manager` - менеджер
- `admin` - администратор
- `support` - поддержка

**Реализация:**

```python

# authentication/models.py

class User(AbstractUser):
    role = ForeignKey(Role)  # Одна роль на пользователя
    email_is_verified = BooleanField(default=False)

class Student(Model):
    user = OneToOneField(User)
    avatar, phone, country, bio, courses...

class Reviewer(Model):
    user = OneToOneField(User)
    expertise_areas, is_active, statistics...
```text
## REST API Архитектура

### Django Ninja

**Центральный роутер:** `pyland/api.py`

```python
from ninja import NinjaAPI

api = NinjaAPI(
    title="Pyland API",
    version="2.0",
    auth=JWTAuth()
)

# Регистрация роутеров

api.add_router("/auth/", authentication_router)
api.add_router("/students/", students_router)
api.add_router("/courses/", courses_router)

#

```text
### Схемы (Pydantic)

```python

# app/schemas.py

class ArticleOut(Schema):
    id: int
    title: str
    slug: str
    author_name: str
    published_at: datetime

    class Config:
        from_attributes = True  # Support Django ORM

class CreateArticleIn(Schema):
    title: str = Field(..., min_length=5)
    content: str = Field(..., min_length=10)
    category_id: int
```text
### Endpoints Pattern

```python

# app/api.py

router = Router(tags=["Blog"])

@router.get("/articles/", response=List[ArticleOut])
def list_articles(request, category: str = None):
    queryset = Article.objects.filter(status='published')
    if category:
        queryset = queryset.filter(category__slug=category)
    return queryset

@router.post("/articles/", response=ArticleOut)
def create_article(request, payload: CreateArticleIn):
    article = Article.objects.create(**payload.dict())
    return article
```text
## Система Курсов

### Иерархия

```text
Course (1)
  └── Lessons (N)
        └── Steps (N)
              ├── Tips (N)
              └── ExtraSources (N)
```text
### Прогресс

```python

# reviewers/models.py

class StepProgress(Model):
    profile = FK(Student)
    step = FK(Step)
    is_completed = BooleanField()
    completed_at = DateTimeField(null=True)
```text
### Submission Workflow

```text
Student → создает Submission
    ↓
Reviewer → создает Review + StudentImprovements
    ↓
Submission.status = 'needs_work'
    ↓
Student → помечает improvements как completed
    ↓
Student → resubmit (revision_count++)
    ↓
Reviewer → approve
    ↓
Submission.status = 'approved' → урок разблокирован
```text
## Кэширование (Redis)

### Стратегия

**Паттерн:**

```python

# app/cache_utils.py

def get_cache_key(prefix, *args, **kwargs):
    params = json.dumps({'args': args, 'kwargs': sorted(kwargs.items())})
    hash = hashlib.md5(params.encode()).hexdigest()[:12]
    return f"{prefix}:{hash}"

def cache_page_data(timeout=300, key_prefix='data'):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = get_cache_key(key_prefix, *args, **kwargs)
            cached = safe_cache_get(cache_key)
            if cached:
                return cached
            result = func(*args, **kwargs)
            safe_cache_set(cache_key, result, timeout)
            return result
        return wrapper
    return decorator
```text
### Что кэшируется

- **Blog:** списки статей, детали статей, категории (5-10 мин)
- **Students:** прогресс курсов, статистика (10 мин)
- **Courses:** списки курсов, данные уроков (15 мин)
- **Managers:** статистика платформы (5 мин)

### Инвалидация

```python

# При изменении данных

def save(self, *args, **kwargs):
    super().save(*args, **kwargs)
    self.invalidate_cache()

def invalidate_cache(self):
    cache.delete(f'article:{self.slug}')
    cache.delete('article_list:*')  # Wildcard pattern
```text
## Celery Tasks

### Структура

```python

# app/tasks.py

from celery import shared_task

@shared_task(bind=True, max_retries=3)
def send_email_notification(self, user_id, template, context):
    try:
        user = User.objects.get(id=user_id)
        send_mail(...)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
```text
### Типы задач

- **Email:** верификация, сброс пароля, уведомления
- **Notifications:** SMS, Telegram
- **Reports:** генерация статистики
- **Cleanup:** удаление старых данных

## Internationalization (i18n)

### Поддерживаемые языки

- `ru` - Русский (по умолчанию)
- `en` - English
- `ka` - ქართული (Georgian)

### Workflow

```python

# В коде

from django.utils.translation import gettext_lazy as _

message = _("Hello, World!")

# В шаблонах

{% load i18n %}
{% trans "Welcome" %}

# Команды

python manage.py makemessages -l en
python manage.py compilemessages
```text
### Файлы переводов

```text
src/locale/
├── en/LC_MESSAGES/django.po  # 486 strings (100%)
├── ka/LC_MESSAGES/django.po  # 494 strings (100%)
└── ru/LC_MESSAGES/django.po  # default
```text
## Безопасность

### Аутентификация

- JWT токены (access + refresh)
- Email verification обязателен
- Password reset через email

### Авторизация

```python

# Декораторы

@require_role(['student', 'mentor'])
def view(request):
    pass

@require_permission('can_review')
def review_view(request):
    pass
```text
### Защита

- **CSRF** - включен для всех форм
- **XSS** - автоэкранирование Django
- **SQL Injection** - ORM защита
- **Rate Limiting** - middleware для API
- **Security Headers** - django-security

### Проверки

```bash

# Уязвимости зависимостей

poetry run safety check

# Security сканирование кода

poetry run bandit -r src/
```text
## Тестирование

### Структура

```text
app/
└── tests/
    ├── conftest.py       # Fixtures
    ├── factories.py      # Factory Boy
    ├── test_models.py    # Unit tests
    ├── test_api.py       # API tests
    └── test_views.py     # View tests
```text
### Типы тестов

**Unit Tests:**

```python
@pytest.mark.django_db
class TestArticleModel:
    def test_article_creation(self, user, category):
        article = Article.objects.create(...)
        assert article.slug == "test-article"
```text
**API Tests:**

```python
def test_list_articles_api(api_client):
    response = api_client.get("/api/blog/articles/")
    assert response.status_code == 200
```text
**Integration Tests:**

```python
@pytest.mark.integration
def test_full_submission_workflow(student, reviewer, lesson):

    # Полный workflow от создания до approve

    pass
```text
### Coverage

Цель: >80% coverage для всех приложений

```bash
poetry run pytest --cov=src --cov-report=html
```text
## CI/CD Pipeline

### GitHub Actions Workflows

**1. Main CI (`ci.yml`):**

- Тестирование (PostgreSQL 15 + Redis 7)
- Security checks (safety, bandit)
- Code quality (black, isort)
- Coverage upload (Codecov)

**2. PR Checks (`pr-checks.yml`):**

- Validation (migrations, templates, i18n)
- Complexity analysis (radon)

**3. Documentation (`docs.yml`):**

- Markdown linting
- Link checking

**4. Dependency Updates (`dependency-updates.yml`):**

- Weekly auto-updates
- Security audits

### Pre-commit Hooks

Локальные проверки перед коммитом:

- Ruff (linting + formatting)
- Black (code style)
- isort (imports)
- Bandit (security)
- Django-upgrade (Django version)
- File quality checks

## Производительность

### Database Optimization

```python

# Select related / Prefetch related

articles = Article.objects.select_related('author', 'category')
courses = Course.objects.prefetch_related('lessons__steps')

# Annotate для агрегации

courses = Course.objects.annotate(
    lesson_count=Count('lessons'),
    avg_progress=Avg('enrollments__progress')
)

# Index для частых запросов

class Article(Model):
    class Meta:
        indexes = [
            Index(fields=['slug']),
            Index(fields=['-published_at']),
        ]
```text
### Caching Strategy

- **View caching:** редко меняющиеся страницы (15 мин)
- **Fragment caching:** части шаблонов (5-10 мин)
- **Query caching:** результаты запросов (5 мин)
- **Fallback:** Dummy cache если Redis недоступен

### Async Tasks

Тяжелые операции через Celery:

- Email отправка
- Report generation
- Data processing
- External API calls

## Monitoring & Logging

### Logging

```python
import logging
logger = logging.getLogger(__name__)

logger.info(f"User {user.id} logged in")
logger.error(f"Failed to process: {exc}")
```text
**Файлы логов:** `src/logs/`

- `django.log` - Django events
- `celery.log` - Celery tasks

### Metrics

- Request/response times
- Cache hit/miss rates
- Database query counts
- Celery task success/failure

## Deployment

### Environment Variables

```env

# Django

SECRET_KEY=...
DEBUG=False
ALLOWED_HOSTS=your-domain.com

# Database

DATABASE_URL=postgresql://...

# Redis

REDIS_URL=redis://...

# Celery

CELERY_BROKER_URL=...

# Email

EMAIL_HOST=...
EMAIL_PORT=587
EMAIL_USE_TLS=True

# Sentry (опционально)

SENTRY_DSN=...
```text
### Static Files

```bash
python manage.py collectstatic --no-input
```text
Serve через Nginx/Whitenoise

### Database Migrations

```bash
python manage.py migrate --no-input
```text
## Масштабирование

### Horizontal Scaling

- Load balancer (Nginx/HAProxy)
- Multiple app servers (Gunicorn workers)
- Redis Cluster для кэша
- PostgreSQL replication (read replicas)

### Vertical Scaling

- Увеличение Gunicorn workers
- Больше Celery workers
- Оптимизация query performance

## Best Practices

### Code Style

- Black для форматирования (line-length=100)
- Ruff для linting
- Type hints везде где возможно
- Docstrings на русском

### Git Workflow

- Feature branches
- PR reviews обязательны
- CI checks должны пройти
- Conventional commits

### API Design

- RESTful endpoints
- Pydantic schemas для validation
- Consistent error responses
- API versioning через URL

### Security

- Secrets в environment variables
- HTTPS only в продакшене
- Regular dependency updates
- Security scanning в CI
