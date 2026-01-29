# Руководство по локализации контента PyLand

## Обзор

Для локализации контента курсов используется **django-modeltranslation** - мощное решение для перевода моделей Django.

## Почему django-modeltranslation?

### Преимущества
- ✅ **Прозрачность**: Автоматическое создание полей для каждого языка
- ✅ **Удобство**: Все переводы в одной админке
- ✅ **Производительность**: Нет дополнительных JOIN'ов к БД
- ✅ **Fallback**: Автоматический откат на язык по умолчанию
- ✅ **Миграция**: Легко перенести существующий контент

### Сравнение с альтернативами

| Решение | Плюсы | Минусы | Для PyLand |
|---------|-------|--------|------------|
| **django-modeltranslation** | Простота, производительность, удобная админка | Дублирование колонок в БД | ✅ **Рекомендуется** |
| django-parler | Чистая БД, гибкость | Сложные JOIN'ы, медленнее | ❌ Избыточно |
| JSON поля | Гибкость | Сложный поиск, нет индексов | ❌ Не подходит |
| Отдельная таблица переводов | Гибкость | Много кода, сложность | ❌ Избыточно |

## Установка

### 1. Установить пакет

```bash
poetry add django-modeltranslation
```

### 2. Добавить в INSTALLED_APPS

```python
# src/pyland/settings.py

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party apps
    'modeltranslation',  # ВАЖНО: Должен быть ПЕРЕД admin!

    # ... остальные приложения
    'courses',
    'blog',
    # ...
]
```

### 3. Настройка языков

```python
# src/pyland/settings.py

# Поддерживаемые языки
LANGUAGES = [
    ('ru', 'Русский'),
    ('en', 'English'),
    ('ka', 'ქართული'),
]

# Язык по умолчанию
LANGUAGE_CODE = 'ru'

# Использовать языки из заголовка Accept-Language
USE_I18N = True

# Настройки modeltranslation
MODELTRANSLATION_DEFAULT_LANGUAGE = 'ru'
MODELTRANSLATION_LANGUAGES = ('ru', 'en', 'ka')
MODELTRANSLATION_FALLBACK_LANGUAGES = ('ru', 'en')
MODELTRANSLATION_PREPOPULATE_LANGUAGE = 'ru'

# Auto-register при запуске
MODELTRANSLATION_AUTO_POPULATE = True
```

## Конфигурация моделей

### Создать translation.py для каждого приложения

#### courses/translation.py

```python
"""
Конфигурация переводов для моделей курсов.
"""
from modeltranslation.translator import TranslationOptions, register

from .models import Course, Lesson, Step, Tip, ExtraSource


@register(Course)
class CourseTranslationOptions(TranslationOptions):
    """
    Переводимые поля модели Course.
    """
    fields = (
        'name',                 # Название курса
        'description',          # Полное описание
        'short_description',    # Краткое описание
    )
    required_languages = {
        'ru': ('name', 'short_description'),  # Обязательные поля для русского
        'en': ('name',),                       # Обязательные поля для английского
        'ka': ('name',),                       # Обязательные поля для грузинского
    }


@register(Lesson)
class LessonTranslationOptions(TranslationOptions):
    """
    Переводимые поля модели Lesson.
    """
    fields = (
        'name',                 # Название урока
        'short_description',    # Краткое описание
    )
    required_languages = {
        'ru': ('name',),
        'en': ('name',),
        'ka': ('name',),
    }


@register(Step)
class StepTranslationOptions(TranslationOptions):
    """
    Переводимые поля модели Step.

    Много контента - все текстовые поля переводятся.
    """
    fields = (
        'name',                 # Название шага
        'description',          # Описание шага
        'actions',              # Действия для выполнения
        'self_check',           # Проверка себя
        'repair_description',   # Описание ремонта
    )
    required_languages = {
        'ru': ('name', 'description'),
        'en': ('name',),
        'ka': ('name',),
    }


@register(Tip)
class TipTranslationOptions(TranslationOptions):
    """
    Переводимые поля модели Tip (подсказки).
    """
    fields = (
        'title',        # Заголовок подсказки
        'description',  # Описание подсказки
    )
    required_languages = {
        'ru': ('title', 'description'),
        'en': ('title',),
        'ka': ('title',),
    }


@register(ExtraSource)
class ExtraSourceTranslationOptions(TranslationOptions):
    """
    Переводимые поля модели ExtraSource (дополнительные материалы).
    """
    fields = (
        'title',        # Название источника
        'description',  # Описание источника
        'url',          # URL может быть разным для разных языков
    )
    required_languages = {
        'ru': ('title',),
        'en': ('title',),
        'ka': ('title',),
    }
```

