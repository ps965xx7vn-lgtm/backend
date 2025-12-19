# Copilot Instructions for Pyland Backend

## Project Overview

**Pyland** is a Django 5.2 online school platform with multi-role user system
(students, mentors, reviewers, managers). It uses **Django Ninja** for REST
APIs, **Redis** for caching, **Celery** for async tasks, and **PostgreSQL**
as primary database.

**Key Technologies:**

- Django 5.2 + Django Ninja (OpenAPI-compliant REST)
- Python 3.13+, pytest-django for testing
- JWT authentication via `ninja-jwt`
- Celery + Redis (with fallback dummy cache support)
- Factory Boy for test fixtures
- Pydantic schemas for API validation
- **Poetry** for dependency management (Python 3.13+)

**Dependencies:**

- Production: Django 5.2.3, Ninja 1.4.3, Pydantic 2.11.7, Celery 5.5.3,
  Redis 6.4.0+, Pillow, django-countries, phonenumber-field,
  django-taggit, loguru, social-auth-app-django, sentry-sdk
- Development: pytest, pytest-django, factory-boy, pytest-cov,
  pytest-xdist, freezegun

---

## Architecture & Core Components

### 1. **App Structure (in `/src/`)**

The project uses a **modular app architecture** with clear separation of concerns:

| App | Purpose | Key Pattern |
|-----|---------|------------|
| `authentication/` | User models, JWT auth | Custom User Role FK |
| `core/` | Homepage, public pages, global context | Context processors for SEO |
| `students/` | Student dashboard, courses progress | Dashboard views + caching |
| `courses/` | Course/lesson/step structure | Hierarchical model |
| `blog/` | Articles, comments, reactions | Full caching + nested comments |
| `managers/` | Admin dashboard, feedback, logs | Rate limiting middleware |
| `reviewers/` | Review workflow for submissions | Review + Improvement models |
| `certificates/` | Course completion certificates | Generated on finish |
| `mentors/` | Mentor profiles, connections | Bridge reviewers & students |
| `payments/` | Payment processing, purchases | Payment status tracking |
| `notifications/` | Email/SMS/Telegram | Celery async handlers |
| `support/` | Support tickets | Ticket tracking |

**URL Routing** (`urls.py`):

- API routes: `path('api/', api.urls)` → all app routers
- i18n patterns wrap Django views with locale prefixes
- Supports 3 languages: Russian (ru), English (en), Georgian (ka)

### 2. **API Architecture (Django Ninja)**

**Central Registry:** `/src/pyland/api.py`

- Aggregates routers from all apps
- Single `NinjaAPI` instance with JWT auth
- Health check: `GET /api/ping` (no auth required)

**Router Pattern:**
Each app has `api.py` with a router:

```python
# Example: blog/api.py
router = Router(tags=["Blog"])

@router.get("/articles/", response=List[ArticleSchema])
def list_articles(request, category: str = None):
    # Pydantic schema validation automatic
    pass

@router.post("/articles/{id}/react/", response=ReactionSchema)
def add_reaction(request, id: int, payload: ReactionPayload):
    # POST bodies auto-validated against Pydantic schema
    pass
```

**Key Pattern:** Request/response validation via Pydantic schemas
in `schemas.py` per app.

### 3. **Database & ORM**

- **Primary DB:** PostgreSQL (via `dj-database-url`)
- **Models:** Django ORM with `get_user_model()` for User everywhere
- **Migrations:** Per-app under `migrations/` (apply with `python manage.py migrate`)
- **Fixtures:** Use `conftest.py` + Factory Boy factories (see Testing section)

**User Model Location:** `authentication/models.py`

- Custom User extends `AbstractUser`, email is unique identifier
- **Role System:** Each user has ONE role via ForeignKey (not M2M)
  - Available roles: student, mentor, reviewer, manager, admin, support
  - Access: `user.role.name` or `user.role_name` property
  - Default role: 'student' (auto-assigned on registration)
