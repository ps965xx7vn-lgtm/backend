# Blog JavaScript Files

JavaScript файлы для интерактивности приложения блога, организованные по функциональности.

## 📋 Содержание

- [Файлы и их назначение](#файлы-и-их-назначение)
- [Архитектура и взаимодействие](#архитектура-и-взаимодействие)
- [API эндпоинты](#api-эндпоинты)
- [Использование в шаблонах](#использование-в-шаблонах)
- [Конвенции кода](#конвенции-кода)
- [Обработка ошибок](#обработка-ошибок)
- [Поддержка и обновление](#поддержка-и-обновление)

## 📁 Файлы и их назначение

### `article-comments.js`

Управление комментариями на странице статьи.

**Функциональность:**

- Отображение формы ответа на комментарий (reply)
- Скрытие форм ответа
- AJAX отправка комментариев
- Динамическое добавление новых комментариев в DOM
- Обновление счетчика комментариев
- Валидация формы (минимум 3 символа)

**API запросы:**

```javascript
POST /blog/ajax/add-comment/
Body: {
    article_id: number,
    content: string,
    parent_id?: number  // Для ответов
}
Response: {
    success: boolean,
    comment_html: string,
    comments_count: number
}
```text
**События:**

- Click на `.reply-btn` - показать форму ответа
- Click на `.cancel-reply-btn` - скрыть форму ответа
- Submit на `.comment-form` - отправить комментарий

**Используется в:**

- `blog/article_detail.html`

**Зависимости:**

- Требует CSRF token (Django)
- Работает с HTML разметкой из `.comment-section`

**Ключевые функции:**

```javascript
showReplyForm(commentId)           // Показать форму ответа
hideReplyForm()                    // Скрыть все формы
submitComment(form, articleId)     // Отправить комментарий
updateCommentsCount(count)         // Обновить счетчик
```text
---

### `article-detail.js`

Общая функциональность страницы статьи.

**Функциональность:**

- Отслеживание прогресса чтения (scroll)
- Сохранение позиции чтения
- Визуальный индикатор прогресса (progress bar)
- Плавная прокрутка к якорям
- Копирование кода из code blocks
- Управление закладками (bookmarks)
- Показ/скрытие оглавления (Table of Contents)

**API запросы:**

```javascript
POST /blog/ajax/update-reading-progress/
Body: {
    article_id: number,
    progress: number  // 0-100
}
Response: {
    success: boolean
}

POST /blog/ajax/toggle-bookmark/
Body: {
    article_id: number
}
Response: {
    success: boolean,
    is_bookmarked: boolean
}
```text
**События:**

- Scroll - обновление прогресса чтения (throttled 1s)
- Click на `.bookmark-btn` - добавить/удалить закладку
- Click на `.copy-code-btn` - копировать код
- Click на `.toc-toggle` - показать/скрыть оглавление

**Используется в:**

- `blog/article_detail.html`

**Зависимости:**

- Требует authenticated user для прогресса и закладок
- Работает с `.reading-progress-bar`, `.bookmark-btn`, `.toc-container`

**Ключевые функции:**

```javascript
calculateReadingProgress()         // Вычислить прогресс 0-100
updateProgressBar(progress)        // Обновить визуальный индикатор
saveReadingProgress(articleId, progress) // Сохранить на сервер
toggleBookmark(articleId)          // Toggle закладки
copyCodeToClipboard(codeElement)   // Копировать код
```text
---

### `article-reactions.js`

Управление реакциями (лайки/дизлайки) на статьи.

**Функциональность:**

- Toggle лайков и дизлайков
- Обновление счетчиков реакций
- Визуальная индикация активных реакций
- Взаимоисключение лайка и дизлайка (только одна реакция)
- Отображение toast уведомлений

**API запросы:**

```javascript
POST /blog/ajax/toggle-reaction/
Body: {
    article_id: number,
    reaction_type: 'like' | 'dislike'
}
Response: {
    success: boolean,
    likes_count: number,
    dislikes_count: number,
    user_reaction: 'like' | 'dislike' | null
}
```text
**События:**

- Click на `.reaction-btn[data-reaction="like"]` - поставить/убрать лайк
- Click на `.reaction-btn[data-reaction="dislike"]` - поставить/убрать дизлайк

**Используется в:**

- `blog/article_detail.html`

**Зависимости:**

- Требует authenticated user
- Работает с `.reactions-container` и `.reaction-btn`
- CSS классы: `.liked`, `.disliked` для активных состояний

**Ключевые функции:**

```javascript
toggleReaction(articleId, reactionType) // Toggle лайка/дизлайка
updateReactionUI(likesCount, dislikesCount, userReaction) // Обновить UI
showToast(message)                   // Показать уведомление
```text
**Логика:**

- Клик на лайк при отсутствии реакции → добавляет лайк
- Клик на лайк при наличии лайка → убирает лайк
- Клик на лайк при наличии дизлайка → меняет на лайк
- То же самое для дизлайка

---

### `blog.js`

Общая функциональность для страниц списков статей.

**Функциональность:**

- Фильтрация статей по категории
- Фильтрация по сложности (difficulty)
- Сортировка статей (дата, популярность, рейтинг)
- Пагинация с AJAX загрузкой
- Lazy loading изображений
- Показ/скрытие фильтров на мобильных устройствах
- Debounced поиск

**События:**

- Change на `.category-filter` - фильтр по категории
- Change на `.difficulty-filter` - фильтр по сложности
- Change на `.sort-select` - сортировка
- Click на `.page-link` - пагинация
- Scroll - lazy loading изображений
- Click на `.filter-toggle` - показать/скрыть фильтры (mobile)

**Используется в:**

- `blog/article_list.html`
- `blog/home.html`
- `blog/category_detail.html`

**Зависимости:**

- Intersection Observer API для lazy loading
- URL Search Params для управления фильтрами

**Ключевые функции:**

```javascript
applyFilters()                       // Применить все фильтры
updateURL(params)                    // Обновить URL с параметрами
loadArticles(url)                    // AJAX загрузка статей
initLazyLoading()                    // Инициализация lazy load
debounce(func, delay)                // Debounce helper
```text
**URL параметры:**

```text
?category=python              # Фильтр по категории
?difficulty=beginner          # Фильтр по сложности
?sort=-views_count           # Сортировка по просмотрам
?page=2                      # Страница пагинации
```text
---

### `search-highlight.js` (извлечен из inline)

Подсветка найденных слов на странице результатов поиска.

**Функциональность:**

- Автоматическая подсветка search query в тексте
- Обертка совпадений в `<mark class="search-highlight">`
- Игнорирование HTML тегов и атрибутов
- Case-insensitive поиск
- Экранирование специальных символов regex

**Используется в:**

- `blog/search_results.html`

**Зависимости:**

- CSS класс `.search-highlight` из `search-results.css`
- Требует data-атрибут `data-search-query` на контейнере

**Ключевые функции:**

```javascript
highlightSearchTerms(query)          // Подсветить все совпадения
escapeRegex(string)                  // Экранировать regex символы
wrapTextNode(node, regex)            // Обернуть текстовый узел
```text
**Использование:**

```html
<div class="search-results" data-search-query="{{ search_query|escapejs }}">
    <div class="search-result-item">
        <p>Python is a programming language...</p>
    </div>
</div>

<script src="{% static 'js/blog/search-highlight.js' %}"></script>
```text
**Результат:**

```html
<p><mark class="search-highlight">Python</mark> is a programming language...</p>
```text
---

### `tag-filter.js` (извлечен из inline)

Фильтрация и сортировка статей на странице тега (`tag_detail.html`).

**Функциональность:**

- Сортировка статей по дате, популярности, рейтингу
- Фильтрация по сложности (beginner/intermediate/advanced)
- Обновление URL без перезагрузки страницы
- Сохранение состояния фильтров в URL

**События:**

- Change на `#sort-select` - изменение сортировки
- Change на `#difficulty-filter` - фильтрация по сложности

**Используется в:**

- `blog/tag_detail.html`

**Зависимости:**

- URL Search Params
- Работает с `<select>` элементами для фильтров

**Ключевые функции:**

```javascript
updateFilters()                      // Применить фильтры и обновить URL
getQueryParams()                     // Получить текущие параметры URL
setQueryParams(params)               // Установить параметры URL
```text
**URL параметры:**

```text
?sort=-published_at              # Сортировка по дате (новые)
?sort=-views_count              # Сортировка по популярности
?sort=-likes_count              # Сортировка по рейтингу
?difficulty=beginner            # Фильтр по сложности
```text
---

### `tag-search.js` (извлечен из inline)

Real-time поиск тегов на странице списка тегов (`tag_list.html`).

**Функциональность:**

- Мгновенная фильтрация тегов по названию (input)
- Case-insensitive поиск
- Показ/скрытие сообщения "Тегов не найдено"
- Debounced поиск (300ms)
- Подсчет найденных тегов

**События:**

- Input на `.tag-search-input` - фильтрация тегов

**Используется в:**

- `blog/tag_list.html`

**Зависимости:**

- CSS классы из `tag-list.css`
- Работает с `.tag-cloud` и `.tag-item`

**Ключевые функции:**

```javascript
filterTags(searchQuery)              // Фильтровать теги
showNoTagsMessage()                  // Показать сообщение
hideNoTagsMessage()                  // Скрыть сообщение
debounce(func, delay)                // Debounce helper
```text
**Использование:**

```html
<input type="text" class="tag-search-input" placeholder="Поиск тегов...">
<div class="tag-cloud">
    <a href="..." class="tag-item" data-tag-name="Python">Python</a>
    <a href="..." class="tag-item" data-tag-name="Django">Django</a>
</div>
<p class="no-tags-message" style="display: none;">Тегов не найдено</p>

<script src="{% static 'js/blog/tag-search.js' %}"></script>
```text
---

## 🏗️ Архитектура и взаимодействие

### Структура приложения

```text
Страница статьи (article_detail.html)
│
├── article-detail.js         # Прогресс чтения, закладки, TOC
├── article-reactions.js      # Лайки/дизлайки
└── article-comments.js       # Комментарии и ответы

Список статей (article_list.html)
│
└── blog.js                   # Фильтрация, сортировка, пагинация

Страница поиска (search_results.html)
│
└── search-highlight.js       # Подсветка результатов

Страница тега (tag_detail.html)
│
└── tag-filter.js             # Фильтрация и сортировка

Список тегов (tag_list.html)
│
└── tag-search.js             # Real-time поиск
```text
### Взаимодействие файлов

Файлы **независимы** друг от друга - не импортируют функции друг друга.

Каждый файл:

- Инициализируется при `DOMContentLoaded`
- Работает со своими DOM элементами
- Делает свои AJAX запросы
- Имеет свои event listeners

**Общие зависимости:**

- Django CSRF token (для POST запросов)
- Fetch API (для AJAX)
- DOM API (для манипуляций)

---

## 🔌 API эндпоинты

### Django Views (AJAX endpoints)

Все AJAX эндпоинты определены в `blog/views.py` и `blog/urls.py`.

#### Комментарии

```python

# blog/urls.py

path('ajax/add-comment/', AddCommentView.as_view(), name='add_comment')
```text
```javascript
// article-comments.js
fetch('/blog/ajax/add-comment/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
    },
    body: JSON.stringify({
        article_id: articleId,
        content: content,
        parent_id: parentId
    })
})
```text
#### Реакции

```python

# blog/urls.py

path('ajax/toggle-reaction/', ToggleReactionView.as_view(), name='toggle_reaction')
```text
```javascript
// article-reactions.js
fetch('/blog/ajax/toggle-reaction/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
    },
    body: JSON.stringify({
        article_id: articleId,
        reaction_type: 'like' // или 'dislike'
    })
})
```text
#### Закладки

```python

# blog/urls.py

path('ajax/toggle-bookmark/', ToggleBookmarkView.as_view(), name='toggle_bookmark')
```text
```javascript
// article-detail.js
fetch('/blog/ajax/toggle-bookmark/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
    },
    body: JSON.stringify({
        article_id: articleId
    })
})
```text
#### Прогресс чтения

```python

# blog/urls.py

path('ajax/update-reading-progress/', UpdateReadingProgressView.as_view(), name='update_reading_progress')
```text
```javascript
// article-detail.js
fetch('/blog/ajax/update-reading-progress/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
    },
    body: JSON.stringify({
        article_id: articleId,
        progress: progress // 0-100
    })
})
```text
### REST API (опционально)

Также доступны REST API эндпоинты через Django Ninja (`blog/api.py`):

```javascript
// Альтернатива через REST API
fetch('/api/blog/articles/article-slug/react/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + jwtToken
    },
    body: JSON.stringify({
        reaction_type: 'like'
    })
})
```text
---

## 📄 Использование в шаблонах

### Базовая структура подключения

```django
{% extends "base.html" %}
{% load static %}

{% block extra_js %}
    <script src="{% static 'js/blog/article-detail.js' %}" defer></script>
    <script src="{% static 'js/blog/article-reactions.js' %}" defer></script>
{% endblock %}
```text
### Карта использования

| Шаблон | JavaScript файлы |
|--------|------------------|
| `article_detail.html` | `article-detail.js`, `article-reactions.js`, `article-comments.js` |
| `article_list.html` | `blog.js` |
| `home.html` | `blog.js` |
| `category_detail.html` | `blog.js` |
| `tag_detail.html` | `tag-filter.js` |
| `tag_list.html` | `tag-search.js` |
| `search_results.html` | `search-highlight.js` |
| `series_list.html` | Нет JS (только CSS) |
| `series_detail.html` | Нет JS (только CSS) |

### Важные data-атрибуты

JavaScript файлы ожидают определенные data-атрибуты на элементах:

```html
<!-- article-comments.js -->
<button class="reply-btn" data-comment-id="{{ comment.id }}">Ответить</button>

<!-- article-reactions.js -->
<button class="reaction-btn"
        data-reaction="like"
        data-article-id="{{ article.id }}">
    👍 <span class="reaction-count">{{ article.likes_count }}</span>
</button>

<!-- article-detail.js -->
<button class="bookmark-btn"
        data-article-id="{{ article.id }}"
        data-bookmarked="{{ is_bookmarked|yesno:'true,false' }}">
    🔖
</button>

<!-- search-highlight.js -->
<div class="search-results" data-search-query="{{ search_query|escapejs }}">
    ...
</div>

<!-- tag-search.js -->
<a href="..." class="tag-item" data-tag-name="{{ tag.name }}">{{ tag.name }}</a>
```text
---

## 💻 Конвенции кода

### Именование функций

```javascript
// Глаголы для действий
function showReplyForm(commentId) { }
function hideReplyForm() { }
function submitComment(form, articleId) { }

// get для получения данных
function getCSRFToken() { }
function getArticleId() { }

// update для обновления UI/данных
function updateCommentsCount(count) { }
function updateProgressBar(progress) { }

// toggle для переключения состояния
function toggleReaction(articleId, type) { }
function toggleBookmark(articleId) { }

// init для инициализации
function initLazyLoading() { }
function initEventListeners() { }
```text
### Async/Await для AJAX

```javascript
// ✅ Правильно: async/await с try-catch
async function submitComment(form, articleId) {
    try {
        const response = await fetch('/blog/ajax/add-comment/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (result.success) {
            // Обработка успеха
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('Произошла ошибка');
    }
}
```text
### Event Delegation

Для динамических элементов используется event delegation:

```javascript
// ✅ Правильно: delegation на родительский элемент
document.querySelector('.comments-list').addEventListener('click', (e) => {
    if (e.target.classList.contains('reply-btn')) {
        const commentId = e.target.dataset.commentId;
        showReplyForm(commentId);
    }
});

// ❌ Неправильно: direct listeners (не работает для динамических элементов)
document.querySelectorAll('.reply-btn').forEach(btn => {
    btn.addEventListener('click', () => { });
});
```text
### DOMContentLoaded

Весь код инициализации обернут в:

```javascript
document.addEventListener('DOMContentLoaded', function() {
    // Инициализация
    initEventListeners();
    initLazyLoading();

    // Event listeners
    document.querySelector('.btn').addEventListener('click', handleClick);
});
```text
---

## ⚠️ Обработка ошибок

### Паттерн обработки AJAX ошибок

```javascript
async function makeRequest(url, data) {
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify(data)
        });

        // Проверка HTTP статуса
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();

        // Проверка бизнес-логики
        if (!result.success) {
            throw new Error(result.error || 'Произошла ошибка');
        }

        return result;

    } catch (error) {
        console.error('Error:', error);

        // Показать пользователю
        showToast('Произошла ошибка: ' + error.message);

        // Fallback действие
        return null;
    }
}
```text
### Валидация перед отправкой

```javascript
function validateCommentForm(content) {
    if (!content || content.trim().length < 3) {
        showToast('Комментарий должен содержать минимум 3 символа');
        return false;
    }

    if (content.length > 5000) {
        showToast('Комментарий слишком длинный (макс 5000 символов)');
        return false;
    }

    return true;
}
```text
### Защита от спама (debounce/throttle)

```javascript
// Debounce для поиска (не чаще чем каждые 300ms)
function debounce(func, delay) {
    let timeoutId;
    return function(...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
}

// Throttle для scroll events (не чаще чем раз в секунду)
function throttle(func, delay) {
    let lastCall = 0;
    return function(...args) {
        const now = Date.now();
        if (now - lastCall >= delay) {
            lastCall = now;
            func.apply(this, args);
        }
    };
}

// Использование
const debouncedSearch = debounce(searchTags, 300);
const throttledProgress = throttle(updateProgress, 1000);
```text
---

## 🔧 Поддержка и обновление

### Добавление нового функционала

1. **Определите функциональность**: Это специфично для страницы или переиспользуемо?
2. **Выберите файл**:
   - Специфично для страницы → добавьте в существующий `{page}.js`
   - Новая страница → создайте новый `{page}.js`
   - Переиспользуемый компонент → создайте `{component}.js`
3. **Следуйте конвенциям**: async/await, event delegation, error handling
4. **Добавьте API endpoint** (если нужно):
   - Django view в `blog/views.py`
   - URL в `blog/urls.py`
5. **Обновите README**: добавьте описание файла

### Извлечение inline скриптов

Если в шаблоне есть `<script>` блоки:

```django
{% block extra_js %}
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Inline код
        });
    </script>
{% endblock %}
```text
**Шаги извлечения:**

1. **Найдите inline скрипты**: `grep -r "<script>" src/blog/templates/`
2. **Создайте файл**: `{functionality}.js` в `static/js/blog/`
3. **Перенесите код**: скопируйте весь JS код
4. **Обработайте Django переменные**: замените на data-атрибуты

   ```django
   <!-- Было -->
   <script>
       const articleId = {{ article.id }};
   </script>

   <!-- Стало -->
   <div data-article-id="{{ article.id }}">

   <script src="{% static 'js/blog/article-detail.js' %}"></script>
   ```

5. **Подключите файл**: `<script src="{% static 'js/blog/...' %}" defer></script>`
6. **Удалите inline**: удалите `<script>` блок из шаблона
7. **Скопируйте в staticfiles**: `python manage.py collectstatic`

### Отладка

**Console logging:**

```javascript
// Для разработки
console.log('Article ID:', articleId);
console.error('Error:', error);

// Для production - удалите или замените на:
if (DEBUG) {
    console.log('Debug info:', data);
}
```text
**Chrome DevTools:**

- **Sources** → Breakpoints для пошаговой отладки
- **Network** → XHR для просмотра AJAX запросов
- **Console** → Для ошибок и логов
- **Elements** → Для проверки DOM изменений

**Django Debug Toolbar:**

```python

# В .env

DEBUG=True

# Просмотр AJAX запросов в браузере

# Toolbar покажет SQL queries, cache hits, etc

```text
### Testing

**Manual testing checklist:**

```text
✅ Функция работает в Chrome/Firefox/Safari
✅ Работает на мобильных устройствах
✅ Обрабатываются ошибки сети
✅ Обрабатываются ошибки валидации
✅ UI обновляется корректно
✅ Нет утечек памяти (не висят listeners)
✅ CSRF token передается
✅ Authenticated users only (где нужно)
```text
**Browser compatibility:**

- Используется современный JS (ES6+)
- Fetch API (requires polyfill для IE11)
- Arrow functions, async/await, template literals
- Целевые браузеры: Chrome 90+, Firefox 88+, Safari 14+

---

## 📊 Статистика

- **Всего JS файлов**: 7
- **Общий объем**: ~2000 строк кода
- **AJAX endpoints**: 4 (комментарии, реакции, закладки, прогресс)
- **Event listeners**: ~30
- **Async функций**: ~15
- **Шаблонов использующих**: 9

---

## 📝 Changelog

### 2025-01-15

- ✅ Извлечен inline JS из `tag_list.html` → `tag-search.js`
- ✅ Извлечен inline JS из `tag_detail.html` → `tag-filter.js`
- ✅ Извлечен inline JS из `search_results.html` → `search-highlight.js`
- ✅ Обновлены все ссылки в шаблонах
- ✅ Все скрипты переведены на async/await
- ✅ Добавлена обработка ошибок во все AJAX функции
- ✅ Создан README.md

### История

- Ранее: все inline скрипты в шаблонах
- Рефакторинг: разделение на модули
- Стандартизация: единые правила кода

---

## 🔗 Связанные документы

- **Стили**: `static/css/blog/README.md` - документация CSS файлов
- **Шаблоны**: `blog/templates/README.md` - документация HTML шаблонов
- **Views**: `blog/views.py` - AJAX endpoints (строки 533-2994)
- **URLs**: `blog/urls.py` - URL маршруты AJAX
- **Приложение**: `blog/README.md` - общая документация блога
- **API**: `BLOG_API_DOCUMENTATION.md` - REST API документация

---

## 🚀 Быстрый старт

### Добавление нового AJAX эндпоинта

**1. Создайте Django view:**

```python

# blog/views.py

from django.views import View
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin

class MyAjaxView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)

            # Ваша логика

            return JsonResponse({
                'success': True,
                'result': result
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
```text
**2. Добавьте URL:**

```python

# blog/urls.py

urlpatterns = [
    path('ajax/my-action/', MyAjaxView.as_view(), name='my_action'),
]
```text
**3. Создайте JS функцию:**

```javascript
// static/js/blog/my-feature.js
async function myAction(dataId) {
    try {
        const response = await fetch('/blog/ajax/my-action/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({ data_id: dataId })
        });

        const result = await response.json();

        if (result.success) {
            // Обработка успеха
            console.log('Success:', result.result);
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

document.addEventListener('DOMContentLoaded', function() {
    document.querySelector('.my-btn').addEventListener('click', function() {
        const dataId = this.dataset.dataId;
        myAction(dataId);
    });
});
```text
**4. Подключите в шаблоне:**

```django
{% extends "base.html" %}
{% load static %}

{% block extra_js %}
    <script src="{% static 'js/blog/my-feature.js' %}" defer></script>
{% endblock %}

{% block content %}
    <button class="my-btn" data-data-id="123">Действие</button>
{% endblock %}
```text
**5. Collectstatic:**

```bash
python manage.py collectstatic --noinput
```text
Готово! 🎉