#### blog/translation.py

```python
"""
Конфигурация переводов для блога.
"""
from modeltranslation.translator import TranslationOptions, register

from .models import Article, Category, Series


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    """
    Переводимые поля категории блога.
    """
    fields = ('name', 'description')
    required_languages = {
        'ru': ('name',),
        'en': ('name',),
        'ka': ('name',),
    }


@register(Article)
class ArticleTranslationOptions(TranslationOptions):
    """
    Переводимые поля статьи.
    """
    fields = (
        'title',
        'content',
        'excerpt',
        'meta_description',
    )
    required_languages = {
        'ru': ('title', 'content'),
        'en': ('title',),
        'ka': ('title',),
    }


@register(Series)
class SeriesTranslationOptions(TranslationOptions):
    """
    Переводимые поля серии статей.
    """
    fields = ('name', 'description')
    required_languages = {
        'ru': ('name',),
        'en': ('name',),
        'ka': ('name',),
    }
```

## Создание миграций

После создания translation.py файлов:

```bash
# Создать миграции для добавления полей переводов
python manage.py makemigrations

# Применить миграции
python manage.py migrate

# Обновить существующий контент (скопировать в language-specific поля)
python manage.py update_translation_fields
```

## Структура БД после миграции

### До (было):
```sql
CREATE TABLE courses_course (
    id UUID PRIMARY KEY,
    name VARCHAR(200),
    description TEXT,
    short_description VARCHAR(350),
    ...
);
```

### После (стало):
```sql
CREATE TABLE courses_course (
    id UUID PRIMARY KEY,
    -- Русский (основной)
    name_ru VARCHAR(200),
    description_ru TEXT,
    short_description_ru VARCHAR(350),
    -- Английский
    name_en VARCHAR(200),
    description_en TEXT,
    short_description_en VARCHAR(350),
    -- Грузинский
    name_ka VARCHAR(200),
    description_ka TEXT,
    short_description_ka VARCHAR(350),
    ...
);
```

## Использование в коде

### Автоматический выбор языка

```python
from django.utils.translation import activate

# Django автоматически выбирает правильное поле
activate('ru')
course = Course.objects.get(slug='python-basics')
print(course.name)  # Выведет name_ru

activate('en')
print(course.name)  # Выведет name_en

activate('ka')
print(course.name)  # Выведет name_ka
```

### Явное указание языка

```python
from modeltranslation.utils import get_translation_fields

# Получить конкретный перевод
course.name_ru  # Русское название
course.name_en  # Английское название
course.name_ka  # Грузинское название

# Получить все переводы
translations = get_translation_fields(Course, 'name')
# ['name_ru', 'name_en', 'name_ka']
```

### В шаблонах

```django
{% load i18n %}

<!-- Django автоматически выбирает нужный язык -->
<h1>{{ course.name }}</h1>
<p>{{ course.description }}</p>

<!-- Явное указание языка -->
{% language 'en' %}
    <h1>{{ course.name }}</h1>
{% endlanguage %}
```

### В API (Django Ninja)

```python
from ninja import Router
from django.utils.translation import get_language

router = Router()

@router.get("/courses/", response=List[CourseSchema])
def list_courses(request):
    # Django автоматически использует язык из Accept-Language заголовка
    # или из /ru/, /en/, /ka/ префикса URL

    courses = Course.objects.filter(status='active')

    # Все переводы автоматически выбираются
    return courses
```

## Админка Django

