# Core JavaScript Files

JavaScript файлы для базовой функциональности приложения, используемые на всех страницах.

## 📁 Файлы и их назначение

### `main.js` (основной файл)

Базовая функциональность, работающая на всех страницах.

**Функциональность:**

- Переключение темы (light/dark mode)
- Сохранение темы в localStorage
- Автоопределение системной темы
- Обработка CSRF токенов для AJAX
- Инициализация tooltips
- Smooth scroll для якорей
- Обработка flash messages
- Lazy loading изображений

**Используется в:**

- `base.html` - подключается на всех страницах

**Ключевые функции:**

```javascript
// Тема
toggleTheme()                        // Переключить тему
initTheme()                          // Инициализировать тему
saveTheme(theme)                     // Сохранить в localStorage
getSystemTheme()                     // Получить системную тему

// CSRF
getCsrfToken()                       // Получить CSRF token для AJAX

// UI
initTooltips()                       // Инициализация tooltips
smoothScroll()                       // Плавная прокрутка к якорям
handleFlashMessages()                // Автоскрытие flash сообщений

// Изображения
initLazyLoading()                    // Lazy loading для img[data-src]
```text
**Переключение темы:**

```javascript
document.addEventListener('DOMContentLoaded', function() {
    // Получить сохраненную тему
    const savedTheme = localStorage.getItem('theme');

    // Или системную тему
    const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches
        ? 'dark'
        : 'light';

    // Применить тему
    const theme = savedTheme || systemTheme;
    document.body.dataset.theme = theme;

    // Переключатель темы
    document.querySelector('.theme-toggle')?.addEventListener('click', () => {
        const currentTheme = document.body.dataset.theme || 'light';
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';

        document.body.dataset.theme = newTheme;
        localStorage.setItem('theme', newTheme);
    });
});
```text
**CSRF токен:**

```javascript
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
}

// Использование в AJAX
fetch('/api/endpoint/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken()
    },
    body: JSON.stringify(data)
});
```text
---

### `desktop-nav.js` (desktop навигация)

Интерактивность desktop навигации.

**Функциональность:**

- Открытие/закрытие dropdown меню
- Закрытие меню при клике вне его
- Highlight активного пункта меню
- Показ/скрытие user меню
- Sticky header при скролле

**Используется в:**

- `base.html` - подключается на всех страницах
- Работает только на desktop (≥992px)

**События:**

- Click на `.dropdown-toggle` - показать/скрыть dropdown
- Click вне dropdown - закрыть dropdown
- Scroll - добавить класс `.sticky` к header
- Hover на `.nav-item` - подсветка

**Ключевые функции:**

```javascript
initDropdowns()                      // Инициализация dropdown меню
toggleUserMenu()                     // Toggle user menu
highlightActiveLink()                // Подсветка активного пункта
handleStickyHeader()                 // Sticky header при скролле
closeDropdownsOnClickOutside()       // Закрытие при клике вне
```text
**Dropdown меню:**

```javascript
document.querySelectorAll('.dropdown-toggle').forEach(toggle => {
    toggle.addEventListener('click', function(e) {
        e.preventDefault();
        const dropdown = this.nextElementSibling;

        // Закрыть другие
        document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
            if (menu !== dropdown) {
                menu.classList.remove('show');
            }
        });

        // Toggle текущий
        dropdown.classList.toggle('show');
    });
});

// Закрытие при клике вне
document.addEventListener('click', function(e) {
    if (!e.target.closest('.dropdown')) {
        document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
            menu.classList.remove('show');
        });
    }
});
```text
**Sticky header:**

```javascript
window.addEventListener('scroll', function() {
    const header = document.querySelector('.header');
    if (window.scrollY > 100) {
        header.classList.add('sticky');
    } else {
        header.classList.remove('sticky');
    }
});
```text
---

### `mobile-menu.js` (мобильное меню)

Логика бургер-меню для мобильных устройств.

**Функциональность:**

- Открытие/закрытие бургер-меню
- Анимация иконки бургера (X)
- Блокировка скролла при открытом меню
- Закрытие по клику на overlay
- Закрытие по ESC
- Accordion подменю

**Используется в:**

- `base.html` - подключается на всех страницах
- Работает только на mobile (<992px)

