# Структура статических файлов PyLand

## 📁 Организация файлов

Все статические файлы организованы по принципу **"каждое приложение имеет
свои файлы"**. Это позволяет:

- ✅ Легко находить и модифицировать стили конкретного приложения
- ✅ Избежать конфликтов при изменении стилей
- ✅ Масштабировать приложения независимо друг от друга
- ✅ Оптимизировать загрузку (загружаются только нужные файлы)

---

## 🗂️ Структура директорий

```text
static/
├── css/
│   ├── students/        # Стили для личного кабинета
│   ├── blog/           # Стили для блога
│   ├── core/           # Общие/базовые стили
│   ├── courses/        # Стили для курсов
│   ├── payments/       # Стили для платежной системы
│   └── managers/        # Стили для админ-панели
│
└── js/
    ├── students/        # Скрипты для личного кабинета
    ├── blog/           # Скрипты для блога
    ├── core/           # Общие/базовые скрипты
    ├── courses/        # Скрипты для курсов
    ├── payments/       # Скрипты для платежной системы
    └── managers/        # Скрипты для админ-панели
```text
---

## 📦 Детальное описание

### 🔷 css/students/ (7 файлов)

Стили для личного кабинета пользователя:

- `code-blocks.css` - подсветка кода в уроках (локальная версия)
- `courses.css` - отображение курсов в дашборде
- `dashboard.css` - основной дашборд
- `markdown.css` - рендеринг markdown контента (локальная версия)
- `password-reset.css` - формы сброса пароля
- `phone-input.css` - поле ввода телефона (локальная версия)
- `settings.css` - страница настроек профиля

**Используется в шаблонах:**

- `students/dashboard/*.html`
- `students/password_reset/*.html`
- `students/auth/*.html`

---

### 🔷 css/blog/ (9 файлов)

Стили для блога:

- `article.css` - детальная страница статьи
- `code-blocks.css` - подсветка кода в статьях (локальная версия)
- `markdown.css` - рендеринг markdown в статьях (локальная версия)
- `pagination.css` - пагинация списков
- `reactions.css` - реакции на статьи
- `search-results.css` - результаты поиска
- `series-detail.css` - детальная страница серии
- `series.css` - список серий
- `tag-list.css` - список тегов
- `utils.css` - утилиты и хелперы для blog

**Используется в шаблонах:**

- `blog/article_*.html`
- `blog/category_*.html`
- `blog/tag_*.html`
- `blog/series_*.html`
- `blog/home.html`

---

### 🔷 css/core/ (10 файлов)

Базовые стили, используемые на всех страницах:

- `animations.css` - анимации и transitions
- `code-blocks.css` - базовая подсветка кода (общая версия)
- `components.css` - переиспользуемые компоненты
- `contact-form.css` - форма контактов
- `desktop-nav.css` - десктопная навигация
- `home.css` - главная страница
- `layout.css` - общая структура страниц
- `legal-pages.css` - юридические страницы
- `main.css` - основные стили
- `markdown.css` - базовый рендеринг markdown (общая версия)
- `mobile-menu.css` - мобильное меню
- `phone-input.css` - базовое поле телефона (общая версия)
- `themes.css` - темы оформления

**Используется в:**

- `base.html` - подключается на всех страницах
- `core/home.html`, `core/about.html`, `core/contacts.html`
- `core/legal/*.html`

---

### 🔷 css/courses/ (2 файла)

Стили для публичных страниц курсов:

- `courses.css` - список и детали курсов (+ используется как универсальный layout для карточек)
- `markdown.css` - рендеринг описания курса (локальная версия)

**Используется в шаблонах:**

- `courses/courses.html`
- `courses/course_detail.html`
- **Также используется** в `blog/*`, `core/about.html`, `core/contacts.html` как универсальная система карточек

---

### 🔷 css/payments/ (2 файла)

Стили для платежной системы Paddle Billing:

- `checkout.css` - форма checkout с выбором валюты
- `paddle_checkout.css` - Paddle.js overlay интеграция

**Используется в шаблонах:**

- `payments/checkout.html` - форма оформления заказа
- `payments/paddle_redirect.html` - Paddle overlay checkout
- `payments/payment_success.html` - страница успеха
- `payments/payment_cancel.html` - страница отмены

---

### 🔷 css/managers/ (1 файл)

Стили для админ-панели менеджера:

- `dashboard.css` - админ-панель управления

**Используется в шаблонах:**

- `managers/base.html` и все шаблоны manager

---

### 🔷 js/students/ (4 файла)

Скрипты для личного кабинета:

- `dashboard.js` - функционал дашборда
- `dashboard-mobile.js` - мобильная версия дашборда
- `lesson-steps.js` - навигация по шагам урока
- `phone-input.js` - обработка поля телефона (локальная версия)

---

### 🔷 js/blog/ (8 файлов)

Скрипты для блога:

- `article-comments.js` - комментарии к статьям
- `article-detail.js` - детальная страница статьи
- `article-reactions.js` - реакции на статьи
- `blog.js` - общая логика блога
- `code-copy.js` - копирование кода из блоков (локальная версия)
- `search-highlight.js` - подсветка результатов поиска
- `tag-filter.js` - фильтрация по тегам
- `tag-search.js` - поиск тегов