### Автоматическая конфигурация

После настройки translation.py админка автоматически показывает табы с языками:

```
┌─────────────────────────────────────┐
│ Курс: Основы Python                 │
│ ┌─────┬─────┬─────┐                │
│ │ RU  │ EN  │ KA  │                │
│ └─────┴─────┴─────┘                │
│                                     │
│ [RU] Название: Основы Python        │
│ [RU] Описание: ...                  │
│                                     │
│ [EN] Name: Python Basics            │
│ [EN] Description: ...               │
│                                     │
│ [KA] სახელი: ...                    │
│ [KA] აღწერა: ...                    │
└─────────────────────────────────────┘
```

### Кастомизация админки

```python
# courses/admin.py

from django.contrib import admin
from modeltranslation.admin import TranslationAdmin, TranslationTabularInline

from .models import Course, Lesson, Step, Tip


class LessonInline(TranslationTabularInline):
    """
    Инлайн для уроков с поддержкой переводов.
    """
    model = Lesson
    fields = ('lesson_number', 'name', 'short_description')
    extra = 0


class StepInline(TranslationTabularInline):
    """
    Инлайн для шагов с поддержкой переводов.
    """
    model = Step
    fields = ('step_number', 'name', 'description')
    extra = 0


@admin.register(Course)
class CourseAdmin(TranslationAdmin):
    """
    Админка курса с табами языков.
    """
    list_display = ('name', 'category', 'status', 'created_at')
    list_filter = ('status', 'category', 'is_featured')
    search_fields = ('name_ru', 'name_en', 'name_ka')
    prepopulated_fields = {'slug': ('name',)}

    # Группировка полей по вкладкам
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'category', 'status')
        }),
        ('Описание', {
            'fields': ('short_description', 'description')
        }),
        ('Медиа', {
            'fields': ('image',)
        }),
        ('Цены и рейтинг', {
            'fields': ('price', 'rating', 'is_featured')
        }),
    )

    inlines = [LessonInline]


@admin.register(Step)
class StepAdmin(TranslationAdmin):
    """
    Админка шага с табами языков.
    """
    list_display = ('name', 'lesson', 'step_number')
    list_filter = ('lesson__course',)
    search_fields = ('name_ru', 'name_en', 'name_ka')

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'lesson', 'step_number')
        }),
        ('Контент', {
            'fields': ('description', 'actions', 'self_check')
        }),
        ('Дополнительно', {
            'fields': ('repair_description', 'image'),
            'classes': ('collapse',)
        }),
    )
```

## Workflow добавления курсов

### 1. Создание курса в админке

1. Перейти в админку `/admin/courses/course/add/`
2. Переключиться на вкладку **RU** (основной язык)
3. Заполнить все обязательные поля на русском
4. Переключиться на вкладку **EN**
5. Заполнить английский перевод (минимум название)
6. Переключиться на вкладку **KA**
7. Заполнить грузинский перевод (минимум название)
8. Сохранить

### 2. Массовый импорт через Django shell

```python
from courses.models import Course, Lesson, Step
from django.utils.translation import activate

# Создание курса
activate('ru')
course = Course.objects.create(
    name="Основы Python",
    short_description="Изучите основы программирования на Python",
    description="Полное описание курса...",
    slug="python-basics",
    category="python",
    status="active"
)

# Добавить переводы
course.name_en = "Python Basics"
course.short_description_en = "Learn Python programming fundamentals"
course.description_en = "Full course description..."

course.name_ka = "Python-ის საფუძვლები"
course.short_description_ka = "ისწავლეთ Python პროგრამირება"
course.save()

# Создание урока
lesson = Lesson.objects.create(
    course=course,
    name="Введение в Python",
    short_description="Первые шаги в программировании",
    lesson_number=1
)

lesson.name_en = "Introduction to Python"
lesson.short_description_en = "First steps in programming"
lesson.save()

# Создание шагов
for i in range(1, 11):
    step = Step.objects.create(
        lesson=lesson,
        name=f"Шаг {i}: Тема",
        description=f"Описание шага {i}...",
        actions=f"Действия для шага {i}...",
        self_check=f"Проверка для шага {i}...",
        step_number=i
    )

    step.name_en = f"Step {i}: Topic"
    step.description_en = f"Description for step {i}..."
    step.actions_en = f"Actions for step {i}..."
    step.self_check_en = f"Self-check for step {i}..."
    step.save()
```

