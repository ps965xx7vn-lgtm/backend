"""
Core Application

Основное приложение платформы Pyland School.

Содержит:
- Главную страницу и лендинг
- Страницы контактов и "О нас"
- Формы обратной связи и подписки
- Юридические страницы (Terms of Service, Privacy Policy)
- API эндпоинты для публичных функций
- Template tags для работы с Markdown
- Контекст-процессоры для footer данных

Modules:
    views: View функции для основных страниц
    forms: Формы обратной связи и подписки
    api: REST API эндпоинты (feedback, subscription, stats, contacts)
    schemas: Pydantic схемы для валидации API
    urls: URL маршруты приложения
    context_processors: Глобальные данные для шаблонов
    templatetags.markdown_filters: Фильтры для работы с Markdown
    templatetags.article_tags: Фильтры для статей блога

API Endpoints:
    POST /api/core/feedback/ - отправка обратной связи
    POST /api/core/subscribe/ - подписка на рассылку
    GET /api/core/contact-info/ - контактная информация
    GET /api/core/stats/ - статистика платформы

Tests:
    43 теста (15 API + 28 schemas) - 100% проходят
"""
