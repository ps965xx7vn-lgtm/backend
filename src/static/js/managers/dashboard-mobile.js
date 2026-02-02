/**
 * Manager Dashboard Mobile Navigation
 * Управление боковым меню на мобильных устройствах
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Manager Mobile Menu: Initializing...');

    // Вычисляем реальную высоту хедера СРАЗУ
    const header = document.querySelector('header') || document.querySelector('.header');
    let headerHeight = 140; // Дефолт для mobile

    if (header) {
        headerHeight = header.offsetHeight;
        console.log('Header height:', headerHeight);
        document.documentElement.style.setProperty('--header-height', headerHeight + 'px');
    }

    const toggleBtn = document.querySelector('.dashboard-menu-btn') || document.querySelector('.mobile-sidebar-toggle');
    const sidebar = document.querySelector('.dashboard-sidebar');
    const overlay = document.querySelector('.sidebar-overlay');

    if (!toggleBtn || !sidebar || !overlay) {
        console.warn('Dashboard elements not found:', { toggleBtn, sidebar, overlay });
        return; // Элементы не найдены
    }

    console.log('Elements found:', {
        toggleBtn: !!toggleBtn,
        sidebar: !!sidebar,
        overlay: !!overlay
    });

    // ВАЖНО: На mobile убираем класс open при инициализации
    // Потому что на desktop sidebar всегда открыт, но нам нужно скрыть на mobile
    if (window.innerWidth < 1024) {
        sidebar.classList.remove('open');
        overlay.classList.remove('active');
        console.log('Mobile mode: Sidebar hidden by default');
    }

    // Открытие/закрытие sidebar
    function toggleSidebar() {
        console.log('Toggle sidebar called');
        const isOpen = sidebar.classList.contains('open');
        console.log('Current state - isOpen:', isOpen);

        if (isOpen) {
            sidebar.classList.remove('open');
            overlay.classList.remove('active');
            document.body.style.overflow = '';
            console.log('Sidebar closed');
        } else {
            sidebar.classList.add('open');
            overlay.classList.add('active');
            document.body.style.overflow = 'hidden';
            console.log('Sidebar opened');

            // Важно: добавляем небольшую задержку перед активацией overlay
            // чтобы клик на кнопке не всплыл к overlay
            setTimeout(() => {
                overlay.style.pointerEvents = 'auto';
            }, 100);
        }
    }

    // Закрытие sidebar
    function closeSidebar() {
        console.log('Close sidebar called');
        overlay.style.pointerEvents = 'none';
        sidebar.classList.remove('open');
        overlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    // Клик по кнопке toggle - используем capture phase
    toggleBtn.addEventListener('click', function(e) {
        console.log('Toggle button clicked');
        e.stopPropagation(); // Останавливаем всплытие
        e.stopImmediatePropagation(); // Останавливаем ВСЕ обработчики
        toggleSidebar();
    }, true); // true = capture phase

    // Клик по overlay
    overlay.addEventListener('click', function(e) {
        console.log('Overlay clicked');
        // Проверяем, что клик именно по overlay, а не по его дочерним элементам
        if (e.target === overlay) {
            closeSidebar();
        }
    });

    // Клик по ссылкам в sidebar - закрываем меню
    const sidebarLinks = sidebar.querySelectorAll('.dashboard-nav-link');
    sidebarLinks.forEach(link => {
        link.addEventListener('click', function() {
            console.log('Sidebar link clicked');
            closeSidebar();
        });
    });

    // ESC key для закрытия
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && sidebar.classList.contains('open')) {
            console.log('ESC pressed - closing sidebar');
            closeSidebar();
        }
    });

    // Закрываем sidebar при resize на desktop
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            if (window.innerWidth >= 1280) {
                console.log('Desktop mode - closing sidebar');
                closeSidebar();
            }
        }, 250);
    });

    console.log('Manager Mobile Menu: Initialized successfully');
});
