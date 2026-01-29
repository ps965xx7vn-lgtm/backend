# Reviewers App - Система проверки работ

## 🎯 Обзор

**Reviewers** — приложение для проверки и ревью студенческих работ в Pyland. Включает:

- Dashboard ревьюера с статистикой
- Система проверки submitted работ
- Обратная связь студентам (review + improvements)
- Notifications о новых работах
- API для интеграции

---

## 📁 Структура приложения

```
reviewers/
├── __init__.py
├── admin.py                 # Админка для моделей ревьюеров
├── api.py                   # Django Ninja REST API
├── apps.py                  # Конфигурация приложения
├── cache_utils.py          # Redis/dummy кэширование
├── context_processors.py   # Контекст для шаблонов
├── decorators.py           # 3 кастомных декоратора
├── forms.py                # 4 формы с валидацией
├── models.py               # Review, StudentImprovement, ReviewerNotification
├── signals.py              # Django сигналы
├── urls.py                 # URL маршруты
├── views.py                # Function-based views
├── templates/              # HTML шаблоны
│   └── reviewers/
│       ├── dashboard.html
│       ├── submissions_list.html
│       ├── submission_review.html
│       ├── submission_detail.html
│       ├── profile.html
│       ├── settings.html
│       ├── history.html
│       ├── statistics.html
│       ├── bulk_operations.html
│       └── notifications.html
├── migrations/             # Миграции БД
├── management/             # Management commands
└── tests.py               # Юнит тесты
```

---

## 🗄️ Модели данных

### Review (Проверка работы)

Основная модель для хранения проверок студенческих работ.

```python
from reviewers.models import Review

# Создание проверки
review = Review.objects.create(
    submission=submission,
    reviewer=reviewer_user,
    status='approved',  # или 'needs_work'
    comments='Отличная работа! Несколько замечаний...',
    time_spent=30  # минуты
)
```

**Поля:**
- `submission` - FK к LessonSubmission (courses app)
- `reviewer` - FK к User (кто проверил)
- `status` - Статус: approved / needs_work
- `comments` - Общий комментарий
- `time_spent` - Время на проверку (минуты)
- `created_at`, `updated_at` - Временные метки

### StudentImprovement (Замечания)

Конкретные улучшения для работы студента.

```python
from reviewers.models import StudentImprovement

# Добавление замечания
improvement = StudentImprovement.objects.create(
    review=review,
    category='code_quality',  # или 'logic', 'style', 'testing'
    description='Рефакторинг метода calculate()',
    priority='medium',  # high / medium / low
    is_resolved=False
)
```

**Поля:**
- `review` - FK к Review
- `category` - Категория: code_quality / logic / style / testing
- `description` - Описание замечания
- `priority` - Приоритет: high / medium / low
- `is_resolved` - Исправлено ли
- `created_at` - Дата создания

### ReviewerNotification (Уведомления)

Уведомления о новых работах для проверки.

```python
from reviewers.models import ReviewerNotification

# Создание уведомления
notification = ReviewerNotification.objects.create(
    reviewer=reviewer_user,
    submission=submission,
    message='Новая работа на проверку: Python Basics - Lesson 3'
)
```

---

## 🔐 Декораторы

### 1. `@active_reviewer_required`

Проверяет что пользователь - активный ревьюер.

```python
from reviewers.decorators import active_reviewer_required

@active_reviewer_required
def dashboard_view(request):
    # Только для reviewer с is_active=True
    pass
```

### 2. `@can_review_course`

Проверяет доступ ревьюера к курсу.

```python
from reviewers.decorators import can_review_course

@can_review_course
def submission_review_view(request, submission_id):
    # Ревьюер может проверять только назначенные курсы
    pass
```

### 3. `@max_reviews_per_day_check`

Ограничение количества проверок в день.

```python
from reviewers.decorators import max_reviews_per_day_check

@max_reviews_per_day_check(max_reviews=20)
def create_review(request):
    # Максимум 20 проверок в день
    pass
```

---

## 📝 Формы

### 1. **ReviewForm**

Форма для создания проверки.

**Поля:**
- `status` - ChoiceField (approved/needs_work)
- `comments` - CharField (Textarea)
- `time_spent` - IntegerField (минуты)

**Валидация:**
- Comments обязательны для needs_work
- Time spent >= 1 минута

### 2. **StudentImprovementForm**

Форма для добавления замечаний.

**Поля:**
- `category` - ChoiceField
- `description` - CharField
- `priority` - ChoiceField

### 3. **ReviewerProfileForm**

Форма редактирования профиля ревьюера.

