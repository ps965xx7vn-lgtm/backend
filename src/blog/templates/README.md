# Blog Templates

HTML шаблоны для приложения блога с поддержкой SEO, адаптивного дизайна и интерактивных элементов.

## 📋 Содержание

- [Обзор](#обзор)
- [Структура шаблонов](#структура-шаблонов)
- [Основные шаблоны](#основные-шаблоны)
- [Переиспользуемые компоненты](#переиспользуемые-компоненты)
- [Context переменные](#context-переменные)
- [SEO оптимизация](#seo-оптимизация)
- [JavaScript интеграция](#javascript-интеграция)
- [Примеры использования](#примеры-использования)

## 🎯 Обзор

Шаблоны блога построены на **Bootstrap 5** с использованием Jinja2 синтаксиса Django. Все шаблоны адаптивные, оптимизированы для SEO и включают микроразметку Schema.org.

### Основные возможности

✅ Адаптивный дизайн (мобильные, планшеты, десктоп)
✅ SEO оптимизация (meta tags, Open Graph, Schema.org)
✅ Поддержка темной темы
✅ AJAX загрузка комментариев и реакций
✅ Прогресс-бар чтения статей
✅ Бесконечная прокрутка (infinite scroll)
✅ Фильтрация и сортировка статей
✅ Социальные кнопки Share
✅ Markdown рендеринг контента
✅ Кастомные template tags

## 📁 Структура шаблонов

```text
templates/blog/
├── home.html                    # Главная страница блога
├── article_list.html            # Список всех статей (с фильтрами)
├── article_detail.html          # Детальная страница статьи
├── category_list.html           # Список категорий
├── category_detail.html         # Статьи категории
├── series_list.html             # Список серий статей
├── series_detail.html           # Статьи серии
├── tag_list.html                # Список тегов
├── tag_detail.html              # Статьи с тегом
├── author_list.html             # Список авторов
├── author_detail.html           # Профиль автора + его статьи
├── difficulty_list.html         # Статьи по уровню сложности
├── featured.html                # Рекомендованные статьи
├── search_results.html          # Результаты поиска
└── includes/                    # Переиспользуемые компоненты
    ├── article_card.html        # Карточка статьи для списков
    ├── article_grid.html        # Сетка статей
    ├── comment_item.html        # Отдельный комментарий
    ├── comment_form.html        # Форма добавления комментария
    ├── reaction_buttons.html    # Кнопки лайк/дизлайк
    ├── share_buttons.html       # Кнопки соцсетей
    ├── reading_progress.html    # Прогресс-бар чтения
    ├── breadcrumbs.html         # Хлебные крошки
    ├── pagination.html          # Пагинация
    └── sidebar.html             # Боковая панель
```text
## 📄 Основные шаблоны

### home.html

**Главная страница блога**

**URL**: `/blog/`
**View**: `BlogHomeView`

**Context переменные**:

```python
{
    'featured_articles': QuerySet[Article],  # До 6 рекомендованных статей
    'latest_articles': QuerySet[Article],    # До 12 последних статей
    'popular_categories': QuerySet[Category], # До 8 категорий с count
    'popular_tags': QuerySet[Tag],           # До 20 популярных тегов
    'stats': {
        'total_articles': int,
        'total_views': int,
        'total_comments': int,
    },
    'page_title': str,                       # "Блог PySchool"
    'meta_description': str,                 # SEO описание
}
```text
**Секции**:

1. **Hero секция** - Приветствие и статистика
2. **Рекомендованные статьи** - Карусель/сетка featured статей
3. **Последние статьи** - Сетка 3x4 со всеми статьями
4. **Категории** - Список категорий с иконками и счетчиками
5. **Популярные теги** - Облако тегов

**Пример структуры**:

```html
{% extends "base.html" %}
{% load blog_extras %}

{% block title %}{{ page_title }}{% endblock %}

{% block content %}
<!-- Hero Section -->
<section class="hero-section">
    <h1>Блог PySchool</h1>
    <p>{{ meta_description }}</p>
    <div class="stats">
        <span>📝 {{ stats.total_articles }} статей</span>
        <span>👁️ {{ stats.total_views }} просмотров</span>
        <span>💬 {{ stats.total_comments }} комментариев</span>
    </div>
</section>

<!-- Featured Articles -->
{% if featured_articles %}
<section class="featured-section">
    <h2>Рекомендуемые статьи</h2>
    <div class="row">
        {% for article in featured_articles %}
            {% include "blog/includes/article_card.html" with article=article featured=True %}
        {% endfor %}
    </div>
</section>
{% endif %}

<!-- Latest Articles -->
<section class="latest-section">
    <h2>Последние статьи</h2>
    {% include "blog/includes/article_grid.html" with articles=latest_articles %}
</section>

<!-- Categories -->
<section class="categories-section">
    <h2>Категории</h2>
    <div class="categories-grid">
        {% for category in popular_categories %}
        <a href="{{ category.get_absolute_url }}" class="category-card">
            <span class="icon">{{ category.icon }}</span>
            <h3>{{ category.name }}</h3>
            <span class="count">{{ category.published_count }} статей</span>
        </a>
        {% endfor %}
    </div>
</section>

<!-- Tags Cloud -->
<section class="tags-section">
    <h2>Популярные теги</h2>
    <div class="tags-cloud">
        {% for tag in popular_tags %}
        <a href="{% url 'blog:tag_detail' tag.slug %}"
           class="tag"
           style="font-size: {{ tag.usage_count|tag_size }}px">

            #{{ tag.name }}

        </a>
        {% endfor %}
    </div>
</section>
{% endblock %}
```text
---

### article_list.html

**Список всех статей с фильтрами**

**URL**: `/blog/articles/`
**View**: `ArticleListView`

**Context переменные**:

```python
{
    'articles': Page[Article],        # Paginated список (12 на страницу)
    'categories': QuerySet[Category], # Все категории для фильтра
    'difficulties': list[tuple],      # Уровни сложности
    'current_category': str|None,     # Активный фильтр категории
    'current_difficulty': str|None,   # Активный фильтр сложности
    'current_sort': str,              # Сортировка (latest/popular/rated)
}
```text
**Фичи**:

- Фильтрация по категориям, сложности, тегам
- Сортировка: последние / популярные / рейтинговые
- Пагинация (12 статей на страницу)
- Бесконечная прокрутка (опционально)
- Показ количества результатов

---

### article_detail.html

**Детальная страница статьи**

**URL**: `/blog/articles/<slug>/`
**View**: `ArticleDetailView`

**Context переменные**:

```python
{
    'article': Article,                    # Текущая статья
    'related_articles': QuerySet[Article], # Похожие статьи (до 5)
    'comments': QuerySet[Comment],         # Корневые комментарии
    'comment_form': CommentForm,           # Форма добавления комментария
    'user_reaction': str|None,             # 'like'/'dislike'/None
    'is_bookmarked': bool,                 # Добавлена ли в закладки
    'reading_progress': int,               # Прогресс чтения (0-100)
}
```text
**Секции**:

1. **Header** - Заголовок, мета-информация, breadcrumbs
2. **Featured Image** - Главное изображение статьи
3. **Content** - Markdown контент (с подсветкой кода)
4. **Reactions** - Кнопки лайк/дизлайк
5. **Tags** - Теги статьи
6. **Share** - Кнопки социальных сетей
7. **Author** - Информация об авторе
8. **Related Articles** - Похожие статьи
9. **Comments** - Система комментариев с вложенностью

**Пример структуры**:

```html
{% extends "base.html" %}
{% load blog_extras %}
{% load markdown_extras %}

{% block title %}{{ article.meta_title|default:article.title }}{% endblock %}

{% block meta %}
<!-- SEO Meta Tags -->
<meta name="description" content="{{ article.meta_description }}">
<meta name="keywords" content="{{ article.meta_keywords }}">
<meta name="author" content="{{ article.author.username }}">

<!-- Open Graph -->
<meta property="og:title" content="{{ article.title }}">
<meta property="og:description" content="{{ article.excerpt }}">
<meta property="og:image" content="{{ article.featured_image.url }}">
<meta property="og:type" content="article">
<meta property="article:published_time" content="{{ article.published_at|date:'c' }}">
<meta property="article:author" content="{{ article.author.username }}">

<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{{ article.title }}">
<meta name="twitter:description" content="{{ article.excerpt }}">
<meta name="twitter:image" content="{{ article.featured_image.url }}">

<!-- Schema.org JSON-LD -->
<script type="application/ld+json">
{
  "@context": "<https://schema.org",>
  "@type": "BlogPosting",
  "headline": "{{ article.title }}",
  "image": "{{ article.featured_image.url }}",
  "datePublished": "{{ article.published_at|date:'c' }}",
  "dateModified": "{{ article.updated_at|date:'c' }}",
  "author": {
    "@type": "Person",
    "name": "{{ article.author.username }}"
  },
  "publisher": {
    "@type": "Organization",
    "name": "PySchool"
  },
  "description": "{{ article.excerpt }}"
}
</script>
{% endblock %}

{% block content %}
<!-- Reading Progress Bar -->
{% include "blog/includes/reading_progress.html" %}

<!-- Breadcrumbs -->
{% include "blog/includes/breadcrumbs.html" with category=article.category article=article %}

<!-- Article Header -->
<article class="article-detail" data-article-id="{{ article.id }}">
    <header class="article-header">
        <div class="meta">
            <a href="{{ article.category.get_absolute_url }}" class="category">
                {{ article.category.icon }} {{ article.category.name }}
            </a>
            <span class="difficulty">{{ article.get_difficulty_display }}</span>
            <time datetime="{{ article.published_at|date:'c' }}">
                {{ article.published_at|date:"d.m.Y" }}
            </time>
            <span class="reading-time">⏱️ {{ article.reading_time }} мин</span>
        </div>

        <h1>{{ article.title }}</h1>

        <div class="stats">
            <span>👁️ {{ article.views_count }} просмотров</span>
            <span>💬 {{ article.comments.count }} комментариев</span>
        </div>
    </header>

    <!-- Featured Image -->
    {% if article.featured_image %}
    <figure class="featured-image">
        <img src="{{ article.featured_image.url }}" alt="{{ article.title }}">
    </figure>
    {% endif %}

    <!-- Article Content (Markdown) -->
    <div class="article-content">
        {{ article.content|markdown }}
    </div>

    <!-- Reactions -->
    {% include "blog/includes/reaction_buttons.html" with article=article user_reaction=user_reaction %}

    <!-- Tags -->
    <div class="article-tags">
        {% for tag in article.tags.all %}
        <a href="{% url 'blog:tag_detail' tag.slug %}" class="tag">#{{ tag.name }}</a>
        {% endfor %}
    </div>

    <!-- Share Buttons -->
    {% include "blog/includes/share_buttons.html" with article=article %}

    <!-- Author Info -->
    {% if article.blog_author %}
    <aside class="author-card">
        <img src="{{ article.blog_author.avatar.url }}" alt="{{ article.blog_author.user.username }}">
        <div>
            <h3>{{ article.blog_author.user.get_full_name }}</h3>
            <p>{{ article.blog_author.bio }}</p>
            <a href="{{ article.blog_author.get_absolute_url }}">Все статьи автора →</a>
        </div>
    </aside>
    {% endif %}
</article>

<!-- Related Articles -->
{% if related_articles %}
<section class="related-articles">
    <h2>Похожие статьи</h2>
    <div class="row">
        {% for related in related_articles %}
            {% include "blog/includes/article_card.html" with article=related %}
        {% endfor %}
    </div>
</section>
{% endif %}

<!-- Comments Section -->
<section class="comments-section" id="comments">
    <h2>Комментарии ({{ comments.count }})</h2>

    {% if user.is_authenticated %}
        {% include "blog/includes/comment_form.html" with form=comment_form article=article %}
    {% else %}
        <p><a href="{% url 'account:login' %}">Войдите</a>, чтобы оставить комментарий</p>
    {% endif %}

    <div class="comments-list">
        {% for comment in comments %}
            {% include "blog/includes/comment_item.html" with comment=comment depth=0 %}
        {% endfor %}
    </div>
</section>
{% endblock %}

{% block extra_js %}
<script src="{% static 'js/article-detail.js' %}"></script>
<script>
// Инициализация функций статьи
document.addEventListener('DOMContentLoaded', function() {
    // Трекинг прогресса чтения
    initReadingProgress({{ article.id }});

    // AJAX реакции
    initReactions({{ article.id }});

    // AJAX комментарии
    initComments({{ article.id }});

    // Автоматическое увеличение просмотров
    incrementViews({{ article.id }});
});
</script>
{% endblock %}
```text
---

### category_detail.html

**Статьи категории**

**URL**: `/blog/categories/<slug>/`
**View**: `CategoryDetailView`

**Context**:

```python
{
    'category': Category,
    'articles': Page[Article],  # Статьи категории (пагинация)
    'total_articles': int,
}
```text
---

### series_detail.html

**Статьи серии**

**URL**: `/blog/series/<slug>/`
**View**: `SeriesDetailView`

**Context**:

```python
{
    'series': Series,
    'articles': QuerySet[Article],  # Статьи в порядке публикации
}
```text
---

### tag_detail.html

**Статьи с тегом**

**URL**: `/blog/tags/<slug>/`
**View**: `TagDetailView`

**Context**:

```python
{
    'tag': Tag,
    'articles': Page[Article],  # Статьи с тегом (пагинация)
}
```text
---

### search_results.html

**Результаты поиска**

**URL**: `/blog/search/?q=python`
**View**: `SearchView`

**Context**:

```python
{
    'query': str,              # Поисковый запрос
    'results': Page[Article],  # Найденные статьи
    'total_results': int,      # Количество результатов
}
```text
## 🧩 Переиспользуемые компоненты

### includes/article_card.html

**Карточка статьи для списков**

**Параметры**:

```python
{
    'article': Article,
    'featured': bool,  # Большая карточка для featured (optional)
}
```text
**Пример использования**:

```html
{% include "blog/includes/article_card.html" with article=article featured=True %}
```text
**Структура**:

```html
<div class="article-card {% if featured %}featured{% endif %}">
    <a href="{{ article.get_absolute_url }}">
        {% if article.featured_image %}
        <img src="{{ article.featured_image.url }}" alt="{{ article.title }}">
        {% endif %}

        <div class="card-body">
            <div class="meta">
                <span class="category">{{ article.category.icon }} {{ article.category.name }}</span>
                <span class="difficulty">{{ article.get_difficulty_display }}</span>
            </div>

            <h3>{{ article.title }}</h3>

            <p>{{ article.excerpt|truncatewords:30|clean_markdown }}</p>

            <div class="footer">
                <time>{{ article.published_at|date:"d.m.Y" }}</time>
                <span>⏱️ {{ article.reading_time }} мин</span>
                <span>👁️ {{ article.views_count }}</span>
            </div>
        </div>
    </a>
</div>
```text
---

### includes/comment_item.html

**Отдельный комментарий с вложенностью**

**Параметры**:

```python
{
    'comment': Comment,
    'depth': int,  # Уровень вложенности (0, 1, 2)
}
```text
**Пример**:

```html
{% include "blog/includes/comment_item.html" with comment=comment depth=0 %}
```text
**Структура** (с рекурсией для вложенности):

```html
<div class="comment-item"
     data-comment-id="{{ comment.id }}"
     style="margin-left: {{ depth|multiply:40 }}px">

    <div class="comment-header">
        <img src="{{ comment.author.avatar }}" alt="{{ comment.author.username }}">
        <strong>{{ comment.author.get_full_name|default:comment.author.username }}</strong>
        <time>{{ comment.created_at|timesince }} назад</time>
        {% if comment.is_edited %}<span class="edited">(изменено)</span>{% endif %}
    </div>

    <div class="comment-content">
        {{ comment.content|linebreaks }}
    </div>

    <div class="comment-actions">
        <button class="like-btn" data-comment-id="{{ comment.id }}">
            👍 {{ comment.likes_count }}
        </button>
        <button class="dislike-btn" data-comment-id="{{ comment.id }}">
            👎 {{ comment.dislikes_count }}
        </button>

        {% if user.is_authenticated and comment.can_reply %}
        <button class="reply-btn" data-comment-id="{{ comment.id }}">
            Ответить
        </button>
        {% endif %}

        {% if user == comment.author %}
        <button class="edit-btn">Редактировать</button>
        <button class="delete-btn">Удалить</button>
        {% endif %}
    </div>

    <!-- Форма ответа (скрыта по умолчанию) -->
    <div class="reply-form" id="reply-form-{{ comment.id }}" style="display: none;">
        {% include "blog/includes/comment_form.html" with parent_id=comment.id %}
    </div>

    <!-- Вложенные комментарии (рекурсия) -->
    {% if depth < 2 %}
    <div class="comment-replies">
        {% for reply in comment.get_replies %}
            {% include "blog/includes/comment_item.html" with comment=reply depth=depth|add:1 %}
        {% endfor %}
    </div>
    {% endif %}
</div>
```text
---

### includes/reaction_buttons.html

**Кнопки лайк/дизлайк**

**Параметры**:

```python
{
    'article': Article,
    'user_reaction': str|None,  # 'like'/'dislike'/None
}
```text
**Структура**:

```html
<div class="reaction-buttons" data-article-id="{{ article.id }}">
    <button class="btn-like {% if user_reaction == 'like' %}active{% endif %}"
            data-reaction="like">
        👍 <span class="count">{{ article.likes_count }}</span>
    </button>

    <button class="btn-dislike {% if user_reaction == 'dislike' %}active{% endif %}"
            data-reaction="dislike">
        👎 <span class="count">{{ article.dislikes_count }}</span>
    </button>

    {% if user.is_authenticated %}
    <button class="btn-bookmark {% if is_bookmarked %}active{% endif %}"
            data-article-id="{{ article.id }}">
        {% if is_bookmarked %}🔖{% else %}📑{% endif %} Закладки
    </button>
    {% endif %}
</div>
```text
---

### includes/pagination.html

**Пагинация для списков**

**Параметры**:

```python
{
    'page_obj': Page,  # Django Page object
}
```text
**Пример**:

```html
{% if page_obj.has_other_pages %}
    {% include "blog/includes/pagination.html" with page_obj=page_obj %}
{% endif %}
```text
## 🔍 SEO оптимизация

### Meta теги

Все шаблоны включают:

- `<title>` - Уникальный заголовок
- `<meta name="description">` - Описание страницы
- `<meta name="keywords">` - Ключевые слова
- `<link rel="canonical">` - Канонический URL

### Open Graph (Facebook, LinkedIn)

```html
<meta property="og:title" content="{{ article.title }}">
<meta property="og:description" content="{{ article.excerpt }}">
<meta property="og:image" content="{{ article.featured_image.url }}">
<meta property="og:type" content="article">
<meta property="og:url" content="{{ request.build_absolute_uri }}">
```text
### Twitter Card

```html
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{{ article.title }}">
<meta name="twitter:description" content="{{ article.excerpt }}">
<meta name="twitter:image" content="{{ article.featured_image.url }}">
```text
### Schema.org (JSON-LD)

```html
<script type="application/ld+json">
{
  "@context": "<https://schema.org",>
  "@type": "BlogPosting",
  "headline": "{{ article.title }}",
  "image": "{{ article.featured_image.url }}",
  "datePublished": "{{ article.published_at|date:'c' }}",
  "dateModified": "{{ article.updated_at|date:'c' }}",
  "author": {
    "@type": "Person",
    "name": "{{ article.author.username }}"
  },
  "publisher": {
    "@type": "Organization",
    "name": "PySchool",
    "logo": {
      "@type": "ImageObject",
      "url": "{{ STATIC_URL }}images/logo.png"
    }
  },
  "description": "{{ article.excerpt }}",
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "{{ request.build_absolute_uri }}"
  }
}
</script>
```text
## 💻 JavaScript интеграция

### AJAX операции

#### Добавление комментария

```javascript
// В article-detail.js
function submitComment(articleId, content, parentId = null) {
    fetch('/blog/ajax/add-comment/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({
            article_id: articleId,
            content: content,
            parent_id: parentId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Добавить комментарий в DOM
            appendComment(data.comment_html);
            updateCommentsCount(data.comments_count);
        }
    });
}
```text
#### Реакции (лайк/дизлайк)

```javascript
function toggleReaction(articleId, reactionType) {
    fetch('/blog/ajax/toggle-reaction/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({
            article_id: articleId,
            reaction_type: reactionType  // 'like' or 'dislike'
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateReactionCounts(data.likes_count, data.dislikes_count);
            highlightUserReaction(data.user_reaction);
        }
    });
}
```text
#### Прогресс чтения

```javascript
function initReadingProgress(articleId) {
    const content = document.querySelector('.article-content');
    const progressBar = document.querySelector('.reading-progress-bar');

    window.addEventListener('scroll', throttle(() => {
        const progress = calculateProgress(content);
        progressBar.style.width = `${progress}%`;

        // Сохранить прогресс на сервере
        if (progress % 10 === 0) {  // Каждые 10%
            saveProgress(articleId, progress);
        }
    }, 500));
}

function saveProgress(articleId, progress) {
    fetch('/blog/ajax/update-reading-progress/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({
            article_id: articleId,
            progress: progress
        })
    });
}
```text
## 📝 Примеры использования

### Кастомизация карточки статьи

```html
<!-- Своя карточка с дополнительными данными -->
<div class="custom-article-card">
    {% with article=my_article %}
        <a href="{{ article.get_absolute_url }}">
            <h3>{{ article.title }}</h3>
            <p>{{ article.excerpt|clean_markdown|truncatewords:20 }}</p>

            <!-- Теги -->
            <div class="tags">
                {% for tag in article.tags.all|slice:":3" %}
                <span class="tag">#{{ tag.name }}</span>
                {% endfor %}
            </div>

            <!-- Прогресс серии -->
            {% if article.series %}
            <div class="series-progress">
                Часть {{ article.series_order }} из {{ article.series.articles.count }}
            </div>
            {% endif %}
        </a>
    {% endwith %}
</div>
```text
### Фильтрация статей

```html
<form method="get" class="filters">
    <!-- Категории -->
    <select name="category">
        <option value="">Все категории</option>
        {% for category in categories %}
        <option value="{{ category.slug }}"
                {% if category.slug == current_category %}selected{% endif %}>
            {{ category.icon }} {{ category.name }}
        </option>
        {% endfor %}
    </select>

    <!-- Сложность -->
    <select name="difficulty">
        <option value="">Любая сложность</option>
        {% for value, label in difficulties %}
        <option value="{{ value }}"
                {% if value == current_difficulty %}selected{% endif %}>
            {{ label }}
        </option>
        {% endfor %}
    </select>

    <!-- Сортировка -->
    <select name="sort">
        <option value="latest" {% if current_sort == 'latest' %}selected{% endif %}>
            Последние
        </option>
        <option value="popular" {% if current_sort == 'popular' %}selected{% endif %}>
            Популярные
        </option>
        <option value="rated" {% if current_sort == 'rated' %}selected{% endif %}>
            Рейтинговые
        </option>
    </select>

    <button type="submit">Применить</button>
</form>
```text
### Адаптивная сетка статей

```html
<div class="articles-grid">
    <div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4">
        {% for article in articles %}
        <div class="col">
            {% include "blog/includes/article_card.html" with article=article %}
        </div>
        {% empty %}
        <div class="col-12">
            <p class="text-center">Статьи не найдены</p>
        </div>
        {% endfor %}
    </div>
</div>
```text
## 🎨 CSS классы

### Основные классы

- `.article-card` - Карточка статьи
- `.article-detail` - Контейнер детальной страницы
- `.comment-item` - Комментарий
- `.reaction-buttons` - Кнопки реакций
- `.reading-progress-bar` - Прогресс-бар чтения
- `.tags-cloud` - Облако тегов
- `.category-card` - Карточка категории

### Модификаторы

- `.featured` - Рекомендованная статья
- `.active` - Активная кнопка/фильтр
- `.edited` - Отредактированный комментарий
- `.pinned` - Закрепленная статья

## 🔗 Связанная документация

- **Template Tags**: См. `templatetags/README.md` - Кастомные фильтры (`clean_markdown`, `tag_size`, etc.)
- **Views**: См. `../README.md` - Документация представлений
- **Models**: См. `../README.md` - Модели данных
- **API**: См. `BLOG_API_DOCUMENTATION.md` - REST API

## 📚 Зависимости

- **Django Templates** - Jinja2 синтаксис
- **Bootstrap 5** - CSS фреймворк
- **Markdown** - Рендеринг контента (`markdown_extras`)
- **django-taggit** - Система тегов

---

**Статус**: ✅ Production Ready | 15 шаблонов | 🎨 Bootstrap 5 | 📱 Responsive
