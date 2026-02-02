/**
 * Manager Dashboard JavaScript
 * Современные интерактивные функции для административной панели
 */

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    initMobileMenu();
    initThemeToggle();
    initTooltips();
    initTableInteractions();
    initAutoRefresh();
    initViewToggle();  // Добавлен переключатель вида (сетка/список)
});

/**
 * Мобильное меню
 */
function initMobileMenu() {
    const toggle = document.querySelector('.dashboard-menu-btn');
    const sidebar = document.querySelector('.dashboard-sidebar');
    const overlay = document.querySelector('.sidebar-overlay');
    
    console.log('Manager Dashboard: Initializing mobile menu');
    console.log('Toggle button:', toggle);
    console.log('Sidebar:', sidebar);
    console.log('Overlay:', overlay);
    
    if (toggle && sidebar && overlay) {
        console.log('All elements found, adding event listeners');
        
        toggle.addEventListener('click', function(e) {
            console.log('Toggle button clicked');
            sidebar.classList.toggle('open');
            overlay.classList.toggle('active');
            console.log('Sidebar classes:', sidebar.className);
            console.log('Overlay classes:', overlay.className);
        });
        
        overlay.addEventListener('click', function() {
            console.log('Overlay clicked');
            sidebar.classList.remove('open');
            overlay.classList.remove('active');
        });
        
        // Закрытие по нажатию Escape
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && sidebar.classList.contains('open')) {
                console.log('Escape pressed, closing sidebar');
                sidebar.classList.remove('open');
                overlay.classList.remove('active');
            }
        });
    } else {
        console.error('Manager Dashboard: Missing elements!', {
            toggle: !!toggle,
            sidebar: !!sidebar,
            overlay: !!overlay
        });
    }
}

/**
 * Переключение темы
 */
function initThemeToggle() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    
    // Создание кнопки переключения темы если её нет
    const headerRight = document.querySelector('.manager-header-right');
    if (headerRight && !document.querySelector('.theme-toggle-btn')) {
        const themeBtn = document.createElement('button');
        themeBtn.className = 'theme-toggle-btn';
        themeBtn.innerHTML = savedTheme === 'dark' ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
        themeBtn.title = 'Переключить тему';
        headerRight.insertBefore(themeBtn, headerRight.firstChild);
        
        themeBtn.addEventListener('click', function() {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            
            this.innerHTML = newTheme === 'dark' ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
            
            // Анимация переключения
            document.body.style.transition = 'background-color 0.3s ease';
            setTimeout(() => {
                document.body.style.transition = '';
            }, 300);
        });
    }
}

/**
 * Инициализация всплывающих подсказок
 */
function initTooltips() {
    const elements = document.querySelectorAll('[data-tooltip]');
    elements.forEach(el => {
        el.addEventListener('mouseenter', showTooltip);
        el.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(e) {
    const text = e.target.getAttribute('data-tooltip');
    if (!text) return;
    
    const tooltip = document.createElement('div');
    tooltip.className = 'custom-tooltip';
    tooltip.textContent = text;
    document.body.appendChild(tooltip);
    
    const rect = e.target.getBoundingClientRect();
    tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
    tooltip.style.top = rect.top - tooltip.offsetHeight - 8 + 'px';
    
    setTimeout(() => tooltip.classList.add('show'), 10);
}

function hideTooltip() {
    const tooltip = document.querySelector('.custom-tooltip');
    if (tooltip) {
        tooltip.classList.remove('show');
        setTimeout(() => tooltip.remove(), 200);
    }
}

/**
 * Интерактивные таблицы
 */
function initTableInteractions() {
    // Сортировка таблиц
    const sortableHeaders = document.querySelectorAll('[data-sortable]');
    sortableHeaders.forEach(header => {
        header.style.cursor = 'pointer';
        header.addEventListener('click', function() {
            sortTable(this);
        });
    });
    
    // Выбор строк
    const checkboxes = document.querySelectorAll('.row-checkbox');
    const selectAll = document.querySelector('#select-all');
    
    if (selectAll) {
        selectAll.addEventListener('change', function() {
            checkboxes.forEach(cb => cb.checked = this.checked);
            updateBulkActions();
        });
    }
    
    checkboxes.forEach(cb => {
        cb.addEventListener('change', updateBulkActions);
    });
}

function sortTable(header) {
    const table = header.closest('table');
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const index = Array.from(header.parentNode.children).indexOf(header);
    const isAscending = header.classList.contains('sort-asc');
    
    // Очистка других заголовков
    table.querySelectorAll('th').forEach(th => {
        th.classList.remove('sort-asc', 'sort-desc');
    });
    
    // Сортировка строк
    rows.sort((a, b) => {
        const aText = a.cells[index].textContent.trim();
        const bText = b.cells[index].textContent.trim();
        
        // Попытка числовой сортировки
        const aNum = parseFloat(aText);
        const bNum = parseFloat(bText);
        
        if (!isNaN(aNum) && !isNaN(bNum)) {
            return isAscending ? bNum - aNum : aNum - bNum;
        }
        
        // Текстовая сортировка
        return isAscending 
            ? bText.localeCompare(aText)
            : aText.localeCompare(bText);
    });
    
    // Обновление DOM
    rows.forEach(row => tbody.appendChild(row));
    
    // Обновление иконки сортировки
    header.classList.add(isAscending ? 'sort-desc' : 'sort-asc');
}

function updateBulkActions() {
    const checked = document.querySelectorAll('.row-checkbox:checked');
    const bulkActions = document.querySelector('.bulk-actions');
    
    if (bulkActions) {
        bulkActions.style.display = checked.length > 0 ? 'flex' : 'none';
        const count = bulkActions.querySelector('.selected-count');
        if (count) count.textContent = checked.length;
    }
}

/**
 * Автообновление данных
 */
function initAutoRefresh() {
    const refreshInterval = 30000; // 30 секунд
    const refreshableElements = document.querySelectorAll('[data-auto-refresh]');
    
    if (refreshableElements.length === 0) return;
    
    setInterval(async () => {
        for (const element of refreshableElements) {
            const url = element.getAttribute('data-refresh-url');
            if (!url) continue;
            
            try {
                const response = await fetch(url);
                if (response.ok) {
                    const html = await response.text();
                    element.innerHTML = html;
                    element.classList.add('animate-fade-in');
                    setTimeout(() => element.classList.remove('animate-fade-in'), 300);
                }
            } catch (error) {

            }
        }
    }, refreshInterval);
}

/**
 * Анимация статистических карточек
 */
function animateStatCards() {
    const cards = document.querySelectorAll('.stat-card');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.classList.add('animate-fade-in');
                }, index * 100);
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });
    
    cards.forEach(card => observer.observe(card));
}

