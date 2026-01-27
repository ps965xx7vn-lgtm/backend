/**
 * Система реакций на статьи блога
 * 
 * Функциональность:
 * - Добавление/удаление/изменение реакций
 * - Обновление счётчиков в реальном времени
 * - Визуальная индикация выбранной реакции
 * - Защита от множественных запросов
 * - Обработка ошибок и уведомления пользователю
 * 
 * Типы реакций:
 * - like: 👍 Нравится
 * - love: ❤️ Супер
 * - helpful: 💡 Полезно
 * - insightful: 🤔 Интересно
 * - amazing: 🤩 Потрясающе
 */

(function() {
    'use strict';

    // Конфигурация
    const CONFIG = {
        apiUrl: window.BLOG_CONFIG?.apiReactionUrl || '/blog/api/article-reaction/',
        csrfTokenName: 'csrftoken',
        reactionButtonsSelector: '.reaction-button',
        activeClass: 'reaction-active',
        loadingClass: 'reaction-loading',
        disabledClass: 'reaction-disabled'
    };

    // Состояние
    let isProcessing = false;
    let currentArticleSlug = null;

    /**
     * Получает CSRF токен из cookies
     * @returns {string} CSRF токен
     */
    function getCsrfToken() {
        const name = CONFIG.csrfTokenName + '=';
        const decodedCookie = decodeURIComponent(document.cookie);
        const ca = decodedCookie.split(';');
        
        for (let i = 0; i < ca.length; i++) {
            let c = ca[i].trim();
            if (c.indexOf(name) === 0) {
                return c.substring(name.length, c.length);
            }
        }
        return '';
    }

    /**
     * Показывает уведомление пользователю
     * @param {string} message - Текст сообщения
     * @param {string} type - Тип сообщения: 'success', 'error', 'info'
     */
    function showNotification(message, type = 'info') {
        // Используем Django messages если доступны
        if (typeof showDjangoMessage !== 'undefined') {
            showDjangoMessage(message, type);
            return;
        }

        // Альтернативная реализация через alert (можно заменить на кастомное уведомление)
        // Простое уведомление для демонстрации
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
            color: white;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            z-index: 10000;
            animation: slideIn 0.3s ease-out;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease-in';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    /**
     * Обновляет визуальное состояние кнопок реакций
     * @param {string|null} activeReactionType - Активная реакция или null
     */
    function updateReactionButtons(activeReactionType) {
        const buttons = document.querySelectorAll(CONFIG.reactionButtonsSelector);
        
        buttons.forEach(button => {
            const reactionType = button.dataset.reactionType;
            
            if (reactionType === activeReactionType) {
                button.classList.add(CONFIG.activeClass);
                button.setAttribute('aria-pressed', 'true');
            } else {
                button.classList.remove(CONFIG.activeClass);
                button.setAttribute('aria-pressed', 'false');
            }
        });
    }

    /**
     * Обновляет счётчики реакций
     * @param {Object} reactions - Объект с количеством реакций {type: count}
     */
    function updateReactionCounts(reactions) {
        Object.keys(reactions).forEach(reactionType => {
            const count = reactions[reactionType];
            const button = document.querySelector(`${CONFIG.reactionButtonsSelector}[data-reaction-type="${reactionType}"]`);
            
            if (button) {
                const countElement = button.querySelector('.reaction-count');
                if (countElement) {
                    countElement.textContent = count > 0 ? count : '';
                    
                    // Анимация изменения счётчика
                    if (count > 0) {
                        countElement.classList.add('count-updated');
                        setTimeout(() => countElement.classList.remove('count-updated'), 300);
                    }
                }
            }
        });
    }

    /**
     * Отключает все кнопки реакций
     * @param {boolean} disabled - Флаг отключения
     */
    function setButtonsDisabled(disabled) {
        const buttons = document.querySelectorAll(CONFIG.reactionButtonsSelector);
        
        buttons.forEach(button => {
            if (disabled) {
                button.classList.add(CONFIG.disabledClass);
                button.disabled = true;
            } else {
                button.classList.remove(CONFIG.disabledClass);
                button.disabled = false;
            }
        });
    }

    /**
     * Отправляет реакцию на сервер
     * @param {string} reactionType - Тип реакции
     * @returns {Promise<Object>} Ответ сервера
     */
    async function sendReaction(reactionType) {
        const formData = new FormData();
        formData.append('article_slug', currentArticleSlug);
        formData.append('reaction_type', reactionType);

        const response = await fetch(CONFIG.apiUrl, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCsrfToken(),
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: formData,
            credentials: 'same-origin'
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.message || `HTTP error ${response.status}`);
        }

        return response.json();
    }

    /**
     * Обрабатывает клик по кнопке реакции
     * @param {Event} event - Событие клика
     */
    async function handleReactionClick(event) {
        event.preventDefault();

        // Защита от множественных кликов
        if (isProcessing) {
            return;
        }

        const button = event.currentTarget;
        const reactionType = button.dataset.reactionType;

        if (!reactionType) {

            return;
        }

        if (!currentArticleSlug) {

            showNotification('Ошибка: не удалось определить статью', 'error');
            return;
        }

        // Устанавливаем состояние загрузки
        isProcessing = true;
        setButtonsDisabled(true);
        button.classList.add(CONFIG.loadingClass);

        try {
            const data = await sendReaction(reactionType);

            if (data.success) {
                // Обновляем UI
                updateReactionButtons(data.user_reaction);
                updateReactionCounts(data.reactions);

                // Показываем уведомление
                if (data.action === 'removed') {
                    showNotification('Реакция удалена', 'info');
                } else if (data.action === 'changed') {
                    showNotification('Реакция изменена!', 'success');
                } else {
                    showNotification(data.message || 'Спасибо за реакцию!', 'success');
                }

                // Логируем для аналитики

            } else {
                showNotification(data.message || 'Не удалось добавить реакцию', 'error');
            }

        } catch (error) {

            // Специальная обработка для 401 (не авторизован)
            if (error.message.includes('401')) {
                showNotification('Для добавления реакции необходимо войти в систему', 'error');
            } else {
                showNotification('Ошибка при добавлении реакции. Попробуйте позже.', 'error');
            }
        } finally {
            // Снимаем состояние загрузки
            isProcessing = false;
            setButtonsDisabled(false);
            button.classList.remove(CONFIG.loadingClass);
        }
    }

    /**
     * Загружает текущие реакции для статьи
     */
    async function loadReactions() {
        if (!currentArticleSlug) {
            return;
        }

        try {
            const response = await fetch(`${CONFIG.apiUrl}?article_slug=${currentArticleSlug}`, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin'
            });

            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}`);
            }

            const data = await response.json();

            if (data.success) {
                updateReactionButtons(data.user_reaction);
                updateReactionCounts(data.reactions);

            }

        } catch (error) {

        }
    }

    /**
     * Инициализация системы реакций
     */
    function init() {
        // Получаем slug статьи из data-атрибута или meta-тега
        const articleElement = document.querySelector('[data-article-slug]');
        if (articleElement) {
            currentArticleSlug = articleElement.dataset.articleSlug;
        } else {
            // Альтернатива: из meta-тега
            const metaSlug = document.querySelector('meta[name="article-slug"]');
            if (metaSlug) {
                currentArticleSlug = metaSlug.getAttribute('content');
            }
        }

        if (!currentArticleSlug) {

            return;
        }

        // Привязываем обработчики к кнопкам
        const buttons = document.querySelectorAll(CONFIG.reactionButtonsSelector);
        buttons.forEach(button => {
            button.addEventListener('click', handleReactionClick);
        });

        // Загружаем текущее состояние реакций
        loadReactions();

    }

    // Запуск при загрузке DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Экспорт для использования в других скриптах
    window.ArticleReactions = {
        init: init,
        loadReactions: loadReactions,
        setArticleSlug: (slug) => {
            currentArticleSlug = slug;
            loadReactions();
        }
    };

})();
