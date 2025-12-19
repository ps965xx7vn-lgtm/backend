# Blog Template Tags

Кастомные теги и фильтры Django для шаблонов блога.

## 📋 Содержание

- [Обзор](#обзор)
- [Установка](#установка)
- [Фильтры](#фильтры)
- [Примеры использования](#примеры-использования)
- [Расширение](#расширение)

## 🎯 Обзор

Модуль `blog_extras.py` содержит кастомные template tags и фильтры для обработки и форматирования данных в шаблонах блога.

### Основные возможности

✅ Очистка Markdown от служебных символов
✅ Форматирование текста для превью
✅ Расчет динамических размеров элементов
✅ Обработка пользовательского контента

## 📁 Структура

```text
templatetags/
├── __init__.py          # Инициализация пакета
└── blog_extras.py       # Кастомные фильтры и теги
```text
## 🔧 Установка

### В шаблонах

Для использования фильтров добавьте в начало шаблона:

```django
{% load blog_extras %}
```text
### Пример

```html
{% load blog_extras %}

<div class="article-preview">
    <p>{{ article.content|clean_markdown|truncatewords:50 }}</p>
</div>
```text
## 🏷️ Фильтры

### clean_markdown

**Назначение**: Очищает текст от Markdown-символов для отображения в карточках и превью.

**Сигнатура**:

```python
@register.filter
def clean_markdown(text: str) -> str
```text
**Параметры**:

- `text` (str): Исходный текст с Markdown разметкой

**Возвращает**:

- `str`: Очищенный текст без Markdown символов

**Что удаляется**:

1. Заголовки (`# ## ###` и т.д.)
2. Жирный текст (`**text**`, `__text__`)
3. Курсив (`*text*`, `_text_`)
4. Ссылки (`[text](url)` → `text`)
5. Инлайн код (`` `code` ``)
6. Блоки кода (`` ```code``` ``)
7. Цитаты (`> quote`)
8. Списки (`- item`, `* item`, `+ item`, `1. item`)
9. Горизонтальные линии (`---`)
10. Лишние пробелы и переносы строк

**Пример использования**:

```django
<!-- Исходный контент статьи -->
{{ article.content }}
<!--

# Заголовок

Это **жирный** текст и *курсив*.

- Список
- Элементов

[Ссылка](http://example.com)

```python

def hello():
    print("Hello")

```text
-->

<!-- После применения фильтра -->
{{ article.content|clean_markdown }}
<!--
Заголовок

Это жирный текст и курсив.

Список
Элементов

Ссылка

def hello(): print("Hello")
-->
```text
**Практическое применение**:

```django
<!-- 1. Превью статьи в карточке -->
<div class="article-card">
    <p class="excerpt">
        {{ article.content|clean_markdown|truncatewords:30 }}
    </p>
</div>

<!-- 2. Meta description для SEO -->
<meta name="description" content="{{ article.excerpt|clean_markdown|truncatewords:25 }}">

<!-- 3. Open Graph описание -->
<meta property="og:description" content="{{ article.content|clean_markdown|truncatewords:40 }}">

<!-- 4. Список комментариев -->
<div class="comment-preview">
    {{ comment.content|clean_markdown|truncatewords:20 }}
</div>

<!-- 5. Поисковые результаты -->
<div class="search-result">
    <p>{{ article.content|clean_markdown|truncatewords:50 }}</p>
</div>
```text
**Детальная реализация**:

```python
@register.filter
def clean_markdown(text):
    """
    Очищает текст от Markdown-символов для отображения в превью карточек.
    Удаляет заголовки (#), жирный текст (**), курсив (*), ссылки и другие символы.
    """
    if not text:
        return text

    # Удаляем заголовки (# ## ### и т.д.)

    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)

    # Удаляем жирный текст (**text** или __text__)

    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'__(.*?)__', r'\1', text)

    # Удаляем курсив (*text* или _text_)

    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'_(.*?)_', r'\1', text)

    # Удаляем ссылки [text](url)

    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)

    # Удаляем инлайн код `code`

    text = re.sub(r'`([^`]+)`', r'\1', text)

    # Удаляем блоки кода ```

    text = re.sub(r'```[\s\S]*?```', '', text)

    # Удаляем цитаты (>)

    text = re.sub(r'^>\s*', '', text, flags=re.MULTILINE)

    # Удаляем списки (- * +)

    text = re.sub(r'^[\s]*[-\*\+]\s+', '', text, flags=re.MULTILINE)

    # Удаляем нумерованные списки

    text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE)

    # Удаляем горизонтальные линии

    text = re.sub(r'^---+\s*$', '', text, flags=re.MULTILINE)

    # Удаляем лишние пробелы и переносы строк

    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()

    return text
```text
## 📝 Примеры использования

### 1. Карточки статей

```django
{% load blog_extras %}

<div class="article-card">
    <h3>{{ article.title }}</h3>

    <!-- Очищенное превью -->
    <p class="excerpt">
        {{ article.content|clean_markdown|truncatewords:50 }}
    </p>

    <!-- Метаданные -->
    <div class="meta">
        <span>{{ article.reading_time }} мин чтения</span>
        <span>{{ article.views_count }} просмотров</span>
    </div>
</div>
```text
### 2. SEO теги

```django
{% load blog_extras %}

<!-- Meta description -->
<meta name="description" content="{{ article.excerpt|clean_markdown|truncatewords:25 }}">

<!-- Open Graph -->
<meta property="og:title" content="{{ article.title }}">
<meta property="og:description" content="{{ article.excerpt|clean_markdown|truncatewords:30 }}">

<!-- Twitter Card -->
<meta name="twitter:description" content="{{ article.excerpt|clean_markdown|truncatewords:30 }}">
```text
### 3. Список комментариев

```django
{% load blog_extras %}

<div class="comments-list">
    {% for comment in comments %}
    <div class="comment">
        <div class="author">{{ comment.author.username }}</div>
        <div class="content">
            <!-- Показываем превью, полный текст по клику -->
            <p class="preview">
                {{ comment.content|clean_markdown|truncatewords:30 }}
            </p>
            <button class="show-more">Показать полностью</button>
        </div>
    </div>
    {% endfor %}
</div>
```text
### 4. Результаты поиска

```django
{% load blog_extras %}

<div class="search-results">
    {% for article in results %}
    <div class="result-item">
        <h4>{{ article.title }}</h4>
        <p class="snippet">
            {{ article.content|clean_markdown|truncatewords:60 }}
        </p>
        <a href="{{ article.get_absolute_url }}">Читать далее →</a>
    </div>
    {% endfor %}
</div>
```text
### 5. Email рассылка

```django
{% load blog_extras %}

<div class="email-digest">
    <h2>Новые статьи на PySchool</h2>

    {% for article in new_articles %}
    <div class="article-preview">
        <h3>{{ article.title }}</h3>
        <p>{{ article.content|clean_markdown|truncatewords:40 }}</p>
        <a href="{{ article.get_absolute_url }}">Читать статью</a>
    </div>
    {% endfor %}
</div>
```text
### 6. Мобильное отображение

```django
{% load blog_extras %}

<!-- Компактный вид для мобильных -->
<div class="mobile-article-list">
    {% for article in articles %}
    <div class="mobile-item">
        <h4>{{ article.title|truncatewords:8 }}</h4>
        <p>{{ article.content|clean_markdown|truncatewords:15 }}</p>
        <a href="{{ article.get_absolute_url }}">→</a>
    </div>
    {% endfor %}
</div>
```text
### 7. Социальные сети

```django
{% load blog_extras %}

<!-- Кнопка Share для Twitter -->
<a href="<https://twitter.com/intent/tweet?text={{> article.title|urlencode }}&url={{ request.build_absolute_uri }}"
   target="_blank"
   class="share-twitter">
    Твитнуть
</a>

<!-- LinkedIn Share с описанием -->
<a href="<https://www.linkedin.com/sharing/share-offsite/?url={{> request.build_absolute_uri }}"
   target="_blank"
   class="share-linkedin">
    Поделиться в LinkedIn
</a>

<!-- WhatsApp Share -->
<a href="<https://wa.me/?text={{> article.title|urlencode }}%20{{ request.build_absolute_uri|urlencode }}"
   target="_blank"
   class="share-whatsapp">
    Отправить в WhatsApp
</a>
```text
## 🔧 Расширение функциональности

### Добавление новых фильтров

Чтобы добавить свой фильтр в `blog_extras.py`:

```python
from django import template
import re

register = template.Library()

@register.filter
def word_count(text):
    """
    Подсчитывает количество слов в тексте.

    Usage:
        {{ article.content|word_count }}
    """
    if not text:
        return 0
    return len(text.split())

@register.filter
def reading_time_detailed(text):
    """
    Расчет времени чтения с учетом изображений и кода.

    Usage:
        {{ article.content|reading_time_detailed }}
    """
    if not text:
        return 0

    # 200 слов в минуту

    words = len(text.split())
    minutes = words / 200

    # +12 секунд за каждое изображение

    images = text.count('![')
    minutes += (images * 12) / 60

    # +10 секунд за каждый блок кода

    code_blocks = text.count('```')
    minutes += (code_blocks * 10) / 60

    return max(1, round(minutes))

@register.filter
def tag_size(usage_count, min_size=12, max_size=32):
    """
    Вычисляет размер шрифта для облака тегов.

    Usage:
        <span style="font-size: {{ tag.usage_count|tag_size }}px">
    """

    # Нормализация от min_size до max_size

    # В зависимости от usage_count

    return min_size + (usage_count * (max_size - min_size) / 100)

@register.filter
def excerpt_smart(text, length=100):
    """
    Умное сокращение текста до ближайшего предложения.

    Usage:
        {{ article.content|clean_markdown|excerpt_smart:150 }}
    """
    if not text or len(text) <= length:
        return text

    # Обрезать по длине

    truncated = text[:length]

    # Найти ближайшую точку

    last_period = truncated.rfind('.')
    if last_period > length * 0.7:  # Если точка не слишком далеко
        return truncated[:last_period + 1]

    # Иначе обрезать по слову

    last_space = truncated.rfind(' ')
    return truncated[:last_space] + '...'

@register.filter
def highlight_search(text, query):
    """
    Подсвечивает поисковые запросы в тексте.

    Usage:
        {{ article.title|highlight_search:search_query }}
    """
    if not query:
        return text

    pattern = re.compile(re.escape(query), re.IGNORECASE)
    return pattern.sub(r'<mark>\g<0></mark>', text)
```text
### Использование новых фильтров

```django
{% load blog_extras %}

<!-- Количество слов -->
<span class="word-count">{{ article.content|word_count }} слов</span>

<!-- Детальное время чтения -->
<span class="reading-time">⏱️ {{ article.content|reading_time_detailed }} мин</span>

<!-- Облако тегов с динамическими размерами -->
<div class="tags-cloud">
    {% for tag in tags %}
    <a href="{% url 'blog:tag_detail' tag.slug %}"
       style="font-size: {{ tag.usage_count|tag_size:14:28 }}px">

        #{{ tag.name }}

    </a>
    {% endfor %}
</div>

<!-- Умное сокращение текста -->
<p class="smart-excerpt">
    {{ article.content|clean_markdown|excerpt_smart:200 }}
</p>

<!-- Подсветка поискового запроса -->
<h3>{{ article.title|highlight_search:query|safe }}</h3>
<p>{{ article.excerpt|clean_markdown|highlight_search:query|safe }}</p>
```text
## 🧪 Тестирование фильтров

Создайте тесты в `tests/test_templatetags.py`:

```python
import pytest
from django.template import Template, Context
from blog.templatetags.blog_extras import clean_markdown

class TestCleanMarkdown:
    """Тесты для фильтра clean_markdown"""

    def test_removes_headers(self):
        """Удаляет заголовки Markdown"""
        text = "# Заголовок\n\nТекст"
        result = clean_markdown(text)
        assert result == "Заголовок Текст"

    def test_removes_bold(self):
        """Удаляет жирный текст"""
        text = "Это **жирный** текст"
        result = clean_markdown(text)
        assert result == "Это жирный текст"

    def test_removes_italic(self):
        """Удаляет курсив"""
        text = "Это *курсивный* текст"
        result = clean_markdown(text)
        assert result == "Это курсивный текст"

    def test_removes_links(self):
        """Удаляет ссылки, оставляя текст"""
        text = "[Текст ссылки](http://example.com)"
        result = clean_markdown(text)
        assert result == "Текст ссылки"

    def test_removes_code_blocks(self):
        """Удаляет блоки кода"""
        text = "Текст\n```python\nprint('hello')\n```\nЕще текст"
        result = clean_markdown(text)
        assert "print" not in result

    def test_removes_lists(self):
        """Удаляет маркеры списков"""
        text = "- Элемент 1\n- Элемент 2"
        result = clean_markdown(text)
        assert result == "Элемент 1 Элемент 2"

    def test_handles_empty_text(self):
        """Обрабатывает пустой текст"""
        assert clean_markdown(None) is None
        assert clean_markdown("") == ""

    def test_in_template(self):
        """Тест использования в шаблоне"""
        template = Template("{% load blog_extras %}{{ text|clean_markdown }}")
        context = Context({'text': "# Заголовок\n\n**Жирный** текст"})
        result = template.render(context)
        assert result == "Заголовок Жирный текст"
```text
Запуск тестов:

```bash
pytest src/blog/tests/test_templatetags.py -v
```text
## 📚 Документация Django Template Tags

### Официальная документация

- [Custom template tags and filters](https://docs.djangoproject.com/en/5.1/howto/custom-template-tags/)
- [Template filter reference](https://docs.djangoproject.com/en/5.1/ref/templates/builtins/#built-in-filter-reference)

### Best Practices

1. **Именование**: Используйте понятные имена фильтров (`clean_markdown` лучше, чем `cm`)
2. **Документация**: Добавляйте docstrings ко всем фильтрам
3. **Обработка ошибок**: Всегда проверяйте входные данные (None, пустые строки)
4. **Производительность**: Избегайте тяжелых операций в фильтрах (они выполняются при каждом рендере)
5. **Тестирование**: Покрывайте фильтры юнит-тестами

### Полезные встроенные фильтры Django

Часто используемые вместе с `clean_markdown`:

```django
<!-- Обрезка текста -->
{{ text|clean_markdown|truncatewords:30 }}
{{ text|clean_markdown|truncatechars:100 }}

<!-- Форматирование -->
{{ text|clean_markdown|title }}
{{ text|clean_markdown|capfirst }}
{{ text|clean_markdown|lower }}
{{ text|clean_markdown|upper }}

<!-- URL encoding -->
{{ text|clean_markdown|urlencode }}

<!-- HTML escape (для безопасности) -->
{{ text|clean_markdown|escape }}

<!-- Linebreaks (превращает \n в <br>) -->
{{ text|clean_markdown|linebreaks }}
{{ text|clean_markdown|linebreaksbr }}

<!-- Default значения -->
{{ text|clean_markdown|default:"Нет описания" }}

<!-- Длина -->
{{ text|clean_markdown|length }}

<!-- Безопасный вывод HTML -->
{{ text|clean_markdown|safe }}
```text
## 🔗 Связанная документация

- **Templates**: См. `templates/README.md` - Использование в шаблонах
- **Models**: См. `../README.md` - Модели данных (Article, Comment)
- **Views**: См. `../README.md` - Context переменные для шаблонов

---

**Статус**: ✅ Production Ready | 1 фильтр | 🧪 Протестировано | 📝 Документировано