### 3. Импорт из JSON

```python
import json
from courses.models import Course, Lesson, Step

# Структура JSON файла
course_data = {
    "ru": {
        "name": "Основы Python",
        "short_description": "Краткое описание",
        "description": "Полное описание",
        "lessons": [
            {
                "name": "Урок 1",
                "short_description": "Описание урока",
                "steps": [
                    {
                        "name": "Шаг 1",
                        "description": "Описание",
                        "actions": "Действия",
                        "self_check": "Проверка"
                    }
                ]
            }
        ]
    },
    "en": {
        "name": "Python Basics",
        "short_description": "Short description",
        "description": "Full description",
        "lessons": [...]
    }
}

def import_course_from_json(data):
    """Импорт курса из JSON с переводами."""

    # Создать курс с русскими данными
    course = Course.objects.create(
        name=data['ru']['name'],
        short_description=data['ru']['short_description'],
        description=data['ru']['description'],
        slug=slugify(data['ru']['name']),
        status='draft'
    )

    # Добавить переводы
    for lang in ['en', 'ka']:
        if lang in data:
            setattr(course, f'name_{lang}', data[lang]['name'])
            setattr(course, f'short_description_{lang}', data[lang]['short_description'])
            setattr(course, f'description_{lang}', data[lang]['description'])

    course.save()

    # Импорт уроков
    for lesson_idx, lesson_data_ru in enumerate(data['ru']['lessons'], 1):
        lesson = Lesson.objects.create(
            course=course,
            name=lesson_data_ru['name'],
            short_description=lesson_data_ru['short_description'],
            lesson_number=lesson_idx
        )

        # Добавить переводы уроков
        for lang in ['en', 'ka']:
            if lang in data and len(data[lang]['lessons']) >= lesson_idx:
                lesson_data = data[lang]['lessons'][lesson_idx - 1]
                setattr(lesson, f'name_{lang}', lesson_data['name'])
                setattr(lesson, f'short_description_{lang}', lesson_data['short_description'])

        lesson.save()

        # Импорт шагов
        for step_idx, step_data_ru in enumerate(lesson_data_ru['steps'], 1):
            step = Step.objects.create(
                lesson=lesson,
                name=step_data_ru['name'],
                description=step_data_ru.get('description', ''),
                actions=step_data_ru.get('actions', ''),
                self_check=step_data_ru.get('self_check', ''),
                step_number=step_idx
            )

            # Добавить переводы шагов
            for lang in ['en', 'ka']:
                if lang in data:
                    lesson_data = data[lang]['lessons'][lesson_idx - 1]
                    if len(lesson_data['steps']) >= step_idx:
                        step_data = lesson_data['steps'][step_idx - 1]
                        setattr(step, f'name_{lang}', step_data['name'])
                        setattr(step, f'description_{lang}', step_data.get('description', ''))
                        setattr(step, f'actions_{lang}', step_data.get('actions', ''))
                        setattr(step, f'self_check_{lang}', step_data.get('self_check', ''))

            step.save()

    return course
```

## Management команды

### Создать команду для импорта курсов

```python
# courses/management/commands/import_course.py

from django.core.management.base import BaseCommand
import json

class Command(BaseCommand):
    help = 'Import course from JSON file with translations'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to JSON file')

    def handle(self, *args, **options):
        with open(options['json_file'], 'r', encoding='utf-8') as f:
            data = json.load(f)

        course = import_course_from_json(data)

        self.stdout.write(
            self.style.SUCCESS(f'Successfully imported course: {course.name}')
        )
```

Использование:
```bash
python manage.py import_course courses/data/python_basics.json
```

## Переключение языка

### В URL