- **Student:** OneToOne extended profile in authentication.models.Student
  - Contains: avatar, phone, country, bio, notification settings, privacy settings
  - Access: `user.student` (created automatically via signal)
- **Reviewer:** OneToOne extended profile in authentication.models.Reviewer
  - Contains: bio, expertise_areas, courses, is_active, statistics
  - Access: `user.reviewer` (created manually when user gets reviewer role)

---

## Developer Workflows

### Project Setup with Poetry

```bash
# Install dependencies (creates virtualenv automatically)
poetry install

# Install only production deps (excludes dev group)
poetry install --no-dev

# Add a new dependency
poetry add package-name

# Add a dev dependency
poetry add --group dev package-name

# Show installed packages and versions
poetry show

# Update all dependencies
poetry update

# Export to requirements.txt
poetry export -f requirements.txt --output requirements.txt
```

**Poetry Configuration:** `pyproject.toml`

- Python version constraint: `>=3.13,<4.0`
- Project name: `pyland`
- Dev dependencies: pytest, pytest-django, factory-boy,
  pytest-cov, pytest-xdist, freezegun

### Popular Management Commands

```bash
# OPTION 1: With Poetry shell (recommended for development)
poetry shell
cd src

# Setup roles and initial data
# Create user roles (student, mentor, reviewer, manager, admin, support)
python manage.py create_roles

# Populate database with test data
python manage.py populate_courses_data     # Create 10 test courses with data

# Blog management
python manage.py generate_sitemap          # Generate sitemap.xml for SEO
python manage.py populate_blog_data        # Create test articles and blog data

# Migrations and data
python manage.py makemigrations [app_name] # Create migrations
python manage.py migrate [app_name]        # Apply migrations

# Admin
python manage.py createsuperuser           # Create admin user

# OPTION 2: Direct poetry run (without shell activation)
poetry run python src/manage.py create_roles
poetry run python src/manage.py populate_courses_data
poetry run python src/manage.py migrate
```

### Running the Application

```bash
# OPTION 1: Activate Poetry virtualenv (recommended for development)
poetry shell
cd src
python manage.py runserver  # http://localhost:8000

# OPTION 2: Run directly with poetry (without shell)
poetry run python src/manage.py runserver

# With Redis (optional but recommended, in separate terminal)
redis-server
```

### Running Tests

```bash
# OPTION 1: With Poetry shell (recommended)
poetry shell
cd src

# All tests
pytest

# Specific app
pytest blog/tests/

# With coverage report
pytest --cov=blog --cov-report=html

# Fail on first error, stop after 10 failures
pytest --maxfail=10 --failed-first

# Verbose output with markers
pytest -v --tb=short

# Parallel execution (faster)
pytest -n auto

# Run specific test file
pytest blog/tests/test_models.py -v

# OPTION 2: Direct poetry run (without shell)
poetry run pytest
poetry run pytest blog/tests/
poetry run pytest --cov=blog --cov-report=html
```

**Test Configuration:** `pytest.ini` defines:

- `DJANGO_SETTINGS_MODULE = pyland.settings`
- Auto-discovers files matching `test_*.py` or `*_tests.py`
- Markers: `@pytest.mark.slow`, `@pytest.mark.integration`, `@pytest.mark.api`, `@pytest.mark.unit`

### Database Management

```bash
# OPTION 1: With Poetry shell (recommended)
poetry shell
cd src

# Create new migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Apply specific app migrations
python manage.py migrate authentication

# Shell for direct queries
python manage.py shell

# Create superuser
python manage.py createsuperuser

# OPTION 2: Direct poetry run (without shell)
poetry run python src/manage.py makemigrations
poetry run python src/manage.py migrate
poetry run python src/manage.py migrate authentication
poetry run python src/manage.py createsuperuser
```

### Celery Tasks

Tasks are in `tasks.py` per app (e.g., `blog/tasks.py`, `authentication/tasks.py`).

