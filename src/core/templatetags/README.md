# Core Template Tags

Custom template tags и filters для приложения core.

## 🎯 Обзор

В папке `templatetags/` находятся пользовательские template tags для
расширения функциональности Django шаблонов.

**Модули:**

- `markdown_filters.py` - фильтры для работы с Markdown
- `article_tags.py` - теги для работы со статьями блога

---

## 📝 markdown_filters.py

Фильтры для конвертации и обработки Markdown контента в шаблонах.

### Регистрация

```python
from django import template
from django.utils.safestring import mark_safe
import markdown
import re

register = template.Library()
```text
---

### Фильтры

#### `markdown_format`

Конвертирует Markdown текст в HTML с поддержкой расширений.

**Signature:**

```python
@register.filter(name='markdown_format')
def markdown_format(text: Optional[str]) -> SafeString
```text
**Параметры:**

- `text` (str | None) - Markdown текст для конвертации

**Возвращает:**

- `SafeString` - HTML код, безопасный для вывода

**Markdown расширения:**

- `extra` - таблицы, footnotes, fenced code blocks
- `codehilite` - подсветка синтаксиса кода
- `toc` - генерация Table of Contents
- `nl2br` - конвертация переносов строк в `<br>`
- `sane_lists` - улучшенная обработка списков

**Использование:**

```django
{% load markdown_filters %}

<div class="article-content">
    {{ article.content|markdown_format|safe }}
</div>
```text
**Входной Markdown:**

```markdown

## Заголовок

Параграф с **жирным** и *курсивом*.

```python

def hello():
    print("Hello, World!")

```text
- Пункт 1
- Пункт 2

```text
**Выходной HTML:**

```html
<h2>Заголовок</h2>
<p>Параграф с <strong>жирным</strong> и <em>курсивом</em>.</p>
<div class="codehilite">
    <pre><code class="language-python">def hello():
    print("Hello, World!")
</code></pre>
</div>
<ul>
    <li>Пункт 1</li>
    <li>Пункт 2</li>
</ul>
```text
---

#### `get_item`

Получает элемент из словаря по ключу (аналог `dict[key]` в Python).

**Signature:**

```python
@register.filter(name='get_item')
def get_item(dictionary: dict, key: str) -> Any
```text
**Параметры:**

- `dictionary` (dict) - Словарь
- `key` (str) - Ключ

**Возвращает:**

- `Any` - Значение из словаря или `None`

**Использование:**

```django
{% load markdown_filters %}

<!-- В контексте: stats = {'students': 100, 'courses': 10} -->
<p>Студентов: {{ stats|get_item:"students" }}</p>
<p>Курсов: {{ stats|get_item:"courses" }}</p>
```text
**Выход:**

```html
<p>Студентов: 100</p>
<p>Курсов: 10</p>
```text
---

#### `clean_markdown`

Удаляет всю Markdown разметку, оставляя только чистый текст.

**Signature:**

```python
@register.filter(name='clean_markdown')
def clean_markdown(text: Optional[str]) -> str
```text
**Параметры:**

- `text` (str | None) - Текст с Markdown разметкой

**Возвращает:**

- `str` - Чистый текст без разметки

**Удаляет:**