**События:**

- Click на `.mobile-menu-toggle` - открыть/закрыть меню
- Click на `.mobile-menu-overlay` - закрыть меню
- Keydown ESC - закрыть меню
- Click на `.submenu-toggle` - открыть/закрыть подменю

**Зависимости:**

- CSS: `css/core/mobile-menu.css`
- Классы: `.mobile-menu`, `.mobile-menu.open`, `.mobile-menu-overlay`

**Ключевые функции:**

```javascript
openMobileMenu()                     // Открыть меню
closeMobileMenu()                    // Закрыть меню
toggleMobileMenu()                   // Toggle меню
lockScroll()                         // Заблокировать скролл body
unlockScroll()                       // Разблокировать скролл
initSubmenuAccordion()               // Инициализация accordion
```text
**Открытие/закрытие:**

```javascript
const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
const mobileMenu = document.querySelector('.mobile-menu');
const mobileMenuOverlay = document.querySelector('.mobile-menu-overlay');

function openMobileMenu() {
    mobileMenu.classList.add('open');
    mobileMenuOverlay.classList.add('show');
    document.body.style.overflow = 'hidden'; // Заблокировать скролл
}

function closeMobileMenu() {
    mobileMenu.classList.remove('open');
    mobileMenuOverlay.classList.remove('show');
    document.body.style.overflow = ''; // Разблокировать скролл
}

// Toggle
mobileMenuToggle.addEventListener('click', function() {
    if (mobileMenu.classList.contains('open')) {
        closeMobileMenu();
    } else {
        openMobileMenu();
    }
});

// Закрытие по overlay
mobileMenuOverlay.addEventListener('click', closeMobileMenu);

// Закрытие по ESC
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && mobileMenu.classList.contains('open')) {
        closeMobileMenu();
    }
});
```text
**Accordion подменю:**

```javascript
document.querySelectorAll('.submenu-toggle').forEach(toggle => {
    toggle.addEventListener('click', function(e) {
        e.preventDefault();
        const submenu = this.nextElementSibling;
        const isOpen = submenu.classList.contains('open');

        // Закрыть все подменю
        document.querySelectorAll('.submenu.open').forEach(menu => {
            menu.classList.remove('open');
        });

        // Toggle текущее
        if (!isOpen) {
            submenu.classList.add('open');
        }
    });
});
```text
---

## 🏗️ Архитектура

### Структура файлов

```text
static/js/core/
├── main.js              # Базовая функциональность (тема, CSRF, etc)
├── desktop-nav.js       # Desktop навигация (≥992px)
└── mobile-menu.js       # Mobile меню (<992px)
```text
### Порядок подключения в base.html

```django
<!-- В конце body, перед закрывающим тегом -->
<script src="{% static 'js/core/main.js' %}" defer></script>
<script src="{% static 'js/core/desktop-nav.js' %}" defer></script>
<script src="{% static 'js/core/mobile-menu.js' %}" defer></script>

{% block extra_js %}{% endblock %}
```text
### Независимость файлов

Файлы **независимы** друг от друга:

- Не импортируют функции друг друга
- Каждый инициализируется при `DOMContentLoaded`
- Работают с разными DOM элементами
- Могут работать параллельно

### Общие зависимости

- Django CSRF token
- Fetch API
- DOM API
- localStorage API
- Intersection Observer (для lazy loading)

---

## 📄 Использование в шаблонах

### base.html (базовый шаблон)

