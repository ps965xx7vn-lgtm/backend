"""
Blog Tests Package.

Современная структура тестов для приложения Blog.

Структура:
    - conftest.py - Pytest fixtures и настройки
    - factories.py - Factory Boy фабрики для создания тестовых данных
    - test_models.py - Тесты моделей
    - test_api.py - Тесты REST API эндпоинтов
    - test_views.py - Тесты Django views
    - test_forms.py - Тесты форм
    - test_admin.py - Тесты админки
    - test_schemas.py - Тесты Pydantic схем

Технологии:
    - pytest - Фреймворк для тестирования
    - pytest-django - Django интеграция
    - factory-boy - Создание тестовых данных
    - pytest-cov - Покрытие кода тестами
    - freezegun - Мокирование времени
"""
