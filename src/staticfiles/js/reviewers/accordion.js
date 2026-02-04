/**
 * Универсальный скрипт аккордеона для страниц проверки работ
 * 
 * Используется на двух страницах:
 * - submission_detail.html (классы с суффиксом -detail)
 * - submission_review.html (базовые классы без суффикса)
 * 
 * Обеспечивает плавное открытие/закрытие блоков истории улучшений
 * с анимацией max-height и поддержкой динамического изменения размера
 */
(function() {
    'use strict';

    /**
     * Переключает состояние элемента аккордеона
     * @param {HTMLElement} button - Кнопка-заголовок аккордеона
     * @param {string} itemClass - CSS селектор элемента аккордеона
     * @param {string} contentClass - CSS селектор контента аккордеона
     */
    function toggleAccordion(button, itemClass, contentClass) {
        const item = button.closest(itemClass);
        if (!item) {
            return;
        }
        
        const content = item.querySelector(contentClass);
        if (!content) {
            return;
        }
        
        const wasActive = item.classList.contains('active');
        
        // Закрываем все открытые элементы аккордеона данного типа
        document.querySelectorAll(`${itemClass}.active`).forEach(i => {
            i.classList.remove('active');
            const c = i.querySelector(contentClass);
            if (c) {
                c.style.maxHeight = '0';
            }
        });
        
        // Открываем кликнутый элемент, если он не был активен
        if (!wasActive) {
            item.classList.add('active');
            // Устанавливаем max-height равный scrollHeight для плавной анимации
            setTimeout(() => {
                content.style.maxHeight = content.scrollHeight + 'px';
            }, 10);
        }
    }
    
    /**
     * Инициализирует аккордеоны на странице после загрузки DOM
     * Поддерживает два типа аккордеонов:
     * 1. Для страницы детального просмотра (.accordion-item-detail)
     * 2. Для страницы проверки работы (.accordion-item)
     */
    function initAccordion() {
        
        // Аккордеоны для страницы submission_detail.html
        const detailItems = document.querySelectorAll('.accordion-item-detail');
        
        detailItems.forEach((item, index) => {
            const button = item.querySelector('.accordion-header-detail');
            if (button) {
                button.addEventListener('click', function(event) {
                    event.preventDefault();
                    event.stopPropagation();
                    toggleAccordion(this, '.accordion-item-detail', '.accordion-content-detail');
                });
            }
        });
        
        // Аккордеоны для страницы submission_review.html
        const reviewItems = document.querySelectorAll('.accordion-item');
        
        reviewItems.forEach((item, index) => {
            const button = item.querySelector('.accordion-header');
            if (button) {
                button.addEventListener('click', function(event) {
                    event.preventDefault();
                    event.stopPropagation();
                    toggleAccordion(this, '.accordion-item', '.accordion-content');
                });
            }
        });
    }
    
    /**
     * Автоматически пересчитывает высоту открытых аккордеонов при изменении размера окна
     * Необходимо для корректного отображения при изменении viewport
     */
    window.addEventListener('resize', function() {
        document.querySelectorAll('.accordion-item-detail.active .accordion-content-detail').forEach(content => {
            content.style.maxHeight = content.scrollHeight + 'px';
        });
        document.querySelectorAll('.accordion-item.active .accordion-content').forEach(content => {
            content.style.maxHeight = content.scrollHeight + 'px';
        });
    });
    
    // Инициализация при готовности DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initAccordion);
    } else {
        initAccordion();
    }
})();