/**
 * Счетчик с анимацией для статистики
 */
function animateCounter(element, target, duration = 1000) {
    let start = 0;
    const increment = target / (duration / 16);
    
    const timer = setInterval(() => {
        start += increment;
        if (start >= target) {
            element.textContent = target;
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(start);
        }
    }, 16);
}

/**
 * Подтверждение действий
 */
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

/**
 * Уведомления
 */
function showNotification(message, type = 'info', duration = 3000) {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${getNotificationIcon(type)}"></i>
        <span>${message}</span>
        <button class="notification-close">&times;</button>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => notification.classList.add('show'), 10);
    
    notification.querySelector('.notification-close').addEventListener('click', () => {
        hideNotification(notification);
    });
    
    setTimeout(() => {
        hideNotification(notification);
    }, duration);
}

function hideNotification(notification) {
    notification.classList.remove('show');
    setTimeout(() => notification.remove(), 300);
}

function getNotificationIcon(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

/**
 * AJAX Form Submission
 */
function initAjaxForms() {
    const forms = document.querySelectorAll('[data-ajax-form]');
    
    forms.forEach(form => {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const url = this.action;
            const method = this.method;
            
            const submitBtn = this.querySelector('[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Отправка...';
            
            try {
                const response = await fetch(url, {
                    method: method,
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showNotification(data.message || 'Успешно сохранено', 'success');
                    if (data.redirect) {
                        setTimeout(() => window.location.href = data.redirect, 1000);
                    }
                } else {
                    showNotification(data.message || 'Ошибка при сохранении', 'error');
                }
            } catch (error) {
                showNotification('Ошибка сети', 'error');

            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        });
    });
}

/**
 * Поиск в реальном времени
 */
function initLiveSearch() {
    const searchInputs = document.querySelectorAll('[data-live-search]');
    
    searchInputs.forEach(input => {
        let timeout;
        input.addEventListener('input', function() {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                performSearch(this.value, this.getAttribute('data-search-target'));
            }, 300);
        });
    });
}

async function performSearch(query, target) {
    const targetElement = document.querySelector(target);
    if (!targetElement) return;
    
    const url = targetElement.getAttribute('data-search-url');
    if (!url) return;
    
    try {
        const response = await fetch(`${url}?q=${encodeURIComponent(query)}`);
        if (response.ok) {
            const html = await response.text();
            targetElement.innerHTML = html;
        }
    } catch (error) {

    }
}

/**
 * Export функций для использования в шаблонах
 */
window.managerDashboard = {
    showNotification,
    confirmAction,
    animateCounter,
    initAjaxForms,
    initLiveSearch
};

// Инициализация дополнительных функций
animateStatCards();

/**
 * Инициализация переключателя вида (сетка/список)
 * Копировано и адаптировано из reviewers/dashboard.js
 */
function initViewToggle() {
    const viewToggleBtns = document.querySelectorAll('.view-toggle-btn');
    const reviewsContainer = document.querySelector('.reviews-container');
    
    if (!viewToggleBtns.length || !reviewsContainer) return;
    
    // Загружаем сохраненный вид из localStorage
    const savedView = localStorage.getItem('managersViewMode') || 'grid';
    setView(savedView);
    
    // Обработчики кликов на кнопки
    viewToggleBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const view = this.dataset.view;
            setView(view);
            localStorage.setItem('managersViewMode', view);
        });
    });
    
    function setView(view) {
        // Обновляем data-view атрибут контейнера
        reviewsContainer.setAttribute('data-view', view);
        
        // Обновляем активные кнопки
        viewToggleBtns.forEach(btn => {
            if (btn.dataset.view === view) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
    }
}

