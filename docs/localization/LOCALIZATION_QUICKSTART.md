# Быстрый старт: Локализация контента

## Установка (5 минут)

```bash
# 1. Установить пакет
poetry add django-modeltranslation

# 2. Добавить в INSTALLED_APPS (ПЕРЕД django.contrib.admin!)
# settings.py
INSTALLED_APPS = [
    'modeltranslation',  # ← ВАЖНО: перед admin!
    'django.contrib.admin',
    # ...
]

# 3. Настроить языки в settings.py
MODELTRANSLATION_DEFAULT_LANGUAGE = 'ru'
MODELTRANSLATION_LANGUAGES = ('ru', 'en', 'ka')
MODELTRANSLATION_FALLBACK_LANGUAGES = ('ru', 'en')

# 4. Создать миграции
python manage.py makemigrations

# 5. Применить миграции
python manage.py migrate

# 6. Перенести существующие данные
python manage.py update_translation_fields
```

## Использование

### В админке

Все поля автоматически станут табами с языками:

```
┌─ Курс ──────────────────────┐
│ [ RU ] [ EN ] [ KA ]         │
│                              │
│ [RU] Название: Основы Python │
│ [EN] Name: Python Basics     │
│ [KA] სახელი: ...             │
└──────────────────────────────┘
```

### В коде

```python
from django.utils.translation import activate

activate('ru')
course.name  # Вернёт name_ru

activate('en')
course.name  # Вернёт name_en

# Прямой доступ
course.name_ru
course.name_en
course.name_ka
```

### В шаблонах

```django
<!-- Автоматически выбирается язык -->
<h1>{{ course.name }}</h1>

<!-- Принудительно указать язык -->
{% language 'en' %}
    <h1>{{ course.name }}</h1>
{% endlanguage %}
```

## Полная документация

См. [LOCALIZATION_GUIDE.md](LOCALIZATION_GUIDE.md)