### 4. **SubmissionFilterForm**

Форма фильтрации работ.

**Поля:**
- `status` - Статус работы
- `course` - Курс
- `date_from`, `date_to` - Период

---

## 🌐 Views

### Dashboard
**URL:** `/reviewers/dashboard/`
**Template:** `reviewers/dashboard.html`
**Декораторы:** `@login_required`, `@require_any_role(['reviewer', 'mentor'])`

Главная панель с:
- Статистика проверок
- Новые работы на проверку
- График активности

### Submissions List
**URL:** `/reviewers/submissions/`
**Template:** `reviewers/submissions_list.html`

Список работ с фильтрацией по:
- Статусу
- Курсу
- Дате

### Submission Review
**URL:** `/reviewers/submissions/<id>/`
**Template:** `reviewers/submission_review.html`
**Декораторы:** `@active_reviewer_required`, `@can_review_course`

Проверка конкретной работы:
- Просмотр кода студента
- Форма ReviewForm
- Добавление improvements
- Отправка обратной связи

### Settings
**URL:** `/reviewers/settings/`
**Template:** `reviewers/settings.html`

Настройки ревьюера:
- Редактирование профиля
- Назначенные курсы
- Уведомления

### API Pending Count
**URL:** `/reviewers/api/pending-count/`
**Response:** JSON

Возвращает количество ожидающих работ (для AJAX).

---

## 🚀 API Endpoints

Base URL: `/api/reviewers/`

### GET `/pending/`
Получить работы на проверку.

**Response:**
```json
{
  "submissions": [
    {
      "id": 123,
      "student": "Ivan Petrov",
      "course": "Python Basics",
      "lesson": "Lesson 3: Functions",
      "submitted_at": "2026-01-20T10:30:00Z"
    }
  ],
  "count": 5
}
```

### POST `/review/<submission_id>/`
Создать проверку.

**Request:**
```json
{
  "status": "approved",
  "comments": "Хорошая работа!",
  "time_spent": 25,
  "improvements": [
    {
      "category": "code_quality",
      "description": "Добавить docstrings",
      "priority": "medium"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "review_id": 456,
  "message": "Проверка сохранена"
}
```

---

## 💾 Кэширование

Используется `cache_utils.py` для кэширования:

### get_reviewer_stats(reviewer_id)
Кэширует статистику ревьюера на 10 минут.

```python
from reviewers.cache_utils import get_reviewer_stats

stats = get_reviewer_stats(request.user.id)
# {
#   'total_reviews': 150,
#   'pending_count': 5
# }
```

### invalidate_reviewer_cache(reviewer_id)
Инвалидация кэша при изменениях.

```python
from reviewers.cache_utils import invalidate_reviewer_cache

# После создания review
invalidate_reviewer_cache(reviewer.id)
```

---

## 📚 Дополнительная документация

В папке `docs/` находится расширенная документация:

### 🏛️ [STRUCTURE.md](docs/STRUCTURE.md)

**Описание:** Подробная архитектура приложения reviewers с описанием всех компонентов.

**Содержит:**

**1. Архитектура приложения**

```
reviewers/
├── models.py          # Модели данных
│   ├── Review               # Основная проверка
│   ├── StudentImprovement   # Замечания
│   └── ReviewerNotification # Уведомления
├── views.py           # Function-based views
│   ├── dashboard_view
│   ├── submissions_list_view
│   ├── submission_review_view
│   └── settings_view
├── forms.py           # 4 формы с валидацией
│   ├── ReviewForm
│   ├── ReviewerProfileForm
│   ├── SubmissionFilterForm
│   └── StudentImprovementForm
├── decorators.py      # 3 кастомных декоратора
│   ├── @active_reviewer_required
│   ├── @can_review_course
│   └── @max_reviews_per_day_check
└── cache_utils.py     # Redis/dummy кеширование
    ├── get_reviewer_stats()  # TTL: 10min
    └── invalidate_reviewer_cache()
```

**2. Workflow проверки**

```
1. Студент отправляет работу
   ↓
2. LessonSubmission.status = 'pending'
   ↓
3. ReviewerNotification создается
   ↓
4. Ревьюер получает уведомление
   ↓
5. Ревьюер открывает submission_review_view
   ↓
6. Заполняет ReviewForm
   ↓
7. Добавляет StudentImprovement (замечания)
   ↓
8. Review сохраняется
   ↓
9. LessonSubmission.status обновляется
   ↓
10. Студент получает уведомление
```

**3. Декораторы**

