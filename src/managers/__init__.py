"""
Manager Application - Административная панель управления платформой Pyland.

Этот модуль предоставляет административные функции для управления платформой:
    - Обработка обратной связи (Feedback)
    - Просмотр системных логов (SystemLog)
    - Управление настройками (SystemSettings)
    - Dashboard с общей статистикой

Компоненты:
    - models.py: Модели данных (Feedback, SystemLog, SystemSettings)
    - api.py: REST API эндпоинты (только для staff)
    - views.py: Django views для dashboard
    - admin.py: Конфигурация Django admin
    - middleware.py: Rate limiting и security headers
    - cache_utils.py: Утилиты кеширования
    - schemas.py: Pydantic схемы для API
    - forms.py: Django формы

Автор: Pyland Team
Дата: 2025
"""
