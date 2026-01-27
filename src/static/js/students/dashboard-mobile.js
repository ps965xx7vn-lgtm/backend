/**
 * Dashboard Mobile Navigation
 * Управление боковым меню на мобильных устройствах
 */

document.addEventListener('DOMContentLoaded', function() {

    // Вычисляем реальную высоту хедера СРАЗУ
    const header = document.querySelector('header') || document.querySelector('.header');
    let headerHeight = 140; // Дефолт для mobile

    if (header) {
        headerHeight = header.offsetHeight;

        document.documentElement.style.setProperty('--header-height', headerHeight + 'px');
    }

    const toggleBtn = document.querySelector('.dashboard-menu-btn') || document.querySelector('.mobile-sidebar-toggle');
    const sidebar = document.querySelector('.dashboard-sidebar');
    const overlay = document.querySelector('.sidebar-overlay');

    // Устанавливаем позицию кнопки сразу после определения высоты хедера
    if (toggleBtn) {
        // Кнопка теперь в header, не нужно устанавливать top
        // toggleBtn уже позиционируется через flex в header-content
    }

    if (!toggleBtn || !sidebar || !overlay) {
        console.warn('Dashboard elements not found:', { toggleBtn, sidebar, overlay });
        return; // Элементы не найдены
    }

    // Проверяем начальное состояние


    // ВАЖНО: На mobile убираем класс open при инициализации
    // Потому что на desktop sidebar всегда открыт, но нам нужно скрыть на mobile
    if (window.innerWidth < 1024) {
        sidebar.classList.remove('open');
        overlay.classList.remove('active');

    }

    // Отслеживаем изменения класса sidebar
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'attributes' && mutation.attributeName === 'class') {

            }
        });
    });

    observer.observe(sidebar, {
        attributes: true,
        attributeFilter: ['class']
    });

    // Открытие/закрытие sidebar
    function toggleSidebar() {

        const isOpen = sidebar.classList.contains('open');

        if (isOpen) {
            sidebar.classList.remove('open');
            overlay.classList.remove('active');
            document.body.style.overflow = '';
        } else {
            sidebar.classList.add('open');
            overlay.classList.add('active');
            document.body.style.overflow = 'hidden';
        }

    }

    // Закрытие sidebar
    function closeSidebar() {
        sidebar.classList.remove('open');
        overlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    // Клик по кнопке toggle

    toggleBtn.addEventListener('click', function(e) {

        toggleSidebar();
    });

    // Клик по overlay
    overlay.addEventListener('click', closeSidebar);

    // Клик по ссылкам в sidebar - закрываем меню
    const sidebarLinks = sidebar.querySelectorAll('.dashboard-nav-link');
    sidebarLinks.forEach(link => {
        link.addEventListener('click', closeSidebar);
    });

    // ESC key для закрытия
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && sidebar.classList.contains('open')) {
            closeSidebar();
        }
    });

    // Закрываем sidebar при resize на desktop
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            if (window.innerWidth >= 1280) {
                closeSidebar();
            }
        }, 250);
    });
});