```django
{% load static %}
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}PySchool{% endblock %}</title>

    <!-- CSS -->
    <link rel="stylesheet" href="{% static 'css/core/main.css' %}">
    <link rel="stylesheet" href="{% static 'css/core/components.css' %}">
    <link rel="stylesheet" href="{% static 'css/core/layout.css' %}">
    <link rel="stylesheet" href="{% static 'css/core/animations.css' %}">
    <link rel="stylesheet" href="{% static 'css/core/themes.css' %}">
    <link rel="stylesheet" href="{% static 'css/core/desktop-nav.css' %}">
    <link rel="stylesheet" href="{% static 'css/core/mobile-menu.css' %}">

    {% block extra_css %}{% endblock %}
</head>
<body>
    <div class="main-wrapper">
        <!-- Header с навигацией -->
        {% include 'shared/_header.html' %}

        <!-- Основной контент -->
        <main class="content-wrapper">
            {% if messages %}
            <div class="flash-messages">
                {% for message in messages %}
                <div class="alert alert-{{ message.tags }}" role="alert">
                    {{ message }}
                </div>
                {% endfor %}
            </div>
            {% endif %}

            {% block content %}{% endblock %}
        </main>

        <!-- Footer -->
        {% include 'shared/_footer.html' %}
    </div>

    <!-- Core JavaScript -->
    <script src="{% static 'js/core/main.js' %}" defer></script>
    <script src="{% static 'js/core/desktop-nav.js' %}" defer></script>
    <script src="{% static 'js/core/mobile-menu.js' %}" defer></script>

    <!-- Page specific JS -->
    {% block extra_js %}{% endblock %}
</body>
</html>
```text
### shared/_header.html (навигация)

```django
{% load static %}
<header class="header">
    <div class="container">
        <div class="header-content">
            <!-- Logo -->
            <a href="{% url 'core:home' %}" class="logo">
                <img src="{% static 'img/logo.svg' %}" alt="PySchool">
            </a>

            <!-- Desktop Navigation -->
            <nav class="desktop-nav">
                <ul class="nav-menu">
                    <li class="nav-item">
                        <a href="{% url 'courses:list' %}" class="nav-link">Курсы</a>
                    </li>
                    <li class="nav-item">
                        <a href="{% url 'blog:home' %}" class="nav-link">Блог</a>
                    </li>
                    <li class="nav-item dropdown">
                        <a href="#" class="nav-link dropdown-toggle">Еще</a>
                        <ul class="dropdown-menu">
                            <li><a href="{% url 'core:about' %}">О нас</a></li>
                            <li><a href="{% url 'core:contacts' %}">Контакты</a></li>
                        </ul>
                    </li>

                    {% if user.is_authenticated %}
                    <li class="nav-item dropdown">
                        <a href="#" class="nav-link dropdown-toggle">
                            {{ user.username }}
                        </a>
                        <ul class="dropdown-menu user-menu">
                            <li><a href="{% url 'account:dashboard' %}">Профиль</a></li>
                            <li><a href="{% url 'account:settings' %}">Настройки</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a href="{% url 'account:logout' %}">Выйти</a></li>
                        </ul>
                    </li>
                    {% else %}
                    <li class="nav-item">
                        <a href="{% url 'account:login' %}" class="btn btn-primary">Вход</a>
                    </li>
                    {% endif %}
                </ul>

                <!-- Theme Toggle -->
                <button class="theme-toggle" aria-label="Toggle theme">
                    <span class="theme-icon">🌙</span>
                </button>
            </nav>

            <!-- Mobile Menu Toggle -->
            <button class="mobile-menu-toggle" aria-label="Open menu">
                <span></span>
                <span></span>
                <span></span>
            </button>
        </div>
    </div>
</header>

<!-- Mobile Menu -->
<div class="mobile-menu">
    <div class="mobile-menu-content">
        <ul class="mobile-nav-menu">
            <li><a href="{% url 'courses:list' %}">Курсы</a></li>
            <li><a href="{% url 'blog:home' %}">Блог</a></li>
            <li>
                <a href="#" class="submenu-toggle">Еще ▼</a>
                <ul class="submenu">
                    <li><a href="{% url 'core:about' %}">О нас</a></li>
                    <li><a href="{% url 'core:contacts' %}">Контакты</a></li>
                </ul>
            </li>

            {% if user.is_authenticated %}
            <li>
                <a href="#" class="submenu-toggle">{{ user.username }} ▼</a>
                <ul class="submenu">
                    <li><a href="{% url 'account:dashboard' %}">Профиль</a></li>
                    <li><a href="{% url 'account:settings' %}">Настройки</a></li>
                    <li><a href="{% url 'account:logout' %}">Выйти</a></li>
                </ul>
            </li>
            {% else %}
            <li><a href="{% url 'account:login' %}" class="btn btn-primary">Вход</a></li>
            {% endif %}
        </ul>

        <!-- Theme Toggle в мобильном меню -->
        <button class="theme-toggle mobile" aria-label="Toggle theme">
            🌙 Темная тема
        </button>
    </div>
</div>
<div class="mobile-menu-overlay"></div>
```text
---