```python
# urls.py
from django.conf.urls.i18n import i18n_patterns

urlpatterns = i18n_patterns(
    path('', include('core.urls')),
    path('courses/', include('courses.urls')),
    path('blog/', include('blog.urls')),
    # ...
)
```

Результат:
- `/ru/courses/` - русская версия
- `/en/courses/` - английская версия
- `/ka/courses/` - грузинская версия

### По заголовку Accept-Language

Django автоматически определяет язык из HTTP заголовка.

### По выбору пользователя

```python
from django.utils.translation import activate

def set_language(request, language):
    activate(language)
    request.session[LANGUAGE_SESSION_KEY] = language
    return redirect(request.META.get('HTTP_REFERER', '/'))
```

## Fallback языков

Если перевод отсутствует, используется fallback:

```python
# settings.py
MODELTRANSLATION_FALLBACK_LANGUAGES = ('ru', 'en')

# Пример:
activate('ka')
course = Course.objects.get(slug='test')
# Если name_ka пусто, вернет name_ru
# Если name_ru тоже пусто, вернет name_en
print(course.name)
```

## Лучшие практики

### 1. Обязательные поля

Делайте только самые важные поля обязательными для перевода:

```python
required_languages = {
    'ru': ('name', 'short_description'),  # Основной контент
    'en': ('name',),                       # Минимум для других языков
    'ka': ('name',),
}
```

### 2. Постепенное добавление переводов

1. Сначала создать весь контент на русском
2. Перевести названия на английский
3. Постепенно добавлять полные переводы
4. Грузинский - по необходимости

### 3. Используйте placeholder

Для не переведенного контента используйте placeholder:

```python
@register(Course)
class CourseTranslationOptions(TranslationOptions):
    fields = ('name', 'description')

    # Если перевод отсутствует, показать "[EN] название на русском"
    empty_values = {'': None, None: None}
```

### 4. Мониторинг переводов

Создайте management команду для проверки:

```python
# courses/management/commands/check_translations.py

from django.core.management.base import BaseCommand
from courses.models import Course, Lesson, Step

class Command(BaseCommand):
    help = 'Check translation coverage'

    def handle(self, *args, **options):
        languages = ['ru', 'en', 'ka']
        models = [Course, Lesson, Step]

        for model in models:
            self.stdout.write(f"\n{model.__name__}:")

            for lang in languages:
                total = model.objects.count()
                translated = model.objects.exclude(**{f'name_{lang}': ''}).count()
                percentage = (translated / total * 100) if total > 0 else 0

                self.stdout.write(
                    f"  {lang}: {translated}/{total} ({percentage:.1f}%)"
                )
```

## Резюме

### Файлы для создания

1. `courses/translation.py` - Конфигурация переводов
2. `blog/translation.py` - Конфигурация переводов блога
3. `courses/management/commands/import_course.py` - Импорт курсов
4. `courses/management/commands/check_translations.py` - Проверка переводов
5. `docs/LOCALIZATION_GUIDE.md` - Эта инструкция

### Команды для запуска

```bash
# 1. Установка
poetry add django-modeltranslation

# 2. Создание миграций
python manage.py makemigrations

# 3. Применение миграций
python manage.py migrate

# 4. Копирование существующего контента
python manage.py update_translation_fields

# 5. Проверка переводов
python manage.py check_translations

# 6. Импорт курса
python manage.py import_course courses/data/course.json
```

### Структура данных

```
Course (Курс)
├── name_ru, name_en, name_ka
├── description_ru, description_en, description_ka
├── short_description_ru, short_description_en, short_description_ka
└── Lessons (Уроки)
    ├── name_ru, name_en, name_ka
    ├── short_description_ru, short_description_en, short_description_ka
    └── Steps (Шаги)
        ├── name_ru, name_en, name_ka
        ├── description_ru, description_en, description_ka
        ├── actions_ru, actions_en, actions_ka
        ├── self_check_ru, self_check_en, self_check_ka
        └── repair_description_ru, repair_description_en, repair_description_ka
```

---

**Автор**: Pyland Team
**Дата**: 28 января 2026
**Версия**: 1.0
