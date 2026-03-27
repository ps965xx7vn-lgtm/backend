"""
Payments Application - Модуль обработки платежей

Платформа: Pyland School
Назначение: Обработка покупок курсов через Paddle Billing

Основные возможности:
    ✅ Интеграция с Paddle Billing (международные платежи)
    ✅ Поддержка нескольких валют (USD, EUR, RUB, GEL)
    ✅ Динамические курсы валют с автообновлением каждый час
    ✅ Безопасный checkout через Paddle.js overlay
    ✅ Автоматическое зачисление студента после оплаты
    ✅ Отслеживание статусов платежей и обработка webhook
    ✅ REST API для операций с платежами
    ✅ Thread-safe singleton services

Компоненты:
    models.py          - Модель Payment с методами жизненного цикла
    paddle_service.py  - Интеграция с Paddle API (паттерн Singleton)
    currency_service.py - Динамические курсы валют (паттерн Singleton)
    tasks.py           - Celery задачи для автообновления курсов (каждый час)
    views.py           - Django представления для checkout и результатов
    api.py             - REST API эндпоинты (Django Ninja)
    forms.py           - CheckoutForm с валидацией
    schemas.py         - Pydantic схемы для API
    constants.py       - CSP домены для Paddle.js
    admin.py           - Кастомные отображения в админке

Процесс оплаты:
    1. Студент переходит на страницу курса → нажимает "Купить"
    2. Страница checkout: выбор валюты, принятие условий
    3. Создание Payment (status="pending")
    4. Вызов Paddle API → получение transaction + client_token
    5. Перенаправление на Paddle.js overlay checkout
    6. Завершение оплаты → получение webhook
    7. Обновление статуса → зачисление студента на курс
    8. Отображение страницы успеха

Динамические курсы валют:
    - Автоматическое обновление каждый час через Celery Beat
    - Кэширование в Redis (TTL = 1 час)
    - Fallback на статичные курсы при ошибке API
    - Thread-safe Singleton pattern для CurrencyService
    - Фоновая задача: payments.update_currency_rates (каждый час)
    - Management command: poetry run python src/manage.py update_currency_rates
    - Гарантия актуальных цен без ручного вмешательства
    - Логирование всех обновлений курсов

Статусы:
    pending    - Платеж создан, ожидает обработки
    processing - Транзакция Paddle в процессе
    completed  - ✅ Платеж успешен, студент зачислен
    failed     - ❌ Ошибка платежа
    cancelled  - Пользователь закрыл checkout
    refunded   - Средства возвращены

Безопасность:
    🔒 JWT аутентификация (Django Ninja)
    🔒 CSP заголовки для Paddle.js
    🔒 Верификация подписи webhook
    🔒 UUID первичные ключи (непоследовательные)
    🔒 JSON поле для ответов Paddle (без чувствительных данных)

Доступ:
    Все эндпоинты требуют аутентификации кроме:
    - Health check (/api/payments/ping)
    - Webhook handler (/api/payments/paddle/webhook)

Окружение:
    sandbox    - Тестовое окружение (тестовые карты)
    production - Реальные платежи (настоящие деньги)

Переменные окружения:
    PADDLE_SANDBOX_API_KEY    - Sandbox API ключ (обязательно для разработки)
    PADDLE_API_KEY            - Production API ключ (обязательно для production)
    PADDLE_ENVIRONMENT        - 'sandbox' или 'production'
    PADDLE_WEBHOOK_SECRET     - Secret для верификации webhook
    EXCHANGE_RATE_API_KEY     - API ключ для курсов валют (опционально)

Документация:
    src/payments/README.md                    - Обзор приложения
    docs/payments/PADDLE_INTEGRATION.md       - Технические детали Paddle
    docs/payments/PADDLE_TESTING.md           - Руководство по тестированию
    docs/payments/CURRENCY_SETUP.md           - Настройка динамических курсов
"""