- Заголовки (`#`, `##`, etc.)
- Жирный текст (`**text**`)
- Курсив (`*text*`, `_text_`)
- Ссылки (`[text](url)`)
- Блоки кода (` ``` `)
- Inline код (`` `code` ``)
- Списки (`-`, `*`, `1.`)
- Цитаты (`>`)

**Использование:**

```django
{% load markdown_filters %}

<!-- Для meta description без HTML тегов -->
<meta name="description" content="{{ article.content|clean_markdown|truncatewords:30 }}">
```text
**Пример:**

```python

# Входной текст

"## Заголовок\n\nТекст с **жирным** и *курсивом*.\n\n```python\ncode\n```"

# Выходной текст

"Заголовок Текст с жирным и курсивом."
```text
---

#### `smart_excerpt`

Создает умную выдержку из текста (excerpt) с учетом предложений.

**Signature:**

```python
@register.filter(name='smart_excerpt')
def smart_excerpt(text: Optional[str], length: int = 150) -> str
```text
**Параметры:**

- `text` (str | None) - Исходный текст
- `length` (int) - Максимальная длина (default: 150)

**Возвращает:**

- `str` - Выдержка с добавлением "..." если текст обрезан

**Логика:**

1. Очищает Markdown разметку
2. Обрезает до `length` символов
3. Ищет последнюю точку/восклицательный/вопросительный знак
4. Обрезает по последнему предложению
5. Добавляет "..." если текст был обрезан

**Использование:**

```django
{% load markdown_filters %}

<!-- Карточка статьи с кратким описанием -->
<div class="article-card">
    <h3>{{ article.title }}</h3>
    <p>{{ article.content|smart_excerpt:200 }}</p>
    <a href="{{ article.get_absolute_url }}">Читать далее →</a>
</div>
```text
**Пример:**

```python

# Входной текст (300 символов)

"Это первое предложение. Это второе предложение с подробностями. Это третье предложение, которое будет обрезано."

# Выход при length=100

"Это первое предложение. Это второе предложение с подробностями..."
```text
---

## 📊 article_tags.py

Template tags для работы со статьями блога (используются в core для отображения статистики).

### Регистрация

```python
from django import template

register = template.Library()
```text
---

### Фильтры

#### `pluralize_articles`

Склоняет слово "статья" в зависимости от количества (русский язык).

**Signature:**

```python
@register.filter(name='pluralize_articles')
def pluralize_articles(count: int) -> str
```text
**Параметры:**

- `count` (int) - Количество статей

**Возвращает:**

- `str` - Правильная форма слова ("статья", "статьи" или "статей")

**Логика склонения:**

- Числа, заканчивающиеся на 1 (кроме 11): "статья" (1, 21, 31, ...)
- Числа, заканчивающиеся на 2-4 (кроме 12-14): "статьи" (2, 3, 4, 22, 23, ...)
- Все остальные: "статей" (5-20, 25-30, ...)

**Использование:**

```django
{% load article_tags %}

<p>Найдено: {{ count }} {{ count|pluralize_articles }}</p>
```text
**Примеры вывода:**

```html
1 статья
2 статьи
3 статьи
4 статьи
5 статей
10 статей
11 статей
21 статья
22 статьи
25 статей
100 статей
101 статья
```text
**Код функции:**

```python
def pluralize_articles(count: int) -> str:
    """
    Склонение слова "статья" в зависимости от количества.

    Args:
        count: Количество статей

    Returns:
        Правильная форма слова
    """
    if count % 10 == 1 and count % 100 != 11:
        return "статья"
    elif count % 10 in [2, 3, 4] and count % 100 not in [12, 13, 14]:
        return "статьи"
    else:
        return "статей"
```text
---

## 🔧 Использование

### Загрузка в шаблоне

```django
{% load markdown_filters %}
{% load article_tags %}
```text
### Комбинирование фильтров

```django
<!-- Markdown → HTML → обрезка → safe -->
{{ article.content|markdown_format|truncatewords_html:50|safe }}

<!-- Очистка Markdown → обрезка для meta description -->
<meta name="description" content="{{ article.content|clean_markdown|truncatewords:30 }}">

<!-- Умная выдержка без HTML -->
<p class="excerpt">{{ article.content|smart_excerpt:200 }}</p>
```text
---

## 💡 Примеры

### 1. Блог статья с Markdown

```django
{% extends "base.html" %}
{% load markdown_filters %}

{% block content %}
<article class="blog-post">
    <h1>{{ article.title }}</h1>
    <div class="article-meta">
        <span>{{ article.created_at|date:"d.m.Y" }}</span>
        <span>{{ article.reading_time }} мин</span>
    </div>

    <!-- Markdown контент с подсветкой кода -->
    <div class="article-content">
        {{ article.content|markdown_format|safe }}
    </div>
</article>
{% endblock %}
```text
---

### 2. Карточки статей со smart excerpt

```django
{% load markdown_filters %}
{% load article_tags %}

<div class="articles-grid">
    {% for article in articles %}
    <div class="article-card">
        <h3>{{ article.title }}</h3>

        <!-- Умная выдержка -->
        <p class="excerpt">
            {{ article.content|smart_excerpt:150 }}
        </p>

        <div class="card-footer">
            <span>{{ article.views }} просмотров</span>
            <a href="{{ article.get_absolute_url }}">Читать →</a>
        </div>
    </div>
    {% endfor %}
</div>

<!-- Всего статей с правильным склонением -->
<p class="total">
    Всего: {{ articles.count }} {{ articles.count|pluralize_articles }}
</p>
```text
---

### 3. SEO meta-теги

```django
{% load markdown_filters %}

{% block extra_meta %}
<!-- Open Graph -->
<meta property="og:title" content="{{ article.title }}">
<meta property="og:description" content="{{ article.content|clean_markdown|truncatewords:25 }}">
<meta property="og:type" content="article">

<!-- Twitter Card -->
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{{ article.title }}">
<meta name="twitter:description" content="{{ article.content|smart_excerpt:160 }}">

<!-- Standard Meta -->
<meta name="description" content="{{ article.content|clean_markdown|truncatewords:30 }}">
{% endblock %}
```text
---

### 4. Статистика со склонениями

```django
{% load article_tags %}

<div class="stats-grid">
    <div class="stat-item">
        <span class="number">{{ stats.articles_count }}</span>
        <span class="label">{{ stats.articles_count|pluralize_articles }}</span>
    </div>

    <div class="stat-item">
        <span class="number">{{ stats.students_count }}</span>
        <span class="label">
            {{ stats.students_count|pluralize:"студент,студента,студентов" }}
        </span>
    </div>
</div>
```text
---

### 5. Работа со словарями

```django
{% load markdown_filters %}

<!-- stats = {'python': 50, 'javascript': 30, 'django': 20} -->
<ul class="tech-stats">
    {% for tech in tech_list %}
    <li>
        <strong>{{ tech|title }}</strong>:
        {{ stats|get_item:tech }} {{ stats|get_item:tech|pluralize_articles }}
    </li>
    {% endfor %}
</ul>
```text
---

## 🧪 Тестирование

### Юнит тесты для фильтров

```python
from django.test import TestCase
from django.template import Context, Template

class MarkdownFiltersTestCase(TestCase):
    def test_markdown_format_basic(self):
        template = Template("{% load markdown_filters %}{{ text|markdown_format }}")
        context = Context({'text': '**bold** *italic*'})
        output = template.render(context)
        self.assertIn('<strong>bold</strong>', output)
        self.assertIn('<em>italic</em>', output)

    def test_clean_markdown(self):
        template = Template("{% load markdown_filters %}{{ text|clean_markdown }}")
        context = Context({'text': '## Heading\n\n**Bold** text'})
        output = template.render(context)
        self.assertEqual(output.strip(), 'Heading Bold text')

    def test_smart_excerpt(self):
        template = Template("{% load markdown_filters %}{{ text|smart_excerpt:50 }}")
        text = "First sentence. Second sentence. Third sentence."
        context = Context({'text': text})
        output = template.render(context)
        self.assertIn('First sentence', output)
        self.assertIn('...', output)

class ArticleTagsTestCase(TestCase):
    def test_pluralize_articles(self):
        template = Template("{% load article_tags %}{{ count|pluralize_articles }}")

        # 1 статья

        self.assertEqual(
            Template("{% load article_tags %}{{ count|pluralize_articles }}")
            .render(Context({'count': 1})),
            'статья'
        )

        # 2 статьи

        self.assertEqual(
            Template("{% load article_tags %}{{ count|pluralize_articles }}")
            .render(Context({'count': 2})),
            'статьи'
        )

        # 5 статей

        self.assertEqual(
            Template("{% load article_tags %}{{ count|pluralize_articles }}")
            .render(Context({'count': 5})),
            'статей'
        )
```text
---

## 📚 Связанная документация

- [Django Template Tags Documentation](https://docs.djangoproject.com/en/stable/howto/custom-template-tags/)
- [Python Markdown Library](https://python-markdown.github.io/)
- [Templates README](../templates/README.md)
- [Views Documentation](../views.py)

---

## 🤝 Добавление новых фильтров

При создании нового фильтра:

1. ✅ Добавьте docstring с описанием параметров
2. ✅ Используйте type hints для всех аргументов
3. ✅ Обрабатывайте `None` и пустые значения
4. ✅ Добавьте юнит тесты
5. ✅ Обновите этот README с примерами использования

**Пример нового фильтра:**

```python
@register.filter(name='my_custom_filter')
def my_custom_filter(value: Optional[str], arg: str = 'default') -> str:
    """
    Краткое описание фильтра.

    Args:
        value: Входное значение
        arg: Дополнительный параметр

    Returns:
        Обработанное значение

    Example:
        {{ text|my_custom_filter:"argument" }}
    """
    if not value:
        return ''

    # Ваша логика здесь

    return processed_value
```text
