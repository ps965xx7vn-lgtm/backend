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
    
    console.log('Universal accordion script loaded');
    
    /**
     * Переключает состояние элемента аккордеона
     * @param {HTMLElement} button - Кнопка-заголовок аккордеона
     * @param {string} itemClass - CSS селектор элемента аккордеона
     * @param {string} contentClass - CSS селектор контента аккордеона
     */
    function toggleAccordion(button, itemClass, contentClass) {
        console.log('toggleAccordion called for', itemClass);
        const item = button.closest(itemClass);
        if (!item) {
            console.error('No item found with class', itemClass);
            return;
        }
        
        const content = item.querySelector(contentClass);
        if (!content) {
            console.error('No content found with class', contentClass);
            return;
        }
        
        const wasActive = item.classList.contains('active');
        console.log('Item:', item, 'Content:', content, 'Was active:', wasActive);
        
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
                console.log('Opened item, height:', content.scrollHeight);
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
        console.log('Initializing accordions...');
        
        // Аккордеоны для страницы submission_detail.html
        const detailItems = document.querySelectorAll('.accordion-item-detail');
        console.log('Found detail accordion items:', detailItems.length);
        
        detailItems.forEach((item, index) => {
            const button = item.querySelector('.accordion-header-detail');
            if (button) {
                button.addEventListener('click', function(event) {
                    event.preventDefault();
                    event.stopPropagation();
                    console.log('Detail button clicked for item', index);
                    toggleAccordion(this, '.accordion-item-detail', '.accordion-content-detail');
                });
                console.log(`Detail listener added to item ${index}`);
            }
        });
        
        // Аккордеоны для страницы submission_review.html
        const reviewItems = document.querySelectorAll('.accordion-item');
        console.log('Found review accordion items:', reviewItems.length);
        
        reviewItems.forEach((item, index) => {
            const button = item.querySelector('.accordion-header');
            if (button) {
                button.addEventListener('click', function(event) {
                    event.preventDefault();
                    event.stopPropagation();
                    console.log('Review button clicked for item', index);
                    toggleAccordion(this, '.accordion-item', '.accordion-content');
                });
                console.log(`Review listener added to item ${index}`);
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
