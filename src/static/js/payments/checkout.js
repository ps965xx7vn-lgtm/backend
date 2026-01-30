/**
 * Payments Checkout JavaScript
 *
 * Обработка формы оплаты курса:
 * - Динамическое обновление цены при смене валюты
 * - Валидация перед отправкой
 * - Обработка выбора метода оплаты
 * - Защита от двойной отправки формы
 *
 * @author Pyland Team
 * @date 2025
 */

(function() {
    'use strict';

    // Цены в разных валютах (передаются из шаблона через data-атрибуты)
    const prices = {
        'USD': parseFloat(document.querySelector('[data-price-usd]')?.dataset.priceUsd || 0),
        'GEL': parseFloat(document.querySelector('[data-price-gel]')?.dataset.priceGel || 0),
        'RUB': parseFloat(document.querySelector('[data-price-rub]')?.dataset.priceRub || 0)
    };

    // Элементы DOM
    const form = document.getElementById('checkoutForm');
    const currencySelect = document.getElementById('id_currency');
    const paymentMethodRadios = document.querySelectorAll('input[name="payment_method"]');
    const termsCheckbox = document.getElementById('id_terms');
    const privacyCheckbox = document.getElementById('id_privacy');
    const submitButton = form?.querySelector('button[type="submit"]');

    /**
     * Обновляет отображение цены при смене валюты
     */
    function updateDisplayedPrice() {
        if (!currencySelect) return;

        const selectedCurrency = currencySelect.value;
        const priceElements = document.querySelectorAll('.checkout-price-item');

        priceElements.forEach(element => {
            const currencyLabel = element.querySelector('.currency-label');
            if (currencyLabel && currencyLabel.textContent.includes(selectedCurrency)) {
                element.style.fontWeight = '700';
                element.style.color = '#10b981';
            } else {
                element.style.fontWeight = '400';
                element.style.color = '#4a5568';
            }
        });
    }

    /**
     * Валидация соответствия метода оплаты и валюты
     */
    function validatePaymentMethodCurrency() {
        if (!currencySelect) return true;

        const selectedCurrency = currencySelect.value;
        const selectedMethod = document.querySelector('input[name="payment_method"]:checked')?.value;

        // TBC Bank работает только с GEL
        if (selectedMethod === 'tbc_georgia' && selectedCurrency !== 'GEL') {
            showError('Для оплаты через TBC Bank доступна только валюта GEL');
            currencySelect.value = 'GEL';
            updateDisplayedPrice();
            return false;
        }

        // CloudPayments не работает с GEL
        if (selectedMethod === 'cloudpayments' && selectedCurrency === 'GEL') {
            showError('CloudPayments не поддерживает грузинский лари (GEL)');
            currencySelect.value = 'USD';
            updateDisplayedPrice();
            return false;
        }

        return true;
    }

    /**
     * Показывает сообщение об ошибке
     */
    function showError(message) {
        // Удаляем предыдущие алерты
        const existingAlert = document.querySelector('.alert-error');
        if (existingAlert) {
            existingAlert.remove();
        }

        // Создаём новый алерт
        const alert = document.createElement('div');
        alert.className = 'alert alert-error';
        alert.innerHTML = `
            <svg class="alert-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            <span>${message}</span>
        `;
        alert.style.background = '#fee2e2';
        alert.style.border = '1px solid #fca5a5';
        alert.style.color = '#991b1b';

        form.insertBefore(alert, form.firstChild);

        // Автоматически удаляем через 5 секунд
        setTimeout(() => {
            alert.remove();
        }, 5000);
    }

    /**
     * Валидация формы перед отправкой
     */
    function validateForm(event) {
        // Проверка согласий
        if (!termsCheckbox?.checked) {
            event.preventDefault();
            showError('Необходимо принять условия использования');
            termsCheckbox.focus();
            return false;
        }

        if (!privacyCheckbox?.checked) {
            event.preventDefault();
            showError('Необходимо принять политику конфиденциальности');
            privacyCheckbox.focus();
            return false;
        }

        // Проверка соответствия метода и валюты
        if (!validatePaymentMethodCurrency()) {
            event.preventDefault();
            return false;
        }

        // Защита от двойной отправки
        if (submitButton) {
            submitButton.disabled = true;
            submitButton.innerHTML = `
                <svg class="btn-icon spinner" viewBox="0 0 50 50">
                    <circle class="path" cx="25" cy="25" r="20" fill="none" stroke-width="5"></circle>
                </svg>
                Обработка...
            `;
        }

        return true;
    }

    /**
     * Обработчик смены валюты
     */
    function handleCurrencyChange() {
        updateDisplayedPrice();
        validatePaymentMethodCurrency();
    }

    /**
     * Обработчик смены метода оплаты
     */
    function handlePaymentMethodChange() {
        validatePaymentMethodCurrency();

        // Анимация выбора
        paymentMethodRadios.forEach(radio => {
            const label = radio.nextElementSibling;
            if (radio.checked) {
                label.style.transform = 'scale(1.02)';
                setTimeout(() => {
                    label.style.transform = 'scale(1)';
                }, 200);
            }
        });
    }

    /**
     * Инициализация
     */
    function init() {
        if (!form) return;

        // Обновляем отображение цены при загрузке
        updateDisplayedPrice();

        // Слушатели событий
        if (currencySelect) {
            currencySelect.addEventListener('change', handleCurrencyChange);
        }

        paymentMethodRadios.forEach(radio => {
            radio.addEventListener('change', handlePaymentMethodChange);
        });

        form.addEventListener('submit', validateForm);

        // Сохранение выбора в localStorage для удобства
        if (currencySelect) {
            const savedCurrency = localStorage.getItem('preferred_currency');
            if (savedCurrency && prices[savedCurrency]) {
                currencySelect.value = savedCurrency;
                updateDisplayedPrice();
            }

            currencySelect.addEventListener('change', function() {
                localStorage.setItem('preferred_currency', this.value);
            });
        }

        // Подсветка активного метода оплаты
        const selectedMethod = document.querySelector('input[name="payment_method"]:checked');
        if (selectedMethod) {
            handlePaymentMethodChange();
        }

        console.log('✅ Checkout form initialized');
    }

    // Запускаем после загрузки DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
