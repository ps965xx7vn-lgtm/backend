/**
 * Mobile Sidebar Menu - Modern Navigation
 * Handles sidebar toggle, expandable sections, theme/language switching
 */

(function() {
    'use strict';

    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initMobileSidebar);
    } else {
        initMobileSidebar();
    }

    function initMobileSidebar() {
        const sidebar = document.querySelector('[data-mobile-sidebar]');
        const toggleBtn = document.querySelector('[data-mobile-toggle]');
        const closeBtn = document.querySelector('[data-mobile-close-btn]');
        const overlay = document.querySelector('[data-mobile-close]');

        if (!sidebar || !toggleBtn) return;

        // Toggle sidebar
        toggleBtn.addEventListener('click', () => {
            sidebar.classList.add('active');
            toggleBtn.classList.add('active');
            document.body.style.overflow = 'hidden';
        });

        // Close sidebar function
        function closeSidebar() {
            sidebar.classList.remove('active');
            toggleBtn.classList.remove('active');
            document.body.style.overflow = '';
        }

        // Close on close button
        if (closeBtn) {
            closeBtn.addEventListener('click', closeSidebar);
        }

        // Close on overlay
        if (overlay) {
            overlay.addEventListener('click', closeSidebar);
        }

        // Close on ESC key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && sidebar.classList.contains('active')) {
                closeSidebar();
            }
        });

        // Expandable course menu
        const navToggles = document.querySelectorAll('[data-toggle]');
        navToggles.forEach(toggle => {
            toggle.addEventListener('click', (e) => {
                e.preventDefault();
                const targetId = toggle.getAttribute('data-toggle');
                const submenu = document.querySelector(`[data-submenu="${targetId}"]`);

                if (submenu) {
                    toggle.classList.toggle('active');
                    submenu.classList.toggle('active');
                }
            });
        });

        // Theme switcher - используем глобальный ThemeManager для корректной работы уведомлений
        const themeOptions = document.querySelectorAll('.mobile-theme-option');
        themeOptions.forEach(option => {
            option.addEventListener('click', () => {
                const theme = option.getAttribute('data-theme-icon');
                // Используем ThemeManager если доступен
                if (window.themeManager) {
                    window.themeManager.applyTheme(theme, true);
                } else {
                    // Fallback если ThemeManager еще не инициализирован
                    document.documentElement.setAttribute('data-theme', theme);
                    localStorage.setItem('theme', theme);
                }
            });
        });

        // Language switcher - интеграция с LanguageManager для реального переключения языка
        const langBtns = document.querySelectorAll('.mobile-lang-btn');
        langBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const langCode = btn.getAttribute('data-lang');

                // Визуальное обновление кнопок
                langBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');

                // Используем LanguageManager для переключения языка через Django
                if (window.languageManager) {
                    window.languageManager.changeLanguage(langCode);
                } else {
                    // Fallback: прямое переключение если LanguageManager не готов
                    localStorage.setItem('language', langCode);
                    sessionStorage.setItem('language_changed', langCode);

                    const currentPath = window.location.pathname;
                    const pathWithoutLang = currentPath.replace(/^\/[a-z]{2}\//, '/');
                    const newPath = `/${langCode}${pathWithoutLang}`;
                    window.location.href = newPath + window.location.search;
                }
            });
        });

        // Set active language on load
        // Извлекаем первые 2 символа языка (например, 'ru' из 'ru-RU' или 'en' из 'en-US')
        const currentLang = (document.documentElement.lang || 'ru').split('-')[0];
        const activeLangBtn = document.querySelector(`.mobile-lang-btn[data-lang="${currentLang}"]`);
        if (activeLangBtn) {
            activeLangBtn.classList.add('active');
        }

        // Close sidebar on internal navigation
        const navLinks = sidebar.querySelectorAll('a:not([data-toggle])');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                // Small delay to allow navigation to start
                setTimeout(closeSidebar, 100);
            });
        });

        // Handle window resize - close sidebar on desktop (≥ 1280px)
        let resizeTimer;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(() => {
                if (window.innerWidth >= 1280) {
                    closeSidebar();
                }
            }, 250);
        });

        // Prevent body scroll when sidebar is open
        sidebar.addEventListener('touchmove', (e) => {
            if (e.target === sidebar || e.target === overlay) {
                e.preventDefault();
            }
        }, { passive: false });
    }
})();
