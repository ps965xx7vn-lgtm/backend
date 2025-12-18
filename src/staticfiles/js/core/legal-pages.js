/**
 * Legal Pages Interactive Features
 * Интерактивные функции для юридических страниц
 * 
 * Функции:
 * - Подсветка активного раздела в оглавлении
 * - Кнопка "Наверх"
 * - Плавная прокрутка по якорям
 */

(function() {
    'use strict';

    // ===== Плавная прокрутка по якорям =====
    function initSmoothScroll() {
        const tocLinks = document.querySelectorAll('.legal-toc-link');
        
        tocLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                const href = this.getAttribute('href');
                
                if (href && href.startsWith('#')) {
                    e.preventDefault();
                    const targetId = href.slice(1);
                    const targetElement = document.getElementById(targetId);
                    
                    if (targetElement) {
                        targetElement.scrollIntoView({
                            behavior: 'smooth',
                            block: 'start'
                        });
                        
                        // Обновляем URL без перезагрузки
                        history.pushState(null, '', href);
                    }
                }
            });
        });
    }

    // ===== Подсветка активного раздела в оглавлении =====
    function initActiveSection() {
        const sections = document.querySelectorAll('.legal-section');
        const tocLinks = document.querySelectorAll('.legal-toc-link');
        
        if (sections.length === 0 || tocLinks.length === 0) return;

        const observerOptions = {
            root: null,
            rootMargin: '-100px 0px -60% 0px',
            threshold: 0
        };

        const observerCallback = (entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const sectionId = entry.target.getAttribute('id');
                    
                    // Убираем active у всех ссылок
                    tocLinks.forEach(link => {
                        link.classList.remove('active');
                    });
                    
                    // Добавляем active к текущей секции
                    const activeLink = document.querySelector(`.legal-toc-link[href="#${sectionId}"]`);
                    if (activeLink) {
                        activeLink.classList.add('active');
                    }
                }
            });
        };

        const observer = new IntersectionObserver(observerCallback, observerOptions);
        
        sections.forEach(section => {
            if (section.getAttribute('id')) {
                observer.observe(section);
            }
        });
    }

    // ===== Кнопка "Наверх" =====
    function initBackToTop() {
        const backToTopButton = document.querySelector('.legal-back-to-top');
        
        if (!backToTopButton) return;

        // Показываем/скрываем кнопку при прокрутке
        function toggleBackToTop() {
            if (window.scrollY > 400) {
                backToTopButton.classList.add('visible');
            } else {
                backToTopButton.classList.remove('visible');
            }
        }

        // Обработчик прокрутки с throttle
        let scrollTimeout;
        window.addEventListener('scroll', function() {
            if (scrollTimeout) {
                window.cancelAnimationFrame(scrollTimeout);
            }
            
            scrollTimeout = window.requestAnimationFrame(function() {
                toggleBackToTop();
            });
        });

        // Прокрутка наверх по клику
        backToTopButton.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });

        // Проверяем позицию при загрузке
        toggleBackToTop();
    }

    // ===== Автоматическое создание якорей для секций =====
    function initAutoAnchors() {
        const sections = document.querySelectorAll('.legal-section');
        
        sections.forEach((section, index) => {
            // Если у секции нет ID, создаем его
            if (!section.getAttribute('id')) {
                const title = section.querySelector('.legal-section-title');
                if (title) {
                    // Создаем ID из заголовка
                    const text = title.textContent.trim();
                    const id = 'section-' + text.toLowerCase()
                        .replace(/[^\w\s-]/g, '')
                        .replace(/\s+/g, '-')
                        .replace(/-+/g, '-')
                        .substring(0, 50);
                    
                    section.setAttribute('id', id || `section-${index + 1}`);
                }
            }
        });
    }

    // ===== Копирование ссылки на раздел =====
    function initCopyLink() {
        const sectionTitles = document.querySelectorAll('.legal-section-title');
        
        sectionTitles.forEach(title => {
            const section = title.closest('.legal-section');
            const sectionId = section?.getAttribute('id');
            
            if (!sectionId) return;

            // Добавляем иконку ссылки при наведении
            title.style.cursor = 'pointer';
            title.setAttribute('title', 'Нажмите чтобы скопировать ссылку');
            
            title.addEventListener('click', async function() {
                const url = `${window.location.origin}${window.location.pathname}#${sectionId}`;
                
                try {
                    await navigator.clipboard.writeText(url);
                    
                    // Показываем уведомление
                    showNotification('Ссылка скопирована!');
                } catch (err) {

                }
            });
        });
    }

    // ===== Показ уведомления =====
    function showNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'legal-notification';
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--legal-accent);
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            box-shadow: var(--legal-shadow);
            z-index: 1000;
            animation: slideInRight 0.3s ease-out;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease-out';
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 2000);
    }

    // ===== Прокрутка к якорю при загрузке страницы =====
    function scrollToHashOnLoad() {
        if (window.location.hash) {
            const targetId = window.location.hash.slice(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                setTimeout(() => {
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }, 100);
            }
        }
    }

    // ===== Инициализация всех функций =====
    function init() {
        // Проверяем что мы на странице с legal-page
        if (!document.querySelector('.legal-page')) return;

        initAutoAnchors();
        initSmoothScroll();
        initActiveSection();
        initBackToTop();
        initCopyLink();
        scrollToHashOnLoad();
    }

    // Запускаем после полной загрузки DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // ===== Добавляем CSS для анимаций уведомлений =====
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInRight {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOutRight {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);

})();