## 🔌 API и взаимодействие

### CSRF Token

Все POST/PUT/DELETE запросы должны включать CSRF токен:

```javascript
// main.js предоставляет функцию
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
}

// Использование в других файлах
fetch('/api/endpoint/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken() // Из main.js
    },
    body: JSON.stringify(data)
});
```text
### localStorage API

Используется для сохранения настроек:

```javascript
// Сохранить тему
localStorage.setItem('theme', 'dark');

// Получить тему
const theme = localStorage.getItem('theme');

// Удалить
localStorage.removeItem('theme');

// Очистить всё
localStorage.clear();
```text
### Взаимодействие с Django

```javascript
// Flash messages автоматически скрываются через 5 секунд
// main.js
document.querySelectorAll('.flash-messages .alert').forEach(alert => {
    setTimeout(() => {
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 300);
    }, 5000);
});
```text
---

## 💻 Конвенции кода

### Именование функций

```javascript
// Глаголы для действий
function openMenu() { }
function closeMenu() { }
function toggleMenu() { }

// init для инициализации
function initTheme() { }
function initDropdowns() { }

// handle для обработчиков
function handleScroll() { }
function handleClick() { }

// get для получения данных
function getTheme() { }
function getCsrfToken() { }
```text
### DOMContentLoaded

Весь код инициализации:

```javascript
document.addEventListener('DOMContentLoaded', function() {
    // Инициализация
    initTheme();
    initDropdowns();
    initLazyLoading();

    // Event listeners
    setupEventListeners();
});
```text
### Event Listeners

```javascript
// Используем делегирование где возможно
document.addEventListener('click', function(e) {
    if (e.target.matches('.dropdown-toggle')) {
        // Обработка
    }
});

// Или прямые listeners
document.querySelector('.btn').addEventListener('click', function() {
    // Обработка
});
```text
### Обработка ошибок

```javascript
try {
    const theme = localStorage.getItem('theme');
    document.body.dataset.theme = theme;
} catch (error) {
    console.error('Error loading theme:', error);
    // Fallback
    document.body.dataset.theme = 'light';
}
```text
---

## 📊 Статистика

- **Всего JS файлов**: 3
- **Базовый**: `main.js` (тема, CSRF, tooltips, lazy loading)
- **Навигация**: `desktop-nav.js`, `mobile-menu.js`
- **Общий объем**: ~800 строк кода
- **Event listeners**: ~15
- **Функций**: ~20

---

## 🔗 Связанные документы

- **Стили**: `static/css/core/README.md` - документация CSS файлов
- **Шаблоны**: `core/templates/` - HTML шаблоны core
- **Блог JS**: `static/js/blog/README.md` - JavaScript блога
- **Base template**: `core/templates/base.html` - базовый шаблон

---

## 🚀 Быстрый старт

### Добавление нового функционала

**Если нужен новый общий функционал:**

1. Добавьте функцию в `main.js`:

```javascript
// main.js
function myNewFeature() {
    // Код
}

document.addEventListener('DOMContentLoaded', function() {
    myNewFeature();
});
```text
2. Или создайте новый файл `my-feature.js` и подключите в `base.html`:

```django
<script src="{% static 'js/core/my-feature.js' %}" defer></script>
```text
### Использование темы в своем коде

```javascript
// Получить текущую тему
const currentTheme = document.body.dataset.theme || 'light';

// Подписаться на изменения темы
const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
        if (mutation.attributeName === 'data-theme') {
            const newTheme = document.body.dataset.theme;
            console.log('Theme changed to:', newTheme);
        }
    });
});

observer.observe(document.body, {
    attributes: true,
    attributeFilter: ['data-theme']
});
```text
### Добавление tooltip

```html
<!-- HTML -->
<button data-tooltip="Это подсказка">Наведи на меня</button>
```text
```javascript
// main.js автоматически инициализирует все [data-tooltip]
// Или вручную:
const tooltip = document.querySelector('[data-tooltip]');
tooltip.addEventListener('mouseenter', function() {
    showTooltip(this.dataset.tooltip);
});
```text
Готово! 🎉
