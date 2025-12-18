"""
Blog Application

Полнофункциональное приложение блога для Django платформы Pyland School.

Основные компоненты:
- Модели: Article, Category, Comment, Newsletter, Series, Author, ArticleReaction
- API: 12 REST эндпоинтов (Django Ninja)
- Views: 24 Django представления
- Кеширование: Redis для оптимизации производительности
- SEO: Мета-теги, sitemap, schema.org

Модули:
    models.py - 11 моделей данных (1862 строки)
    views.py - 24 класс-based views (3016 строк)
    api.py - REST API эндпоинты (12 endpoints)
    schemas.py - Pydantic схемы для валидации
    forms.py - Django формы (CommentForm)
    admin.py - Админ панель (11 ModelAdmin классов)
    cache_utils.py - Redis кеширование (8 функций)
    tasks.py - Celery фоновые задачи (5 tasks)
    middleware.py - Rate limiting middleware
    urls.py - URL маршруты (15 patterns)

Тесты:
    tests/ - 149 юнит тестов с 75% покрытием кода

Документация:
    README.md - Полная документация приложения
    templates/README.md - Описание HTML шаблонов
    templatetags/README.md - Custom template tags
"""
