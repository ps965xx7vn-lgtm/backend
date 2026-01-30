"""
Blog Application

Полнофункциональное приложение блога для Django платформы Pyland School.

Основные компоненты:
- Модели: Article, Category, Comment, Series, Author, ArticleReaction
- API: 12 REST эндпоинтов (Django Ninja)
- Views: 24 Django представления
- Кеширование: Redis для оптимизации производительности
- SEO: Мета-теги, sitemap, schema.org
- Newsletter: Интеграция с централизованной системой notifications.Subscription

Модули:
    models.py - 10 моделей данных
    views.py - 24 класс-based views (включая NewsletterSubscribeView)
    api.py - REST API эндпоинты (12 endpoints)
    schemas.py - Pydantic схемы для валидации
    forms.py - Django формы (CommentForm)
    admin.py - Админ панель (10 ModelAdmin классов)
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