```bash
# OPTION 1: With Poetry shell (recommended)
poetry shell
cd src

# Start Celery worker
celery -A pyland worker -l info

# Start Celery beat scheduler (for periodic tasks, in separate terminal)
celery -A pyland beat -l info

# Combined (worker + beat in one process - dev only)
celery -A pyland worker -B -l info

# OPTION 2: Direct poetry run (without shell)
poetry run celery -A pyland worker -l info
poetry run celery -A pyland beat -l info
poetry run celery -A pyland worker -B -l info
```

**Task definition pattern:**

```python
from celery import shared_task

@shared_task(bind=True, max_retries=3)
def send_email_notification(self, user_id):
    try:
        # Async work
        pass
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)  # Retry in 60s
```

**Triggering:** Called from views/APIs via `task.delay()` or `.apply_async()`.

---

## Critical Conventions & Patterns

### 1. **Caching (Redis-backed)**

**Cache Utils Pattern:**

```python
# blog/cache_utils.py - exemplary implementation
from django.core.cache import cache

def get_cache_key(prefix, *args, **kwargs):
    """Generate unique key from prefix + args."""
    params_str = json.dumps({'args': args, 'kwargs': sorted(kwargs.items())})
    hash_obj = hashlib.md5(params_str.encode())
    params_hash = hash_obj.hexdigest()[:12]
    return f"{prefix}:{params_hash}"

@cache_page_data(timeout=300, key_prefix='article_list')
def get_articles(category=None, page=1):
    """Decorator auto-caches, checks Redis health."""
    return articles
```

**Convention:** Prefix caches with app name (`blog:`, `students:`, etc.). Fallback to dummy cache if Redis unavailable.

### 2. **Logging (Loguru + Django logger)**

Every module should import logger:

```python
import logging
logger = logging.getLogger(__name__)

logger.info(f"User {user_id} logged in")
logger.error(f"Failed to process: {exc}")
```

**Configured in `settings.py`** — all logs route to `/src/logs/` directory.

### 3. **Error Handling Pattern (try-except in APIs)**

```python
# All API endpoints wrap in try-except
@router.post("/do-something/")
def do_something(request, payload: Schema):
    try:
        result = _process(payload)
        logger.info(f"Success: {result}")
        return {"data": result}
    except ValidationError as e:
        logger.warning(f"Validation failed: {e}")
        return {"error": str(e)}, 400
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"error": "Internal server error"}, 500
```

### 4. **Testing Patterns**

**Fixture Location:** `conftest.py` at app level and root.
**Factories Location:** `tests/factories.py` per app.

**Standard test file structure:**

```python
# blog/tests/test_models.py
@pytest.mark.django_db
class TestArticleModel:
    def test_article_creation(self, user, category):
        """Arrange-Act-Assert pattern."""
        # Arrange
        article_data = {"title": "Test", "category": category, "author": user}
        # Act
        article = Article.objects.create(**article_data)
        # Assert
        assert article.slug == "test"
        assert article.author == user

# blog/tests/test_api.py
def test_list_articles_api(api_client, article):
    """Test API responses with Ninja's TestClient."""
    response = api_client.get("/api/blog/articles/")
    assert response.status_code == 200
    assert len(response.json()["data"]) >= 1
```

**Key Factories (in `blog/tests/factories.py`):**

- `UserFactory`, `StaffUserFactory`, `SuperUserFactory`
- `CategoryFactory`, `ArticleFactory`, `DraftArticleFactory`
- `CommentFactory`, `ReactionFactory`, `BookmarkFactory`

**Clients Available:**

- `api_client = TestClient(api)` — from `ninja.testing`
- `authenticated_client = client` with `client.force_login(user)`

### 5. **Pydantic Schemas (Input/Output Validation)**

Located in `schemas.py` per app:

```python
from pydantic import BaseModel, EmailStr

class ArticleSchema(BaseModel):
    id: int
    title: str
    content: str
    author_name: str
    published_at: datetime

    class Config:
        from_attributes = True  # Support Django ORM objects

class CreateArticlePayload(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    content: str = Field(..., min_length=10)
    category_id: int
    tags: List[str] = []
```

