/**
 * Paddle Checkout Integration
 *
 * Инициализирует Paddle Billing checkout и обрабатывает платежи.
 * Использует Paddle.js v2 SDK для overlay checkout.
 *
 * Требуемые data-атрибуты на контейнере:
 * - data-transaction-id: ID транзакции Paddle
 * - data-client-token: Client Token для аутентификации
 * - data-paddle-env: Окружение (sandbox или production)
 * - data-success-url: URL для редиректа после успеха
 * - data-cancel-url: URL для редиректа при отмене
 * - data-customer-email: Email пользователя
 * - data-has-token: Флаг наличия client token
 */

(function() {
    'use strict';

    /**
     * Получает конфигурацию из data-атрибутов контейнера
     * @returns {Object} Объект с конфигурацией Paddle
     */
    function getPaddleConfig() {
        const container = document.getElementById('paddle-checkout-container');
        if (!container) {
            console.error('❌ Контейнер #paddle-checkout-container не найден');
            return null;
        }

        return {
            transactionId: container.dataset.transactionId,
            clientToken: container.dataset.clientToken,
            environment: container.dataset.paddleEnv,
            successUrl: container.dataset.successUrl,
            cancelUrl: container.dataset.cancelUrl,
            customerEmail: container.dataset.customerEmail,
            hasToken: container.dataset.hasToken === 'true'
        };
    }

    /**
     * Обновляет статус на странице
     * @param {string} html - HTML содержимое для отображения
     */
    function updateStatus(html) {
        const statusEl = document.getElementById('status');
        if (statusEl) {
            statusEl.innerHTML = html;
        }
    }

    /**
     * Обработчик событий Paddle Checkout
     * @param {Object} event - Событие от Paddle
     * @param {Object} config - Конфигурация с URLs
     */
    function handlePaddleEvent(event, config) {
        console.log('📬 Paddle событие:', event);

        switch(event.name) {
            case 'checkout.loaded':
                console.log('✅ Форма оплаты загружена');
                updateStatus('<div class="status">✅ Форма оплаты загружена</div>');
                break;

            case 'checkout.completed':
                console.log('✅ Оплата завершена успешно!');
                updateStatus('<div class="status">✅ Оплата прошла успешно!<br>Перенаправление...</div>');
                setTimeout(function() {
                    window.location.href = config.successUrl;
                }, 1500);
                break;

            case 'checkout.closed':
                console.log('ℹ️ Форма оплаты закрыта');
                updateStatus('<p>Форма оплаты закрыта</p>');
                setTimeout(function() {
                    window.location.href = config.cancelUrl;
                }, 2000);
                break;

            case 'checkout.error':
                console.error('❌ Ошибка checkout:', event);
                const errorDetail = event.detail || 'Неизвестная ошибка';
                updateStatus(
                    '<div class="error">❌ Ошибка: ' + errorDetail +
                    '<br><a href="' + config.cancelUrl + '" style="color: #667eea; font-weight: 600;">Вернуться</a></div>'
                );
                break;
        }
    }

    /**
     * Открывает Paddle Checkout overlay
     * @param {Object} config - Конфигурация Paddle
     */
    function openCheckout(config) {
        try {
            console.log('🎯 Открываем Paddle Checkout...');

            Paddle.Checkout.open({
                transactionId: config.transactionId
            });

            console.log('✅ Paddle.Checkout.open() вызван');

        } catch (error) {
            console.error('❌ Ошибка открытия checkout:', error);
            updateStatus(
                '<div class="error">❌ Не удалось открыть форму оплаты: ' + error.message +
                '<br><br>Причины:<br>' +
                '- Transaction может быть в неправильном статусе<br>' +
                '- Client token может быть невалидным<br>' +
                '- Проблема с подключением к Paddle<br><br>' +
                '<a href="' + config.cancelUrl + '" style="color: #667eea; font-weight: 600;">Попробовать снова</a></div>'
            );
        }
    }

    /**
     * Инициализирует Paddle SDK и открывает checkout
     */
    function initializePaddle() {
        // Проверяем что Paddle SDK загружен
        if (typeof Paddle === 'undefined') {
            console.log('⏳ Ожидание загрузки Paddle SDK...');
            setTimeout(initializePaddle, 200);
            return;
        }

        console.log('✅ Paddle SDK загружен');

        // Получаем конфигурацию
        const config = getPaddleConfig();
        if (!config) {
            return;
        }

        // Логируем конфигурацию (без токена для безопасности)
        console.log('🚀 Paddle Billing Checkout');
        console.log('📝 Transaction ID:', config.transactionId);
        console.log('🔑 Client Token:', config.hasToken ? 'Получен' : 'Отсутствует');
        console.log('🌍 Environment:', config.environment);
        console.log('👤 Customer Email:', config.customerEmail);

        // Проверяем наличие client token
        if (!config.hasToken || !config.clientToken) {
            console.error('❌ Client Token missing!');
            updateStatus(
                '<div class="error">❌ Ошибка: Client Token не получен от сервера.<br>' +
                'Paddle Billing требует client token для инициализации.<br><br>' +
                '<a href="' + config.cancelUrl + '" style="color: #667eea; font-weight: 600;">Попробовать снова</a></div>'
            );
            return;
        }

        try {
            // Шаг 1: Устанавливаем sandbox окружение (только для sandbox)
            if (config.environment === 'sandbox') {
                Paddle.Environment.set('sandbox');
                console.log('✅ Paddle Environment установлен: sandbox');
            }

            // Шаг 2: Инициализируем Paddle с client token
            Paddle.Initialize({
                token: config.clientToken,
                pwCustomer: config.customerEmail,
                eventCallback: function(event) {
                    handlePaddleEvent(event, config);
                }
            });

            console.log('✅ Paddle.Initialize() выполнен');

            // Шаг 3: Открываем checkout overlay через 1 секунду
            setTimeout(function() {
                openCheckout(config);
            }, 1000);

        } catch (error) {
            console.error('❌ Ошибка инициализации Paddle:', error);
            updateStatus(
                '<div class="error">❌ Ошибка инициализации Paddle: ' + error.message +
                '<br><br><a href="' + config.cancelUrl + '" style="color: #667eea; font-weight: 600;">Попробовать снова</a></div>'
            );
        }
    }

    // Запускаем инициализацию при загрузке DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializePaddle);
    } else {
        initializePaddle();
    }

})();