---

### 🔷 js/core/ (5 файлов)

Базовые скрипты:

- `code-copy.js` - базовое копирование кода (общая версия)
- `desktop-nav.js` - десктопная навигация
- `legal-ppayments/ (2 файла)

Скрипты для платежной системы:

- `checkout.js` - функционал формы checkout
- `paddle_checkout.js` - Paddle.js SDK интеграция и обработка событий

---

### 🔷 js/ages.js` - функционал юридических страниц
- `main.js` - основная логика
- `mobile-menu.js` - мобильное меню
- `phone-input.js` - базовое поле телефона (общая версия)

---

### 🔷 js/courses/ (2 файла)

Скрипты для курсов:

- `course-detail.js` - детальная страница курса
- `courses.js` - список курсов и общая логика

---

### 🔷 js/managers/ (1 файл)

- `dashboard.js` - админ-панель

---

## 🔄 Дублированные файлы

Некоторые файлы дублированы для каждого приложения, чтобы можно было кастомизировать их независимо:

### code-blocks.css

- ✅ `css/core/code-blocks.css` - базовая версия
- ✅ `css/students/code-blocks.css` - для уроков в дашборде
- ✅ `css/blog/code-blocks.css` - для статей блога

### markdown.css

- ✅ `css/core/markdown.css` - базовая версия
- ✅ `css/students/markdown.css` - для контента в дашборде
- ✅ `css/blog/markdown.css` - для статей блога
- ✅ `css/courses/markdown.css` - для описания курсов

### phone-input.css

- ✅ `css/core/phone-input.css` - базовая версия
- ✅ `css/students/phone-input.css` - для настроек профиля

### phone-input.js

- ✅ `js/core/phone-input.js` - базовая версия
- ✅ `js/students/phone-input.js` - для настроек профиля

### code-copy.js

- ✅ `js/core/code-copy.js` - базовая версия
- ✅ `js/blog/code-copy.js` - для статей блога

---

## 📝 Правила использования

### 1️⃣ Подключение в шаблонах

```django
{% block extra_css %}
<link rel="stylesheet" href="{% static 'css/[app]/[file].css' %}">
{% endblock %}

{% block extra_js %}
<script src="{% static 'js/[app]/[file].js' %}"></script>
{% endblock %}
```text
### 2️⃣ Создание нового файла

```bash

# CSS

touch src/static/css/[app]/new-feature.css

# JavaScript

touch src/static/js/[app]/new-feature.js
```text
### 3️⃣ Общие vs специфичные файлы

- **Общие (core/)** - используются на многих страницах, изменения влияют глобально
- **Специфичные (app/)** - используются только в конкретном приложении

### 4️⃣ Когда создавать дубликат

Создавайте локальную копию из `core/`, если:

- ✅ Нужны специфичные изменения только для вашего приложения
- ✅ Файл используется в 2+ разных приложениях с разными стилями
- ✅ Хотите экспериментировать без риска поломать другие страницы

---

## 🚀 Оптимизация

### Размеры файлов

```bash

# Проверить размеры

find static/css static/js -type f \( -name "*.css" -o -name "*.js" \) -exec du -h {} \; | sort -h

# Минификация (для production)

python manage.py collectstatic --noinput
```text
### Сжатие

В production Django Whitenoise автоматически сжимает и кеширует статику.

---

## 📊 Статистика

**CSS:**

- students: 7 файлов
- blog: 9 файлов
- core: 10 файлов
- courses: 2 файла
- manager: 1 файл
- **Всего: 29 CSS файлов**

**JavaScript:**

- students: 4 файла
- blog: 8 файлов
- core: 5 файлов
- courses: 2 файла
- manager: 1 файл
- **Всего: 20 JS файлов**

---

## 🔍 Поиск файлов

```bash

# Найти все CSS файлы приложения

find static/css/[app] -name "*.css"

# Где используется файл

grep -r "static 'css/[app]/[file].css'" src/*/templates/

# Список всех статических файлов

find static -type f \( -name "*.css" -o -name "*.js" \)
```text
---

## ✅ Чеклист при добавлении нового функционала

- [ ] Создал файл в правильной папке (`css/[app]/` или `js/[app]/`)
- [ ] Подключил в соответствующем шаблоне через `{% static %}`
- [ ] Проверил, что файл не дублируется (если только не нужна локальная версия)
- [ ] Протестировал на разных страницах
- [ ] Добавил описание в этот README (если нужно)

---

## 📅 История изменений

**12 ноября 2025**

- ✅ Реорганизована вся структура static/
- ✅ Файлы распределены по приложениям
- ✅ Созданы дубликаты для кастомизации (code-blocks, markdown, phone-input)
- ✅ Обновлены все шаблоны (students, blog, core, courses)
- ✅ Удалены пустые и дублированные файлы
- ✅ Создана документация

---

**Автор:** PyLand Development Team
**Последнее обновление:** 12 ноября 2025