### 6. **Admin Customization**

Located in `admin.py` per app, extends Django `ModelAdmin`:
```python
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'published_at')
    list_filter = ('status', 'category', 'published_at')
    search_fields = ('title', 'content')
    readonly_fields = ('slug', 'created_at')
    prepopulated_fields = {'slug': ('title',)}
```

---

## Integration Points & Data Flows

### 1. **Authentication Flow**
- User registers → `authentication.views.SignUpView` or `/api/auth/register`
- Email verification signal in `authentication.signals.py`
- JWT tokens via `ninja-jwt` at `/api/auth/token/`
- Profile auto-created via Django signal on User creation

### 2. **Student Progress Tracking**
- Student enrolls in course → `students/models.py` stores enrollment
- Progress updates async via Celery → cached in Redis
- Dashboard reads from `students.views.DashboardView` + cache

### 3. **Blog Publishing Workflow**
- Create article (draft) → `blog.models.Article` (status='draft')
- Publish → update status to 'published', cache invalidates
- Readers fetch from cached list → count views via signal
- Comments trigger email notification tasks (Celery)

### 4. **Role-Based Access**
- Middleware/decorators check `request.user.profile.roles.all()`
- Manager endpoints in `/managers/api.py` check `is_staff=True`
- Rate limiting applied to sensitive endpoints via `middleware.py`

---

## Specialized Apps Details

### **Students App**
- **Purpose:** Account management, profile editing, personal dashboard
- **Key Models:** User profile extended via `authentication/Profile`
- **API Endpoints:** Registration, login, profile get/update, token management, avatar upload
- **Middleware:** `StudentsRateLimitMiddleware` (1000 req/hour for auth, 100 for anon)
- **Schemas:** `RegisterIn`, `LoginIn`, `ProfileOut`, `NotificationSettingsOut`

### **Courses App**
- **Hierarchy:** Course → Lesson → Step → (Tip/ExtraSource)
- **Submissions:** `LessonSubmission` model tracks student submissions with status workflow
- **Status Workflow:** pending → changes_requested → approved
- **Caching:** Progress cached per student per course
- **Key Endpoints:** List/get courses, create lessons/steps, manage submissions

### **Reviewers App**
- **Purpose:** Review workflow for student submissions with modern architecture
- **Models:**
  - `Reviewer` (from authentication.models) - reviewer profile with expertise, courses, is_active, statistics
  - `Review` - review of submission with status/rating/comments/time_spent
  - `StudentImprovement` - specific improvements for submission with priority
  - `ReviewerNotification` - notifications about new submissions
- **Decorators:**
  - `active_reviewer_required` - checks reviewer is_active=True
  - `can_review_course` - validates course access
  - `max_reviews_per_day_check` - enforces daily review limit
- **Forms:** ReviewForm, ReviewerProfileForm, SubmissionFilterForm, StudentImprovementForm (full validation + clean methods)
- **Views:** dashboard_view, submissions_list_view, submission_review_view, settings_view, api_pending_count
- **URLs:** Simple structure like students app: dashboard/, submissions/, submissions/<id>/, settings/, api/pending-count/
- **Caching:** get_reviewer_stats (10min TTL), invalidate_reviewer_cache pattern
- **Statuses:** approved / needs_work / rejected
- **Access Control:** @require_any_role(['reviewer', 'mentor']) + custom decorators
- **Review Process:** GET form → POST validation → update submission status → invalidate cache → redirect

### **Blog App**
- **Features:** 149 unit tests, Redis caching, nested comments (max 3 levels)
- **Models:** Category, Article, Series, Comment, Reaction, Bookmark, ReadingProgress, Newsletter
- **Markdown Support:** Articles stored as markdown, rendered with `django-markdownify`
- **Reactions:** Like, love, helpful, insightful, amazing types
- **SEO:** Meta-tags, schema.org, Open Graph, sitemap generation