```python
# decorators.py

@active_reviewer_required
def some_view(request):
    """
    Проверяет:
    - Пользователь авторизован
    - Имеет роль reviewer или mentor
    - reviewer.is_active = True
    """
    pass

@can_review_course(course_id_param='course_id')
def review_submission(request, course_id, submission_id):
    """
    Проверяет:
    - Ревьюер может проверять этот курс
    - course in reviewer.courses.all()
    """
    pass

@max_reviews_per_day_check(limit=20)
def create_review(request):
    """
    Проверяет:
    - Не превышен лимит проверок в день
    - Защита от перегрузки
    """
    pass
```

**4. Формы и валидация**

```python
# forms.py - ReviewForm

class ReviewForm(forms.ModelForm):
    """
    Форма для создания/редактирования проверки.

    Валидация:
    - status: approved / needs_work
    - comments: мин. 10 символов
    - time_spent: > 0 минут
    """

    def clean_comments(self):
        comments = self.cleaned_data.get('comments', '')

        if len(comments) < 10:
            raise ValidationError(
                'Комментарий должен содержать минимум 10 символов'
            )

        return comments
```

**5. Кеширование**

```python
# cache_utils.py

from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

def get_reviewer_stats(reviewer_id):
    """
    Получает статистику ревьюера с кешированием.
    TTL: 10 минут
    """
    cache_key = f'reviewer_stats:{reviewer_id}'

    # Пробуем получить из кеша
    cached_stats = safe_cache_get(cache_key)
    if cached_stats:
        return cached_stats

    # Собираем статистику
    from reviewers.models import Review

    stats = {
        'total_reviews': Review.objects.filter(
            reviewer_id=reviewer_id
        ).count(),
        'approved': Review.objects.filter(
            reviewer_id=reviewer_id,
            status='approved'
        ).count(),
        'avg_time': Review.objects.filter(
            reviewer_id=reviewer_id
        ).aggregate(Avg('time_spent'))['time_spent__avg'] or 0,
    }

    # Сохраняем в кеш на 10 мин
    safe_cache_set(cache_key, stats, 600)

    return stats

def invalidate_reviewer_cache(reviewer_id):
    """Инвалидирует кеш при новой проверке"""
    cache_key = f'reviewer_stats:{reviewer_id}'
    safe_cache_delete(cache_key)
```

**Ключевые принципы:**
- Function-based views (проще class-based)
- Полная валидация в формах
- Кеширование статистики
- Декораторы для защиты
- Чистые URL без лишних префиксов

---

## 🧪 Тестирование

```bash
# Все тесты reviewers app
pytest src/reviewers/tests.py -v

# С coverage
pytest src/reviewers/tests.py --cov=reviewers --cov-report=html
```

**Тест кейсы:**
- Создание проверок
- Валидация форм
- Декораторы доступа
- API endpoints
- Кэширование

---

## 🔧 Management Commands

```bash
# Создать тестовые данные
python manage.py populate_reviewers_data

# Отправить напоминания ревьюерам
python manage.py send_reviewer_reminders

# Обновить статистику
python manage.py update_reviewer_stats
```

---

## 📊 Workflow

### 1. Студент отправляет работу
→ Создается `LessonSubmission` (в courses app)

### 2. Уведомление ревьюеру
→ Создается `ReviewerNotification`

### 3. Ревьюер проверяет
→ `/reviewers/submissions/<id>/`
→ Заполняет `ReviewForm`
→ Добавляет `StudentImprovement`

### 4. Отправка результата
→ Создается `Review`
→ Обновляется статус `LessonSubmission`
→ Email студенту через Celery

### 5. Студент исправляет
→ Обновляет work и отправляет снова
→ Цикл повторяется

---

## 🔗 Связи с другими приложениями

### Authentication
- Использует `User` model
- Использует `Reviewer` profile (OneToOne с User)
- Использует декораторы: `@require_any_role(['reviewer', 'mentor'])`

### Courses
- Связь с `LessonSubmission` (submission → review)
- Проверка доступа к курсам через `reviewer.courses.all()`

### Notifications
- Отправка email через Celery tasks
- Push уведомления о новых работах

---

## ⚙️ Настройки

В `settings.py`:

```python
# Reviewers app settings
REVIEWERS_MAX_REVIEWS_PER_DAY = 20
REVIEWERS_CACHE_TIMEOUT = 600  # 10 минут
REVIEWERS_NOTIFICATION_ENABLED = True
```

---

## 📚 Дополнительная документация

- **[STRUCTURE.md](STRUCTURE.md)** - Детали архитектуры
- **[Copilot Instructions](/.github/copilot-instructions.md)** - Инструкции для AI

---

**Обновлено:** 22 января 2026
