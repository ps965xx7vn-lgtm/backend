"""
Payments Tests Package - Тесты для приложения payments.

Структура тестов:
    - conftest.py: Фикстуры для тестов
    - factories.py: Factory Boy фабрики
    - test_models.py: Тесты моделей Payment
    - test_paddle_service.py: Тесты PaddleService
    - test_currency_service.py: Тесты CurrencyService
    - test_views.py: Тесты представлений
    - test_api.py: Тесты API endpoints
    - test_forms.py: Тесты форм
    - test_tasks.py: Тесты Celery задач
    - test_integration.py: Интеграционные тесты

Покрытие:
    - Unit тесты для всех компонентов
    - Integration тесты для процесса оплаты
    - Mock тесты для Paddle API
"""
