# Core CSS Files

Базовые стили для всего приложения, используемые на всех страницах через `base.html`.

## 📋 Содержание

- [Файлы и их назначение](#файлы-и-их-назначение)
- [Архитектура стилей](#архитектура-стилей)
- [Использование в шаблонах](#использование-в-шаблонах)
- [Темизация](#темизация)
- [Адаптивность](#адаптивность)

## 📁 Файлы и их назначение

### `main.css` (базовые стили)

Основные глобальные стили приложения.

**Включает:**

- CSS переменные (цвета, шрифты, отступы, тени)
- Сброс стилей (reset)
- Типографика (заголовки, параграфы, списки)
- Базовые классы для текста
- Утилитные классы (margin, padding, display)

**Используется в:**

- `base.html` - подключается на всех страницах

**Ключевые переменные:**

```css
:root {
    --primary-color: #3498db;
    --secondary-color: #2ecc71;
    --danger-color: #e74c3c;
    --warning-color: #f39c12;
    --dark-color: #2c3e50;
    --light-color: #ecf0f1;

    --font-primary: 'Inter', sans-serif;
    --font-code: 'Fira Code', monospace;

    --spacing-xs: 0.25rem;
    --spacing-sm: 0.5rem;
    --spacing-md: 1rem;
    --spacing-lg: 1.5rem;
    --spacing-xl: 2rem;

    --border-radius: 8px;
    --transition-speed: 0.3s;
}
```text
**Утилитные классы:**

```css
.container              /* Контейнер с max-width */
.text-center            /* Центрирование текста */
.text-left, .text-right /* Выравнивание текста */
.mt-1, .mt-2, .mt-3     /* Margin top */
.mb-1, .mb-2, .mb-3     /* Margin bottom */
.d-flex                 /* Display flex */
.d-none                 /* Display none */
```text
---

### `components.css` (компоненты)

Переиспользуемые UI компоненты.

**Включает:**

- `.btn` - кнопки (primary, secondary, success, danger, outline)
- `.card` - карточки контента
- `.badge` - бейджи и метки
- `.alert` - уведомления (success, info, warning, danger)
- `.modal` - модальные окна
- `.tooltip` - подсказки
- `.dropdown` - выпадающие меню
- `.tabs` - табы/вкладки
- `.progress` - прогресс-бары
- `.loader` - спиннеры загрузки

**Используется в:**

- `base.html` - подключается на всех страницах

**Примеры компонентов:**

```css
/* Кнопки */
.btn                    /* Базовая кнопка */
.btn-primary            /* Основная кнопка */
.btn-secondary          /* Вторичная кнопка */
.btn-outline-primary    /* Контурная кнопка */
.btn-sm, .btn-lg        /* Размеры кнопок */

/* Карточки */
.card                   /* Контейнер карточки */
.card-header            /* Шапка карточки */
.card-body              /* Тело карточки */
.card-footer            /* Подвал карточки */

/* Уведомления */
.alert                  /* Базовое уведомление */
.alert-success          /* Успех (зеленое) */
.alert-warning          /* Предупреждение (желтое) */
.alert-danger           /* Ошибка (красное) */
.alert-info             /* Информация (синее) */
```text
---

### `layout.css` (layout)

Структура страницы и основные layout элементы.

**Включает:**

- `.main-wrapper` - обертка всей страницы
- `.content-wrapper` - обертка контента
- `.sidebar` - боковая панель
- `.header` - шапка сайта
- `.footer` - подвал сайта
- Grid системы
- Flex utilities

**Используется в:**

- `base.html` - подключается на всех страницах

**Структура страницы:**

```html
<div class="main-wrapper">
    <header class="header">...</header>
    <main class="content-wrapper">
        <aside class="sidebar">...</aside>
        <div class="main-content">...</div>
    </main>
    <footer class="footer">...</footer>
</div>
```text
**Grid система:**

```css
.row                    /* Flex контейнер */
.col-1 ... .col-12      /* Колонки (1-12) */
.col-md-6, .col-lg-4    /* Адаптивные колонки */
.gap-1, .gap-2          /* Отступы между элементами */
```text
---

### `animations.css` (анимации)

CSS анимации и transitions.

**Включает:**

- `@keyframes` анимации (fadeIn, slideIn, bounce, spin)
- Utility классы для анимаций
- Hover эффекты
- Loading анимации
- Transitions для smooth UI

**Используется в:**

- `base.html` - подключается на всех страницах

**Анимации:**

```css
.fade-in                /* Плавное появление */
.slide-in-left          /* Въезд слева */
.slide-in-right         /* Въезд справа */
.bounce                 /* Подпрыгивание */
.pulse                  /* Пульсация */
.rotate                 /* Вращение */
.shake                  /* Тряска */

/* Hover эффекты */
.hover-scale            /* Увеличение при наведении */
.hover-shadow           /* Тень при наведении */
.hover-lift             /* Поднятие при наведении */
```text
**Использование:**

```html
<div class="fade-in">Появится плавно</div>
<button class="btn hover-scale">Увеличится при hover</button>
```text
---

### `themes.css` (темы)

Поддержка светлой и темной тем.

**Включает:**

- CSS переменные для светлой темы
- CSS переменные для темной темы
- Переключение через `[data-theme="dark"]`
- Автоопределение системной темы через `prefers-color-scheme`

**Используется в:**

- `base.html` - подключается на всех страницах

**Структура:**

```css
/* Светлая тема (по умолчанию) */
:root {
    --bg-primary: #ffffff;
    --bg-secondary: #f8f9fa;
    --text-primary: #212529;
    --text-secondary: #6c757d;
}

/* Темная тема */
[data-theme="dark"] {
    --bg-primary: #1a1a1a;
    --bg-secondary: #2d2d2d;
    --text-primary: #e0e0e0;
    --text-secondary: #9e9e9e;
}

/* Автоопределение системной темы */
@media (prefers-color-scheme: dark) {
    :root {
        --bg-primary: #1a1a1a;
        ...
    }
}
```text
**Переключение темы:**

```javascript
// В main.js
document.body.dataset.theme = 'dark'; // или 'light'
```text
---

### `desktop-nav.css` (desktop навигация)

Стили для desktop навигации в header.

**Включает:**

- `.desktop-nav` - контейнер навигации
- `.nav-menu` - список пунктов меню
- `.nav-item` - элемент меню
- `.nav-link` - ссылка меню
- `.dropdown-menu` - выпадающие подменю
- `.user-menu` - меню пользователя

**Используется в:**

- `base.html` - подключается на всех страницах
- `shared/_header.html` - компонент header

**Ключевые классы:**

```css
.desktop-nav            /* Flex навигация */
.nav-menu               /* Горизонтальный список */
.nav-item               /* Li элемент */
.nav-link               /* A элемент с hover */
.nav-link.active        /* Активная страница */
.dropdown-menu          /* Выпадающее меню */
.user-menu              /* Меню авторизованного пользователя */
```text
**Медиа-запрос:**

- Показывается на `min-width: 992px`
- Скрывается на мобильных устройствах

---

### `mobile-menu.css` (mobile навигация)

Стили для мобильного бургер-меню.

**Включает:**

- `.mobile-menu-toggle` - кнопка бургера
- `.mobile-menu` - выдвигающееся меню
- `.mobile-menu-overlay` - затемняющий оверлей
- `.mobile-menu-content` - контент меню
- Анимации открытия/закрытия

**Используется в:**

- `base.html` - подключается на всех страницах
- `shared/_header.html` - компонент header

**Зависимости:**

- `js/core/mobile-menu.js` - логика открытия/закрытия

**Ключевые классы:**

```css
.mobile-menu-toggle     /* Кнопка бургера (3 полоски) */
.mobile-menu            /* Боковое меню (справа) */
.mobile-menu.open       /* Открытое состояние */
.mobile-menu-overlay    /* Темный оверлей */
.mobile-menu-content    /* Список пунктов меню */
```text
**Медиа-запрос:**

- Показывается на `max-width: 991px`
- Скрывается на desktop

---

### `home.css` (главная страница)

Стили специфичные для главной страницы (`core/home.html`).

**Включает:**

- `.hero-section` - главный баннер
- `.features-section` - секция с преимуществами
- `.stats-section` - статистика
- `.cta-section` - Call to Action
- `.testimonials` - отзывы

**Используется в:**

- `core/home.html`

**Секции:**

```css
.hero-section           /* Первый экран с заголовком */
.hero-content           /* Текст + кнопки */
.hero-image             /* Изображение справа */

.features-section       /* Преимущества (grid) */
.feature-card           /* Карточка преимущества */
.feature-icon           /* Иконка */

.stats-section          /* Статистика (flex) */
.stat-item              /* Один показатель */
.stat-number            /* Большое число */
.stat-label             /* Подпись */

.cta-section            /* Призыв к действию */
```text
---

### `contact-form.css` (форма контактов)

Стили для страницы контактов и формы обратной связи.

**Включает:**

- `.contact-container` - контейнер страницы
- `.contact-form` - форма обратной связи
- `.form-group` - группа полей формы
- `.form-control` - input/textarea стили
- `.contact-info` - блок контактной информации

**Используется в:**

- `core/contacts.html`

**Ключевые классы:**

```css
.contact-container      /* Flex контейнер (форма + инфо) */
.contact-form           /* Форма слева */
.contact-info           /* Контакты справа */

.form-group             /* Обертка для label + input */
.form-label             /* Label поля */
.form-control           /* Input/textarea/select */
.form-control:focus     /* Фокус состояние */
.form-error             /* Сообщение об ошибке */

.submit-btn             /* Кнопка отправки */
```text
---

### `legal-pages.css` (юридические страницы)

Стили для страниц Terms of Service и Privacy Policy.

**Включает:**

- `.legal-container` - контейнер страницы
- `.legal-content` - контент с текстом
- `.legal-section` - секция документа
- `.legal-list` - списки в документе
- Типографика для длинного текста

**Используется в:**

- `core/legal/terms_of_service.html`
- `core/legal/privacy_policy.html`

**Ключевые классы:**

```css
.legal-container        /* Контейнер с max-width */
.legal-header           /* Заголовок документа */
.legal-content          /* Текстовый контент */
.legal-section          /* Секция с подзаголовком */
.legal-list             /* Маркированный список */
.last-updated           /* Дата последнего обновления */
```text
---

## 🏗️ Архитектура стилей

### Порядок подключения

Файлы подключаются в определенном порядке в `base.html`:

```django
{% load static %}
<!DOCTYPE html>
<html>
<head>
    <!-- 1. Базовые стили (переменные, reset, типографика) -->
    <link rel="stylesheet" href="{% static 'css/core/main.css' %}">

    <!-- 2. Компоненты (кнопки, карточки, модалки) -->
    <link rel="stylesheet" href="{% static 'css/core/components.css' %}">

    <!-- 3. Layout (структура страницы) -->
    <link rel="stylesheet" href="{% static 'css/core/layout.css' %}">

    <!-- 4. Анимации -->
    <link rel="stylesheet" href="{% static 'css/core/animations.css' %}">

    <!-- 5. Темы (light/dark mode) -->
    <link rel="stylesheet" href="{% static 'css/core/themes.css' %}">

    <!-- 6. Навигация -->
    <link rel="stylesheet" href="{% static 'css/core/desktop-nav.css' %}">
    <link rel="stylesheet" href="{% static 'css/core/mobile-menu.css' %}">

    <!-- 7. Специфичные для страницы -->
    {% block extra_css %}{% endblock %}
</head>
```text
### Каскад и специфичность

Порядок важен:

1. `main.css` задает базовые переменные и reset
2. `components.css` использует эти переменные для компонентов
3. `layout.css` структурирует страницу
4. `animations.css` добавляет интерактивность
5. `themes.css` перезаписывает переменные для темной темы
6. Навигация использует все предыдущие стили
7. Специфичные файлы могут перезаписывать любое

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

    <!-- Core CSS -->
    <link rel="stylesheet" href="{% static 'css/core/main.css' %}">
    <link rel="stylesheet" href="{% static 'css/core/components.css' %}">
    <link rel="stylesheet" href="{% static 'css/core/layout.css' %}">
    <link rel="stylesheet" href="{% static 'css/core/animations.css' %}">
    <link rel="stylesheet" href="{% static 'css/core/themes.css' %}">
    <link rel="stylesheet" href="{% static 'css/core/desktop-nav.css' %}">
    <link rel="stylesheet" href="{% static 'css/core/mobile-menu.css' %}">

    <!-- Page specific CSS -->
    {% block extra_css %}{% endblock %}
</head>
<body>
    <div class="main-wrapper">
        {% include 'shared/_header.html' %}

        <main class="content-wrapper">
            {% block content %}{% endblock %}
        </main>

        {% include 'shared/_footer.html' %}
    </div>

    <!-- Core JS -->
    <script src="{% static 'js/core/main.js' %}" defer></script>
    <script src="{% static 'js/core/desktop-nav.js' %}" defer></script>
    <script src="{% static 'js/core/mobile-menu.js' %}" defer></script>

    {% block extra_js %}{% endblock %}
</body>
</html>
```text
### home.html (главная)

```django
{% extends "base.html" %}
{% load static %}

{% block title %}Главная - PySchool{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="{% static 'css/core/home.css' %}">
{% endblock %}

{% block content %}
<section class="hero-section">
    <div class="container">
        <div class="hero-content fade-in">
            <h1>Изучайте Python онлайн</h1>
            <p>Интерактивные курсы для начинающих и профессионалов</p>
            <a href="{% url 'courses:list' %}" class="btn btn-primary btn-lg hover-scale">
                Начать обучение
            </a>
        </div>
    </div>
</section>

<section class="features-section">
    {% include 'shared/_features_section.html' %}
</section>
{% endblock %}
```text
### contacts.html (контакты)

```django
{% extends "base.html" %}
{% load static %}

{% block title %}Контакты - PySchool{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="{% static 'css/courses.css' %}">
<link rel="stylesheet" href="{% static 'css/phone-input.css' %}">
<link rel="stylesheet" href="{% static 'css/core/contact-form.css' %}">
{% endblock %}

{% block content %}
<div class="contact-container">
    <form class="contact-form" method="post">
        {% csrf_token %}
        <!-- Форма -->
    </form>

    <div class="contact-info">
        <!-- Контактная информация -->
    </div>
</div>
{% endblock %}
```text
---

## 🎨 Темизация

### Светлая тема (по умолчанию)

```css
:root {
    --bg-primary: #ffffff;
    --bg-secondary: #f8f9fa;
    --bg-tertiary: #e9ecef;

    --text-primary: #212529;
    --text-secondary: #6c757d;
    --text-muted: #adb5bd;

    --border-color: #dee2e6;
    --shadow: 0 2px 4px rgba(0,0,0,0.1);
}
```text
### Темная тема

```css
[data-theme="dark"] {
    --bg-primary: #1a1a1a;
    --bg-secondary: #2d2d2d;
    --bg-tertiary: #3a3a3a;

    --text-primary: #e0e0e0;
    --text-secondary: #9e9e9e;
    --text-muted: #757575;

    --border-color: #4a4a4a;
    --shadow: 0 2px 4px rgba(0,0,0,0.3);
}
```text
### Переключение темы

```javascript
// main.js
function toggleTheme() {
    const currentTheme = document.body.dataset.theme || 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';

    document.body.dataset.theme = newTheme;
    localStorage.setItem('theme', newTheme);
}

// Инициализация при загрузке
document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.body.dataset.theme = savedTheme;
});
```text
---

## 📱 Адаптивность

### Breakpoints

```css
/* Mobile */
@media (max-width: 575px) { }

/* Tablet */
@media (min-width: 576px) and (max-width: 991px) { }

/* Desktop */
@media (min-width: 992px) { }

/* Large Desktop */
@media (min-width: 1200px) { }
```text
### Адаптивная навигация

- **Desktop (≥992px)**: `desktop-nav.css` - горизонтальное меню
- **Mobile (<992px)**: `mobile-menu.css` - бургер-меню

### Адаптивный layout

```css
/* Mobile first подход */
.container {
    width: 100%;
    padding: 0 1rem;
}

/* Tablet */
@media (min-width: 768px) {
    .container {
        max-width: 720px;
        margin: 0 auto;
    }
}

/* Desktop */
@media (min-width: 992px) {
    .container {
        max-width: 960px;
    }
}

/* Large Desktop */
@media (min-width: 1200px) {
    .container {
        max-width: 1140px;
    }
}
```text
---

## 📊 Статистика

- **Всего CSS файлов**: 10
- **Базовые стили**: `main.css`, `components.css`, `layout.css`
- **Функциональные**: `animations.css`, `themes.css`
- **Навигация**: `desktop-nav.css`, `mobile-menu.css`
- **Специфичные**: `home.css`, `contact-form.css`, `legal-pages.css`
- **Шаблонов использующих**: 8 (base.html + 7 страниц)

---

## 🔗 Связанные документы

- **JavaScript**: `static/js/core/README.md` - документация JS файлов
- **Шаблоны**: `core/templates/` - HTML шаблоны core
- **Блог стили**: `static/css/blog/README.md` - стили блога
