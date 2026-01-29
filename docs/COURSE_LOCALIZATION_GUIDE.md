# Руководство по локализации курсов Pyland (Poetry)

## 📋 Содержание

1. [Быстрый старт](#быстрый-старт)
2. [Структура курса](#структура-курса)
3. [Создание JSON с локализацией](#создание-json-с-локализацией)
4. [Импорт курса в базу данных](#импорт-курса-в-базу-данных)
5. [Работа через Django Admin](#работа-через-django-admin)
6. [Проверка переводов](#проверка-переводов)
7. [Best Practices](#best-practices)

---

## 🚀 Быстрый старт

### 1. Установка django-modeltranslation

```bash
# Активируйте Poetry окружение
poetry shell
cd src

# Установите пакет
poetry add django-modeltranslation
```

### 2. Настройка settings.py

```python
# src/pyland/settings.py

INSTALLED_APPS = [
    'modeltranslation',  # ⚠️ ОБЯЗАТЕЛЬНО ПЕРЕД 'django.contrib.admin'
    'django.contrib.admin',
    'django.contrib.auth',
    # ... остальные приложения
    'courses',
]

# Языки проекта
LANGUAGES = [
    ('ru', 'Русский'),
    ('en', 'English'),
    ('ka', 'ქართული'),
]

# Язык по умолчанию
LANGUAGE_CODE = 'ru'

# Настройки modeltranslation
MODELTRANSLATION_DEFAULT_LANGUAGE = 'ru'
MODELTRANSLATION_LANGUAGES = ('ru', 'en', 'ka')
MODELTRANSLATION_FALLBACK_LANGUAGES = ('ru', 'en')
MODELTRANSLATION_PREPOPULATE_LANGUAGE = 'ru'
```

### 3. Создание translation.py

Файл уже создан в `src/courses/translation.py`:

```python
from modeltranslation.translator import translator, TranslationOptions
from .models import Course, Lesson, Step, Tip, ExtraSource


@translator.register(Course)
class CourseTranslationOptions(TranslationOptions):
    fields = ('name', 'description', 'short_description')
    required_languages = {'ru': ('name', 'description'), 'en': ('name',), 'ka': ('name',)}


@translator.register(Lesson)
class LessonTranslationOptions(TranslationOptions):
    fields = ('name', 'short_description')
    required_languages = {'ru': ('name',), 'en': ('name',), 'ka': ('name',)}


@translator.register(Step)
class StepTranslationOptions(TranslationOptions):
    fields = ('name', 'description', 'actions', 'self_check', 'repair_description')
    required_languages = {
        'ru': ('name', 'description', 'actions'),
        'en': ('name',),
        'ka': ('name',)
    }


@translator.register(Tip)
class TipTranslationOptions(TranslationOptions):
    fields = ('title', 'description')
    required_languages = {'ru': ('title', 'description')}


@translator.register(ExtraSource)
class ExtraSourceTranslationOptions(TranslationOptions):
    fields = ('title', 'description', 'url')
    required_languages = {'ru': ('title',)}
```

### 4. Создание миграций

```bash
# Создайте миграции для полей переводов
python manage.py makemigrations

# Примените миграции
python manage.py migrate

# Обновите существующие данные (если есть)
python manage.py update_translation_fields
```

### 5. Импорт примера курса

```bash
# Импортируйте курс "Основы Git и GitHub"
python manage.py import_course docs/examples/git_github_course.json
```

---

## 📚 Структура курса

### Иерархия моделей

```
Course (Курс)
├── name, description, short_description
├── category, price, status
└── Lessons[] (Уроки)
    ├── name, short_description
    ├── order
    └── Steps[] (Шаги)
        ├── name, description, actions
        ├── self_check, repair_description
        ├── order, is_required
        ├── Tips[] (Подсказки)
        │   └── title, description
        └── ExtraSources[] (Доп. материалы)
            └── title, description, url
```

### Поля для локализации

#### Course (Курс)
- ✅ **name** - Название курса (обязательно для всех языков)
- ✅ **description** - Полное описание (обязательно для ru)
- ✅ **short_description** - Краткое описание (обязательно для ru)

#### Lesson (Урок)
- ✅ **name** - Название урока (обязательно для всех языков)
- ✅ **short_description** - Краткое описание (рекомендуется для ru)

#### Step (Шаг)
- ✅ **name** - Название шага (обязательно для всех языков)
- ✅ **description** - Теоретическое описание (обязательно для ru, en, ka)
- ✅ **actions** - Практические действия (обязательно для ru, en, ka)
- ✅ **self_check** - Проверка понимания (рекомендуется для всех)
- ✅ **repair_description** - Что делать если не получилось (рекомендуется)

#### Tip (Подсказка)
- ✅ **title** - Заголовок подсказки (обязательно для ru)
- ✅ **description** - Текст подсказки (обязательно для ru)

#### ExtraSource (Доп. материал)
- ✅ **title** - Название материала (обязательно для ru)
- ✅ **description** - Описание материала (опционально)
- ✅ **url** - Ссылка (может быть разной для языков)

---

## 🗂️ Создание JSON с локализацией

### Пример структуры

```json
{
  "ru": {
    "name": "Название курса",
    "short_description": "Краткое описание",
    "description": "Полное описание курса",
    "category": "programming",
    "price": 0,
    "status": "active",
    "lessons": [
      {
        "name": "Название урока",
        "short_description": "Описание урока",
        "steps": [
          {
            "name": "Название шага",
            "description": "Теория: что нужно знать",
            "actions": "1. Первое действие\n2. Второе действие",
            "self_check": "Вопросы для проверки понимания",
            "repair_description": "Что делать если не получилось"
          }
        ]
      }
    ]
  },
  "en": {
    "name": "Course Title",
    "short_description": "Short description",
    "description": "Full course description",
    "category": "programming",
    "price": 0,
    "status": "active",
    "lessons": [
      {
        "name": "Lesson Title",
        "short_description": "Lesson description",
        "steps": [
          {
            "name": "Step Title",
            "description": "Theory: what you need to know",
            "actions": "1. First action\n2. Second action",
            "self_check": "Questions to check understanding",
            "repair_description": "What to do if it doesn't work"
          }
        ]
      }
    ]
  },
  "ka": {
    "name": "კურსის სახელწოდება",
    // ... аналогично
  }
}
```

### Создание минимального курса

Для минимального курса достаточно:

```json
{
  "ru": {
    "name": "Тестовый курс",
    "description": "Описание",
    "short_description": "Краткое",
    "category": "other",
    "price": 0,
    "status": "draft",
    "lessons": [
      {
        "name": "Урок 1",
        "steps": [
          {
            "name": "Шаг 1",
            "description": "Текст шага",
            "actions": "Действия"
          }
        ]
      }
    ]
  },
  "en": {
    "name": "Test Course",
    "description": "Description",
    "short_description": "Short",
    "category": "other",
    "price": 0,
    "status": "draft",
    "lessons": [
      {
        "name": "Lesson 1",
        "steps": [
          {
            "name": "Step 1",
            "description": "Step text",
            "actions": "Actions"
          }
        ]
      }
    ]
  }
}
```

---

## 💾 Импорт курса в базу данных

### Создание команды импорта

Создайте файл `src/courses/management/commands/import_course.py`:

```python
import json
import logging
from django.core.management.base import BaseCommand
from django.db import transaction
from courses.models import Course, Lesson, Step

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Import course from JSON file with translations'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to JSON file')

    def handle(self, *args, **options):
        json_file = options['json_file']

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            with transaction.atomic():
                # Создаём курс с русскими данными
                ru_data = data.get('ru', {})
                course = Course.objects.create(
                    name_ru=ru_data.get('name'),
                    description_ru=ru_data.get('description'),
                    short_description_ru=ru_data.get('short_description'),
                    category=ru_data.get('category', 'other'),
                    price=ru_data.get('price', 0),
                    status=ru_data.get('status', 'draft'),
                )

                # Добавляем английские переводы
                en_data = data.get('en', {})
                if en_data:
                    course.name_en = en_data.get('name')
                    course.description_en = en_data.get('description')
                    course.short_description_en = en_data.get('short_description')

                # Добавляем грузинские переводы
                ka_data = data.get('ka', {})
                if ka_data:
                    course.name_ka = ka_data.get('name')
                    course.description_ka = ka_data.get('description')
                    course.short_description_ka = ka_data.get('short_description')

                course.save()

                # Импортируем уроки
                for lang_code in ['ru', 'en', 'ka']:
                    lang_data = data.get(lang_code, {})
                    lessons_data = lang_data.get('lessons', [])

                    for order, lesson_data in enumerate(lessons_data, start=1):
                        # Создаём урок только один раз (для русского)
                        if lang_code == 'ru':
                            lesson = Lesson.objects.create(
                                course=course,
                                name_ru=lesson_data.get('name'),
                                short_description_ru=lesson_data.get('short_description'),
                                order=order
                            )
                        else:
                            # Обновляем переводы существующего урока
                            lesson = course.lessons.all()[order - 1]
                            setattr(lesson, f'name_{lang_code}', lesson_data.get('name'))
                            setattr(lesson, f'short_description_{lang_code}',
                                   lesson_data.get('short_description'))
                            lesson.save()

                        # Импортируем шаги
                        steps_data = lesson_data.get('steps', [])
                        for step_order, step_data in enumerate(steps_data, start=1):
                            if lang_code == 'ru':
                                step = Step.objects.create(
                                    lesson=lesson,
                                    name_ru=step_data.get('name'),
                                    description_ru=step_data.get('description'),
                                    actions_ru=step_data.get('actions'),
                                    self_check_ru=step_data.get('self_check'),
                                    repair_description_ru=step_data.get('repair_description'),
                                    order=step_order,
                                    is_required=True
                                )
                            else:
                                step = lesson.steps.all()[step_order - 1]
                                setattr(step, f'name_{lang_code}', step_data.get('name'))
                                setattr(step, f'description_{lang_code}',
                                       step_data.get('description'))
                                setattr(step, f'actions_{lang_code}',
                                       step_data.get('actions'))
                                setattr(step, f'self_check_{lang_code}',
                                       step_data.get('self_check'))
                                setattr(step, f'repair_description_{lang_code}',
                                       step_data.get('repair_description'))
                                step.save()

                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Course "{course.name}" imported successfully!\n'
                        f'   ID: {course.id}\n'
                        f'   Lessons: {course.lessons.count()}\n'
                        f'   Total Steps: {sum(l.steps.count() for l in course.lessons.all())}'
                    )
                )

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'❌ File not found: {json_file}'))
        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f'❌ Invalid JSON: {e}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Import failed: {e}'))
            logger.exception('Course import error')
```

### Использование команды

```bash
# Импорт курса
python manage.py import_course docs/examples/git_github_course.json

# Вывод:
# ✅ Course "Основы Git и GitHub" imported successfully!
#    ID: 1
#    Lessons: 5
#    Total Steps: 50
```

---

## 🎨 Работа через Django Admin

### После применения миграций

Django Admin автоматически получит табы для переводов:

```
┌─────────────────────────────────────┐
│ Course: Основы Git и GitHub         │
├─────────────────────────────────────┤
│ [Русский] [English] [ქართული]      │  ← Табы языков
│                                     │
│ Название (ru): [Основы Git...]      │
│ Описание (ru): [Научитесь...]       │
│ Краткое (ru):  [Научитесь...]       │
│                                     │
│ Категория: [programming ▼]          │
│ Цена: [0]                           │
│ Статус: [active ▼]                  │
│                                     │
│         [Сохранить и продолжить]    │
└─────────────────────────────────────┘
```

### Добавление курса через Admin

1. Откройте http://localhost:8000/admin/courses/course/
2. Нажмите "Добавить курс"
3. Заполните **основные поля** (без языкового кода):
   - name, description, short_description
   - category, price, status
4. Нажмите "Сохранить и продолжить"
5. Переключитесь на таб **English**
6. Заполните переводы
7. Переключитесь на таб **ქართული**
8. Заполните переводы
9. Сохраните

### Массовое редактирование

Для массового перевода используйте **Django Shell**:

```python
python manage.py shell

from courses.models import Course

course = Course.objects.get(id=1)

# Русский (уже заполнен)
print(course.name_ru)  # "Основы Git и GitHub"

# Добавляем английский перевод
course.name_en = "Git and GitHub Basics"
course.description_en = "Learn Git from scratch"
course.save()

# Добавляем грузинский
course.name_ka = "Git და GitHub-ის საფუძვლები"
course.save()

# Проверка
print(course.name)     # Текущий язык (ru)
print(course.name_en)  # "Git and GitHub Basics"
print(course.name_ka)  # "Git და GitHub-ის საფუძვლები"
```

---

## ✅ Проверка переводов

### Команда check_translations

Используйте команду из `src/courses/management/commands/check_translations.py`:

```bash
# Проверка всех переводов
python manage.py check_translations

# Вывод:
# 📊 Translation Coverage Report
# ═══════════════════════════════════════════════
#
# Course Model:
# ✅ Русский (ru): 100% (3/3 fields)
# ✅ English (en): 100% (3/3 fields)
# ⚠️  ქართული (ka): 67% (2/3 fields) - missing: description_ka
#
# Lesson Model:
# ✅ Русский (ru): 100% (10/10 lessons)
# ✅ English (en): 100% (10/10 lessons)
# ✅ ქართული (ka): 100% (10/10 lessons)
#
# Step Model:
# ✅ Русский (ru): 100% (50/50 steps)
# ⚠️  English (en): 80% (40/50 steps) - 10 steps incomplete
# ⚠️  ქართული (ka): 60% (30/50 steps) - 20 steps incomplete

# Детальная проверка
python manage.py check_translations --detailed

# Вывод покажет конкретные недостающие переводы
```

### Ручная проверка в Shell

```python
from courses.models import Course, Lesson, Step
from django.utils.translation import activate

# Активируйте нужный язык
activate('en')

course = Course.objects.get(id=1)
print(course.name)  # Автоматически вернёт name_en

# Проверка всех языков
for lang in ['ru', 'en', 'ka']:
    activate(lang)
    print(f"{lang}: {course.name}")

# Вывод:
# ru: Основы Git и GitHub
# en: Git and GitHub Basics
# ka: Git და GitHub-ის საფუძვლები
```

---

## 📋 Best Practices

### 1. Структура переводов

✅ **Правильно:**
- Один JSON файл = один курс
- Все языки в одном файле
- Одинаковая структура для всех языков

❌ **Неправильно:**
- Разные файлы для разных языков
- Неполная структура в некоторых языках
- Отсутствие обязательных полей

### 2. Качество переводов

✅ **Правильно:**
- Профессиональный перевод
- Адаптация примеров под язык
- Проверка носителем языка

❌ **Неправильно:**
- Машинный перевод без проверки
- Прямой дословный перевод
- Использование терминов не на языке аудитории

### 3. Обязательные поля

**Минимум для публикации:**
- Course: name_ru, name_en, description_ru
- Lesson: name_ru, name_en
- Step: name_ru, name_en, description_ru, actions_ru

**Рекомендуется:**
- Все поля для ru, en
- Основные поля для ka
- self_check для всех шагов
- repair_description для сложных шагов

### 4. Версионирование

```bash
# Храните JSON файлы в Git
git add docs/examples/git_github_course.json
git commit -m "Add Git & GitHub course with full translations"

# Создавайте версии при обновлениях
git tag course-git-v1.0
```

### 5. Тестирование

```python
# Создайте тесты для проверки переводов
# src/courses/tests/test_translations.py

import pytest
from django.utils.translation import activate
from courses.models import Course


@pytest.mark.django_db
class TestCourseTranslations:
    def test_course_has_all_translations(self):
        course = Course.objects.create(
            name_ru="Тест",
            name_en="Test",
            name_ka="ტესტი"
        )

        activate('ru')
        assert course.name == "Тест"

        activate('en')
        assert course.name == "Test"

        activate('ka')
        assert course.name == "ტესტი"

    def test_fallback_translation(self):
        course = Course.objects.create(
            name_ru="Тест",
            name_en="Test"
            # name_ka не задан
        )

        activate('ka')
        # Должен использовать fallback (ru или en)
        assert course.name in ["Тест", "Test"]
```

### 6. Производительность

```python
# Используйте select_related для уменьшения запросов
courses = Course.objects.prefetch_related(
    'lessons__steps__tips',
    'lessons__steps__extra_sources'
).all()

# Для API используйте Pydantic schemas с переводами
from pydantic import BaseModel

class CourseSchema(BaseModel):
    id: int
    name: str  # Автоматически выберет нужный язык
    description: str

    class Config:
        from_attributes = True
```

### 7. Экспорт курсов

Создайте команду для экспорта:

```python
# src/courses/management/commands/export_course.py

from django.core.management.base import BaseCommand
import json


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('course_id', type=int)
        parser.add_argument('output_file', type=str)

    def handle(self, *args, **options):
        course = Course.objects.get(id=options['course_id'])

        data = {
            'ru': self.export_language(course, 'ru'),
            'en': self.export_language(course, 'en'),
            'ka': self.export_language(course, 'ka'),
        }

        with open(options['output_file'], 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
```

---

## 🎯 Пример реального workflow

### Создание нового курса "Python Основы"

```bash
# 1. Создайте JSON файл
nano docs/examples/python_basics_course.json

# 2. Заполните структуру для всех языков (ru, en, ka)

# 3. Импортируйте курс
python manage.py import_course docs/examples/python_basics_course.json

# 4. Проверьте переводы
python manage.py check_translations

# 5. Откройте в Admin для финальной проверки
python manage.py runserver
# http://localhost:8000/admin/courses/course/

# 6. Опубликуйте курс (измените status на 'active')

# 7. Закоммитьте в Git
git add docs/examples/python_basics_course.json
git commit -m "feat: Add Python Basics course with full localization"
git push origin dev
```

---

## 🆘 Troubleshooting

### Проблема: Переводы не отображаются в Admin

**Решение:**
```bash
# 1. Проверьте, что modeltranslation в INSTALLED_APPS
# 2. Проверьте, что он ПЕРЕД django.contrib.admin
# 3. Пересоздайте миграции
python manage.py makemigrations courses
python manage.py migrate
```

### Проблема: Fallback не работает

**Решение:**
```python
# settings.py
MODELTRANSLATION_FALLBACK_LANGUAGES = ('ru', 'en')  # ru первым!
```

### Проблема: Импорт курса завершается с ошибкой

**Решение:**
```bash
# Проверьте структуру JSON
python -m json.tool docs/examples/your_course.json

# Проверьте обязательные поля
# Добавьте логирование в команду import_course
```

### Проблема: Слишком долгий импорт

**Решение:**
```python
# Используйте bulk_create для шагов
steps = [
    Step(lesson=lesson, name_ru=data['name'], order=i)
    for i, data in enumerate(steps_data, 1)
]
Step.objects.bulk_create(steps)
```

---

## 📚 Полезные ссылки

- [django-modeltranslation Documentation](https://django-modeltranslation.readthedocs.io/)
- [Django i18n Guide](https://docs.djangoproject.com/en/5.2/topics/i18n/)
- [Poetry Documentation](https://python-poetry.org/docs/)
- [Git & GitHub Course Example](./examples/git_github_course.json)

---

## ✨ Итоги

Теперь у вас есть:

✅ Полное понимание структуры курса
✅ Настроенная система локализации
✅ Готовые команды для импорта/экспорта
✅ Пример курса на 3 языках (50+ шагов)
✅ Инструменты проверки переводов
✅ Best practices для работы с курсами

**Следующий шаг:** Создайте свой первый курс используя `git_github_course.json` как шаблон! 🚀