### **Managers App**
- **Dashboard:** Feedback management, system logs, platform statistics
- **Models:** Feedback, SystemLog
- **Rate Limiting:** 50 req/hour for operations
- **Caching:** Statistics cached 5-10 minutes
- **Logging:** All actions logged with timestamps, user, action type

### **Payments App**
- **Model:** Payment with user, course, amount, status
- **Status:** pending / completed / failed / cancelled
- **Methods:** Credit card, bank transfer, PayPal, etc.
- **Extra Data:** JSON field for payment gateway responses
- **Views:** Purchase view for course checkout

### **Notifications App**
- **Channels:** Email (primary), SMS (via Twilio), Telegram (via bot)
- **Tasks:** Async Celery tasks for sending
- **Settings:** Per-user notification preferences in Profile
- **Types:** course_updates, lesson_reminders, achievement_alerts, weekly_summary

### **Certificates App**
- **Trigger:** Auto-generated when course completion % >= 100
- **Fields:** Student, course, completion date, certificate number
- **Format:** PDF export with student name, course, completion date

### **Mentors App**
- **Profile:** Mentor with expertise areas, available courses
- **Connection:** Many-to-many between mentors and students
- **Review Rights:** Mentors can review submissions in assigned courses

### **Support App**
- **Ticket System:** User creates support tickets
- **Status:** open / in_progress / resolved / closed
- **Assignment:** Auto-assigned or manually assigned to support team

---

## File Organization Best Practices

For **new features**, follow this structure:

```
your_app/
├── models.py           # Django models
├── schemas.py          # Pydantic schemas (API I/O)
├── api.py              # Django Ninja router + endpoints
├── views.py            # Django views (if using templates)
├── forms.py            # Django forms
├── admin.py            # Admin registration
├── tasks.py            # Celery tasks
├── urls.py             # URL patterns
├── cache_utils.py      # Cache helpers (if needed)
├── middleware.py       # Request middleware (if needed)
├── signals.py          # Django signals (if needed)
├── tests/
│   ├── conftest.py     # Fixtures
│   ├── factories.py    # Factory Boy factories
│   ├── test_models.py  # Model unit tests
│   ├── test_api.py     # API endpoint tests
│   └── test_views.py   # View tests
└── migrations/         # Auto-generated
```

---

## Common Development Tasks

### Adding a New API Endpoint

1. **Define Pydantic schema** in `your_app/schemas.py`
2. **Add route** in `your_app/api.py`:
   ```python
   @router.post("/endpoint/", response=ResponseSchema)
   def create_item(request, payload: CreatePayload):
       # Validation auto-handled by Pydantic
       return Item.objects.create(**payload.dict())
   ```
3. **Test** in `your_app/tests/test_api.py`:
   ```python
   def test_create_item_api(api_client):
       response = api_client.post("/api/your_app/endpoint/", json={...})
       assert response.status_code == 201
   ```
4. Router auto-added to main API in `/pyland/api.py`

### Adding a Celery Task

1. Create in `your_app/tasks.py`:
   ```python
   @shared_task(bind=True, max_retries=3)
   def process_data(self, data_id):
       try:
           data = Model.objects.get(id=data_id)
           # Process
       except Exception as exc:
           raise self.retry(exc=exc, countdown=60)
   ```
2. Call from view/API: `process_data.delay(data_id)`
3. Test with `pytest-django` (auto-uses eager mode in tests)

### Adding a Database Model

1. Define in `your_app/models.py` with full docstrings
2. Create schema in `schemas.py` for serialization
3. Register in `admin.py` for admin interface
4. Run migrations: `python manage.py makemigrations && python manage.py migrate`
5. Add tests in `your_app/tests/test_models.py`

---

## Debugging & Troubleshooting

### Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| "Redis unavailable" warning | Redis not running | `redis-server` or use dummy cache |
| Test database not resetting | Fixtures not using `@pytest.mark.django_db` | Add decorator to test class |
| 401 Unauthorized on API | Missing JWT token or expired | Check `Authorization: Bearer <token>` header |
| Import errors in tests | Missing factory imports | Import from `your_app.tests.factories` |
| Migrations out of sync | Stale migration state | `python manage.py migrate --fake-initial` (dev only) |

### Inspection Tools

```bash
# Django shell with imported models
python manage.py shell
>>> from blog.models import Article
>>> Article.objects.all().count()

# View SQL queries (DEBUG=True in settings)
from django.db import connection
print(connection.queries)

# API docs (auto-generated by Ninja)
# http://127.0.0.1:8000/api/docs

# Test coverage
pytest --cov=src --cov-report=html
# Open htmlcov/index.html
```

---

## Key Files Reference

| File | Purpose |
|------|---------|
| `src/pyland/settings.py` | Django config: INSTALLED_APPS, DATABASES, CACHES, LOGGING |
| `src/pyland/api.py` | Main API aggregator (all routers registered here) |
| `src/pyland/urls.py` | Main URL router (i18n + API + admin) |
| `pytest.ini` | Test discovery & markers config |
| `pyproject.toml` | Dependencies, Python version constraint (3.13+) |
| `REDIS_SETUP.md` | Redis installation & fallback cache guide |
| `AUTHENTICATION_REFACTORING.md` | Auth system architecture changes |

---

## Language & Documentation Standards

- **Comments & Docstrings:** Russian (Русский) for clarity with Russian dev team
- **Code:** English identifiers (function names, variable names)
- **Commit Messages:** English
- **Type Hints:** Used throughout (e.g., `def func(x: int) -> str:`)
- **Logging:** Use logger.info/warning/error with context

Example:
```python
def process_user_data(user_id: int) -> dict:
    """
    Обрабатывает данные пользователя и кэширует результат.

    Args:
        user_id: ID пользователя

    Returns:
        dict: Обработанные данные

    Raises:
        User.DoesNotExist: Если пользователь не найден
    """
    logger.info(f"Processing user {user_id}")
    # ...
```

---

## Quick Reference Commands

```bash
# Setup & Environment
poetry install                      # Install dependencies
poetry shell                        # Activate virtualenv
cd src                             # Navigate to Django project

# Development server (from src/ directory)
python manage.py runserver         # http://localhost:8000
# Alternative without poetry shell:
# poetry run python src/manage.py runserver

# Database (from src/ directory with poetry shell)
python manage.py makemigrations    # Create migrations
python manage.py migrate           # Apply migrations
python manage.py createsuperuser   # Create admin user
# Alternatives with poetry run:
# poetry run python src/manage.py makemigrations
# poetry run python src/manage.py migrate
# poetry run python src/manage.py createsuperuser

# Testing (from src/ directory with poetry shell)
pytest                             # Run all tests
pytest -v --tb=short              # Verbose with short traceback
pytest --cov=blog --cov-report=html  # Coverage report
pytest blog/tests/test_models.py   # Specific file
# Alternatives with poetry run:
# poetry run pytest
# poetry run pytest blog/tests/
# poetry run pytest --cov=blog --cov-report=html

# Celery (in separate terminals, from src/ directory with poetry shell)
celery -A pyland worker -l info    # Worker
celery -A pyland beat -l info      # Beat scheduler
celery -A pyland worker -B -l info # Combined (dev only)
# Alternatives with poetry run:
# poetry run celery -A pyland worker -l info
# poetry run celery -A pyland beat -l info
# poetry run celery -A pyland worker -B -l info

# Redis (in separate terminal)
redis-server                       # Start Redis

# Management commands (from src/ directory with poetry shell)
python manage.py populate_courses_data    # Create test courses
python manage.py create_roles             # Create user roles
python manage.py generate_sitemap         # Generate sitemap.xml
# Alternatives with poetry run:
# poetry run python src/manage.py populate_courses_data
# poetry run python src/manage.py create_roles
# poetry run python src/manage.py generate_sitemap
```
