/**
 * Bulk Operations JavaScript
 * Современный функционал для массовых операций с работами студентов
 */

(function() {
    'use strict';

    // Состояние приложения
    const state = {
        selectedSubmissions: new Set(),
        currentAction: null,
        isProcessing: false
    };

    // DOM элементы
    const elements = {
        checkboxes: null,
        selectAllBtn: null,
        deselectAllBtn: null,
        bulkAcceptBtn: null,
        bulkRejectBtn: null,
        selectedCount: null,
        modal: null,
        modalTitle: null,
        modalContent: null,
        cancelModal: null,
        confirmAction: null,
        bulkComment: null,
        bulkRating: null,
        ratingGroup: null,
        filterForm: null,
        resetFiltersBtn: null
    };

    /**
     * Инициализация приложения
     */
    function init() {
        cacheElements();
        bindEvents();
        updateUI();
    }

    /**
     * Кэширование DOM элементов
     */
    function cacheElements() {
        elements.checkboxes = document.querySelectorAll('.submission-checkbox');
        elements.selectAllBtn = document.getElementById('selectAllBtn');
        elements.deselectAllBtn = document.getElementById('deselectAllBtn');
        elements.bulkAcceptBtn = document.getElementById('bulkAcceptBtn');
        elements.bulkRejectBtn = document.getElementById('bulkRejectBtn');
        elements.selectedCount = document.getElementById('selectedCount');
        elements.modal = document.getElementById('bulkActionModal');
        elements.modalTitle = document.getElementById('modalTitle');
        elements.cancelModal = document.getElementById('cancelModal');
        elements.confirmAction = document.getElementById('confirmAction');
        elements.bulkComment = document.getElementById('bulkComment');
        elements.filterForm = document.getElementById('bulk-filter-form');
        elements.resetFiltersBtn = document.getElementById('reset-filters');
    }

    /**
     * Привязка обработчиков событий
     */
    function bindEvents() {
        // Чекбоксы работ
        elements.checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', handleCheckboxChange);
        });

        // Кнопки выбора всех/снятия выбора
        if (elements.selectAllBtn) {
            elements.selectAllBtn.addEventListener('click', selectAll);
        }

        if (elements.deselectAllBtn) {
            elements.deselectAllBtn.addEventListener('click', deselectAll);
        }

        // Кнопки массовых действий
        if (elements.bulkAcceptBtn) {
            elements.bulkAcceptBtn.addEventListener('click', () => openModal('accept'));
        }

        if (elements.bulkRejectBtn) {
            elements.bulkRejectBtn.addEventListener('click', () => openModal('reject'));
        }

        // Модальное окно
        if (elements.cancelModal) {
            elements.cancelModal.addEventListener('click', closeModal);
        }

        if (elements.confirmAction) {
            elements.confirmAction.addEventListener('click', confirmBulkAction);
        }

        if (elements.modal) {
            elements.modal.addEventListener('click', handleModalOutsideClick);
        }

        // Фильтры
        if (elements.resetFiltersBtn) {
            elements.resetFiltersBtn.addEventListener('click', resetFilters);
        }

        // Escape для закрытия модалки
        document.addEventListener('keydown', handleEscapeKey);
    }

    /**
     * Обработка изменения чекбокса
     */
    function handleCheckboxChange(event) {
        const submissionId = event.target.value;

        if (event.target.checked) {
            state.selectedSubmissions.add(submissionId);
        } else {
            state.selectedSubmissions.delete(submissionId);
        }

        updateUI();
    }

    /**
     * Выбрать все работы
     */
    function selectAll() {
        elements.checkboxes.forEach(checkbox => {
            checkbox.checked = true;
            state.selectedSubmissions.add(checkbox.value);
        });
        updateUI();
        if (typeof window.showNotification === 'function') {
            window.showNotification('Все работы выбраны', 'success');
        }
    }

    /**
     * Снять выбор со всех работ
     */
    function deselectAll() {
        elements.checkboxes.forEach(checkbox => {
            checkbox.checked = false;
        });
        state.selectedSubmissions.clear();
        updateUI();
        if (typeof window.showNotification === 'function') {
            window.showNotification('Выбор снят', 'info');
        }
    }

    /**
     * Обновление UI
     */
    function updateUI() {
        const count = state.selectedSubmissions.size;

        // Обновляем счетчик
        if (elements.selectedCount) {
            elements.selectedCount.textContent = count;
        }

        // Активируем/деактивируем кнопки
        const hasSelection = count > 0;
        if (elements.bulkAcceptBtn) {
            elements.bulkAcceptBtn.disabled = !hasSelection || state.isProcessing;
        }
        if (elements.bulkRejectBtn) {
            elements.bulkRejectBtn.disabled = !hasSelection || state.isProcessing;
        }
    }

    /**
     * Открыть модальное окно
     */
    function openModal(action) {
        state.currentAction = action;

        if (action === 'accept') {
            elements.modalTitle.textContent = 'Принять выбранные работы';
        } else {
            elements.modalTitle.textContent = 'Отклонить выбранные работы';
        }

        elements.modal.style.display = 'flex';
        elements.bulkComment.focus();
    }

    /**
     * Закрыть модальное окно
     */
    function closeModal() {
        elements.modal.style.display = 'none';
        elements.bulkComment.value = '';
        state.currentAction = null;
    }

    /**
     * Обработка клика вне модального окна
     */
    function handleModalOutsideClick(event) {
        if (event.target === elements.modal) {
            closeModal();
        }
    }

    /**
     * Обработка клавиши Escape
     */
    function handleEscapeKey(event) {
        if (event.key === 'Escape' && elements.modal.style.display === 'flex') {
            closeModal();
        }
    }

    /**
     * Подтверждение массового действия
     */
    async function confirmBulkAction() {
        if (state.isProcessing) return;

        const submissionIds = Array.from(state.selectedSubmissions);
        const comment = elements.bulkComment.value.trim();

        if (submissionIds.length === 0) {
            if (typeof window.showNotification === 'function') {
                window.showNotification('Не выбрано ни одной работы', 'warning');
            }
            return;
        }

        // Показываем загрузку
        state.isProcessing = true;
        elements.confirmAction.disabled = true;
        elements.confirmAction.innerHTML = '<span class="loading-spinner"></span> Обработка...';

        try {
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value
                           || document.querySelector('input[name="csrfmiddlewaretoken"]')?.value
                           || getCookie('csrftoken');

            const response = await fetch('/ru/reviewers/api/bulk-action/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    submission_ids: submissionIds,
                    action: state.currentAction,
                    comment: comment
                })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                if (typeof window.showNotification === 'function') {
                    window.showNotification(data.message || 'Действие выполнено успешно', 'success');
                }
                closeModal();

                // Перезагружаем страницу через 1.5 секунды
                setTimeout(() => {
                    window.location.reload();
                }, 1500);
            } else {
                throw new Error(data.error || 'Произошла ошибка');
            }
        } catch (error) {
            if (typeof window.showNotification === 'function') {
                window.showNotification(error.message || 'Произошла ошибка при выполнении действия', 'error');
            }

            // Восстанавливаем кнопку
            state.isProcessing = false;
            elements.confirmAction.disabled = false;
            elements.confirmAction.textContent = 'Подтвердить';
        }
    }

    /**
     * Сброс фильтров
     */
    function resetFilters() {
        if (elements.filterForm) {
            const inputs = elements.filterForm.querySelectorAll('input, select');
            inputs.forEach(input => {
                if (input.type === 'checkbox' || input.type === 'radio') {
                    input.checked = false;
                } else {
                    input.value = '';
                }
            });

            // Если есть select с плейсхолдером, возвращаем к нему
            const selects = elements.filterForm.querySelectorAll('select');
            selects.forEach(select => {
                if (select.options[0]?.value === '') {
                    select.selectedIndex = 0;
                }
            });

            if (typeof window.showNotification === 'function') {
                window.showNotification('Фильтры сброшены', 'success');
            }
        }
    }

    /**
     * Показать всплывающее уведомление
     */
    function showToast(message, type = 'success') {
        // Удаляем предыдущие toast
        const existingToasts = document.querySelectorAll('.toast');
        existingToasts.forEach(toast => toast.remove());

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;

        const icon = type === 'success' ? '✓'
                   : type === 'error' ? '✗'
                   : type === 'warning' ? '⚠'
                   : 'ℹ';

        toast.innerHTML = `
            <span style="font-size: 1.25rem; font-weight: bold;">${icon}</span>
            <span>${message}</span>
        `;

        document.body.appendChild(toast);

        // Автоматическое удаление через 3 секунды
        setTimeout(() => {
            toast.style.animation = 'slideOutRight 0.3s ease-out';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    /**
     * Получить CSRF токен из cookie
     */
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Экспортируем функции для использования в других скриптах
    window.bulkOperations = {
        selectAll,
        deselectAll
    };

    // Инициализация при загрузке DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
