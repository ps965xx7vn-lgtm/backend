"""
Students Application

Приложение личного кабинета студента платформы Pyland School.

Основные компоненты:
- Личный кабинет (dashboard) с прогрессом по курсам
- Управление профилем и настройками
- Просмотр и прохождение курсов и уроков
- Отправка работ на проверку
- Отслеживание замечаний от ревьюеров
- Экспорт данных и удаление аккаунта

Модули:
    models.py - Модели прогресса студента
    views.py - 13 представлений для личного кабинета
    api.py - REST API эндпоинты
    schemas.py - Pydantic схемы для валидации
    forms.py - Django формы профиля
    admin.py - Админ панель
    cache_utils.py - Кеширование прогресса студента
    middleware.py - Rate limiting (1000 req/hour)
    urls.py - URL маршруты (15 patterns)

Доступ:
    Требуется авторизация и роль 'student'

Документация:
    README.md - Полная документация приложения
    MIDDLEWARE_README.md - Описание middleware
    MIDDLEWARE_SETUP.md - Настройка rate limiting
"""
