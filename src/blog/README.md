# Blog Application

Полнофункциональное приложение блога для Django с REST API, кешированием,
SEO оптимизацией и системой комментариев.

## 🎯 Обзор

Приложение `blog` - это комплексная система управления контентом с поддержкой:

- **Статьи**: Markdown контент, категории, теги, серии, сложность
- **Комментарии**: Вложенные комментарии с реакциями (лайки/дизлайки)
- **Взаимодействие**: Реакции на статьи, закладки, прогресс чтения
- **REST API**: 12 эндпоинтов с автодокументацией (Django Ninja)
- **SEO**: Мета-теги, sitemap, Open Graph, schema.org
- **Производительность**: Redis кеширование, оптимизированные запросы
- **Безопасность**: Rate limiting, CSRF защита, валидация данных

### Основные возможности

✅ Публикация статей с Markdown разметкой
✅ Категории, теги, серии статей
✅ Система комментариев с вложенностью до 3 уровней
✅ Реакции (лайки/дизлайки) на статьи и комментарии
✅ Закладки и прогресс чтения
✅ Полнотекстовый поиск (PostgreSQL)
✅ Фильтрация по категориям, тегам, сложности, авторам
✅ Подписка на email рассылку
✅ Система рейтингов и просмотров
✅ SEO оптимизация (meta, sitemap, schema.org)
✅ REST API для всех операций
✅ Админ панель с массовыми операциями
✅ 149 юнит тестов (75% покрытие кода)

## 📁 Структура приложения

```text
blog/
├── __init__.py              # Пакет приложения
├── admin.py                 # Django Admin конфигурация (11 админ классов)
├── api.py                   # REST API эндпоинты (12 endpoints)
├── apps.py                  # Конфигурация приложения
├── cache_utils.py           # Redis кеширование (8 функций)
├── forms.py                 # Django формы (CommentForm)
├── middleware.py            # Rate limiting middleware
├── models.py                # Модели данных (11 моделей, 1839 строк)
├── schemas.py               # Pydantic схемы для API
├── tasks.py                 # Celery задачи (5 фоновых задач)
├── urls.py                  # URL маршруты (15 URL patterns)
├── views.py                 # Django представления (24 views, 2994 строки)
├── management/
│   └── commands/
│       └── generate_sitemap.py  # Команда генерации sitemap.xml
├── migrations/              # Миграции базы данных
├── templates/               # HTML шаблоны (см. templates/README.md)
├── templatetags/            # Custom template tags (см. templatetags/README.md)
└── tests/                   # Юнит тесты (см. tests/README.md)
```text
## 🗄️ Модели данных

### Основные модели

#### 1. **Category** (Категория)

Категории для организации статей.

```python

# Поля

name: CharField(max_length=100, unique=True)  # Название
slug: SlugField(unique=True)                  # URL-slug
description: TextField(blank=True)            # Описание
icon: CharField(default="📝")                 # Иконка (emoji)
color: CharField(default="#3498db")           # Цвет (HEX)
tag_keywords: TextField(blank=True)           # Ключевые слова
badge: CharField(blank=True)                  # Бейдж для отображения
order: PositiveIntegerField(default=0)        # Порядок сортировки

# Методы

get_absolute_url() -> str                     # URL категории
__str__() -> str                              # Название категории
```text
**Примеры использования:**

```python

# Получить все категории с количеством статей

categories = Category.objects.annotate(
    published_count=Count('articles', filter=Q(articles__status='published'))
)

# Получить статьи категории

python_category = Category.objects.get(slug='python')
articles = python_category.articles.filter(status='published')
```text
#### 2. **Article** (Статья)

Основная модель для статей блога.

```python

# Основные поля

title: CharField(max_length=200)              # Заголовок
slug: SlugField(unique=True)                  # URL-slug
content: TextField()                          # Markdown контент
excerpt: TextField(blank=True)                # Краткое описание
category: ForeignKey(Category)                # Категория
blog_author: ForeignKey(Author, null=True)    # Автор блога
author: ForeignKey(User, null=True)           # Автор (User)
series: ForeignKey(Series, null=True)         # Серия статей
difficulty: CharField(choices=DIFFICULTY)     # Сложность
status: CharField(choices=STATUS)             # Статус (draft/published/archived)

# SEO поля

meta_title: CharField(max_length=60)          # SEO заголовок
meta_description: CharField(max_length=160)   # SEO описание
meta_keywords: TextField()                    # Ключевые слова
featured_image: ImageField()                  # Главное изображение

# Флаги

is_featured: BooleanField(default=False)      # Рекомендованная
allow_comments: BooleanField(default=True)    # Комментарии
is_pinned: BooleanField(default=False)        # Закреплена

# Статистика

views_count: PositiveIntegerField(default=0)  # Просмотры
reading_time: PositiveIntegerField(default=0) # Время чтения (мин)
likes_count: PositiveIntegerField(default=0)  # Лайки
dislikes_count: PositiveIntegerField(default=0) # Дизлайки

# Даты

published_at: DateTimeField(null=True)        # Дата публикации
created_at: DateTimeField(auto_now_add=True)  # Дата создания
updated_at: DateTimeField(auto_now=True)      # Дата обновления

# Связи

tags: TaggableManager()                       # Теги (django-taggit)

# Методы

get_absolute_url() -> str                     # URL статьи
increment_views() -> None                     # +1 просмотр
update_reading_time() -> None                 # Пересчет времени чтения
get_related_articles(limit=5) -> QuerySet     # Похожие статьи
get_reactions_count() -> dict                 # Подсчет реакций
```text
**Примеры использования:**

```python

# Получить опубликованные статьи с оптимизацией

articles = Article.objects.filter(
    status='published',
    published_at__lte=timezone.now()
).select_related('category', 'blog_author', 'author').prefetch_related('tags')

# Создать статью

article = Article.objects.create(
    title='Введение в Python',
    slug='intro-python',
    content='# Python\n\nПримеры кода...',
    category=python_category,
    difficulty='beginner',
    status='draft'
)
article.update_reading_time()  # Автоматический расчет

# Получить похожие статьи

related = article.get_related_articles(limit=5)

# Увеличить просмотры

article.increment_views()
```text
#### 3. **Comment** (Комментарий)

Вложенные комментарии к статьям.

```python

# Поля

article: ForeignKey(Article)                  # Статья
author: ForeignKey(User)                      # Автор
content: TextField(validators=[MinLength(3)]) # Текст (мин 3 символа)
parent: ForeignKey('self', null=True)         # Родительский комментарий
created_at: DateTimeField(auto_now_add=True)  # Дата создания
updated_at: DateTimeField(auto_now=True)      # Дата изменения
is_approved: BooleanField(default=True)       # Одобрен
is_edited: BooleanField(default=False)        # Отредактирован
likes_count: PositiveIntegerField(default=0)  # Лайки
dislikes_count: PositiveIntegerField(default=0) # Дизлайки

# Методы

get_depth() -> int                            # Уровень вложенности (0-2)
can_reply() -> bool                           # Можно ли ответить (depth < 2)
get_replies() -> QuerySet                     # Получить ответы
clean() -> None                               # Валидация (макс 3 уровня)
```text
**Примеры использования:**

```python

# Создать комментарий

comment = Comment.objects.create(
    article=article,
    author=user,
    content='Отличная статья!'
)

# Создать ответ (макс 3 уровня)

reply = Comment.objects.create(
    article=article,
    author=another_user,
    content='Согласен!',
    parent=comment
)

# Получить все комментарии статьи

comments = article.comments.filter(
    parent=None,  # Только корневые
    is_approved=True
).select_related('author').order_by('-created_at')

# Проверить возможность ответа

if comment.can_reply():

    # Можно создать ответ

    pass
```text
#### 4. **Series** (Серия статей)

Объединение статей в серии.

```python

# Поля

title: CharField(max_length=200)              # Название серии
slug: SlugField(unique=True)                  # URL-slug
description: TextField()                      # Описание
created_at: DateTimeField(auto_now_add=True)
updated_at: DateTimeField(auto_now=True)

# Методы

get_absolute_url() -> str                     # URL серии
get_articles() -> QuerySet                    # Статьи в порядке
```text
#### 5. **ArticleReaction** (Реакция на статью)

Лайки/дизлайки на статьи.

```python

# Поля

article: ForeignKey(Article)                  # Статья
user: ForeignKey(User)                        # Пользователь
reaction_type: CharField(choices=['like', 'dislike']) # Тип реакции
created_at: DateTimeField(auto_now_add=True)

# Ограничения

unique_together = ['article', 'user']         # Одна реакция на статью
```text
#### 6. **Bookmark** (Закладка)

Сохраненные статьи пользователя.

```python

# Поля

article: ForeignKey(Article)                  # Статья
user: ForeignKey(User)                        # Пользователь
created_at: DateTimeField(auto_now_add=True)

# Ограничения

unique_together = ['article', 'user']         # Одна закладка
```text
#### 7. **ReadingProgress** (Прогресс чтения)

Отслеживание прогресса чтения статей.

```python

# Поля

article: ForeignKey(Article)                  # Статья
user: ForeignKey(User)                        # Пользователь
progress: PositiveIntegerField(default=0)     # Прогресс (0-100%)
last_position: PositiveIntegerField(default=0) # Последняя позиция
updated_at: DateTimeField(auto_now=True)

# Ограничения

unique_together = ['article', 'user']
```text
#### 8. **Newsletter** (Подписка на рассылку)

Email подписки на обновления блога.

```python

# Поля

email: EmailField(unique=True)                # Email подписчика
is_active: BooleanField(default=True)         # Активна ли подписка
subscribed_at: DateTimeField(auto_now_add=True)
unsubscribed_at: DateTimeField(null=True)

# Методы

unsubscribe() -> None                         # Отписаться
```text
#### 9. **Author** (Автор блога)

Профили авторов для блога.

```python

# Поля

user: OneToOneField(User)                     # Связь с User
bio: TextField(blank=True)                    # Биография
avatar: ImageField(blank=True)                # Аватар
website: URLField(blank=True)                 # Сайт
github: CharField(blank=True)                 # GitHub username
twitter: CharField(blank=True)                # Twitter handle
linkedin: URLField(blank=True)                # LinkedIn

# Методы

get_absolute_url() -> str                     # URL профиля автора
get_articles_count() -> int                   # Количество статей
```text
#### 10. **ArticleView** (Просмотр статьи)

Детальная аналитика просмотров.

```python

# Поля

article: ForeignKey(Article)                  # Статья
user: ForeignKey(User, null=True)             # Пользователь (если авторизован)
ip_address: GenericIPAddressField()           # IP адрес
user_agent: TextField()                       # User Agent
viewed_at: DateTimeField(auto_now_add=True)   # Время просмотра
```text
#### 11. **ArticleReport** (Жалоба на статью)

Система жалоб на неприемлемый контент.

```python

# Поля

article: ForeignKey(Article)                  # Статья
user: ForeignKey(User)                        # Отправитель жалобы
reason: CharField(choices=REPORT_REASONS)     # Причина
description: TextField(blank=True)            # Подробное описание
status: CharField(choices=STATUS_CHOICES)     # Статус (pending/reviewed/rejected)
created_at: DateTimeField(auto_now_add=True)
reviewed_at: DateTimeField(null=True)
reviewed_by: ForeignKey(User, null=True)      # Кто рассмотрел
```text
### Связи между моделями

```text
Category (1) ─────── (*) Article (1) ─────── (*) Comment
                           │                       │
                           │                       └─── (self) parent
                           │
                           ├─────── (*) ArticleReaction
                           │
                           ├─────── (*) Bookmark
                           │
                           ├─────── (*) ReadingProgress
                           │
                           ├─────── (*) ArticleView
                           │
                           └─────── (*) ArticleReport

Series (1) ──────── (*) Article

Author (1) ──────── (*) Article

User (1) ──────────┬─── (*) Comment
                   ├─── (*) ArticleReaction
                   ├─── (*) Bookmark
                   ├─── (*) ReadingProgress
                   └─── (*) ArticleReport

Newsletter (standalone)
```text
## 🔌 API эндпоинты

REST API построен на **Django Ninja** с автоматической документацией.

### Документация API

- **Swagger UI**: `/api/docs` - интерактивная документация
- **OpenAPI Schema**: `/api/openapi.json` - JSON схема

### Список эндпоинтов

#### Статьи

```text
GET  /api/blog/articles/              # Список статей с пагинацией
GET  /api/blog/articles/{slug}/       # Детали статьи
GET  /api/blog/articles/featured/     # Рекомендованные статьи
GET  /api/blog/articles/{slug}/related/ # Похожие статьи
POST /api/blog/articles/{slug}/react/ # Добавить реакцию (лайк/дизлайк)
```text
#### Категории

```text
GET /api/blog/categories/             # Список всех категорий
GET /api/blog/categories/{slug}/      # Детали категории
```text
#### Серии

```text
GET /api/blog/series/                 # Список всех серий
GET /api/blog/series/{slug}/          # Детали серии со статьями
```text
#### Теги

```text
GET /api/blog/tags/                   # Список популярных тегов
GET /api/blog/tags/{slug}/            # Статьи с конкретным тегом
```text
#### Поиск и фильтрация

```text
GET /api/blog/search/?q=python        # Полнотекстовый поиск
GET /api/blog/articles/?category=python  # Фильтр по категории
GET /api/blog/articles/?difficulty=beginner # Фильтр по сложности
GET /api/blog/articles/?tag=django    # Фильтр по тегу
```text
### Примеры запросов

**Получить список статей:**

```bash
curl -X GET "<http://localhost:8000/api/blog/articles/?page=1&page_size=10">
```text
**Ответ:**

```json
{
  "items": [
    {
      "id": 1,
      "title": "Введение в Python",
      "slug": "intro-python",
      "excerpt": "Основы языка программирования Python",
      "category": {
        "id": 1,
        "name": "Python",
        "slug": "python",
        "icon": "🐍"
      },
      "author": {
        "id": 1,
        "username": "admin",
        "avatar": "/media/avatars/admin.jpg"
      },
      "tags": ["python", "basics"],
      "difficulty": "beginner",
      "reading_time": 5,
      "views_count": 150,
      "likes_count": 25,
      "published_at": "2025-01-01T10:00:00Z"
    }
  ],
  "total": 42,
  "page": 1,
  "page_size": 10,
  "total_pages": 5
}
```text
**Поставить лайк:**

```bash
curl -X POST "<http://localhost:8000/api/blog/articles/intro-python/react/"> \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"reaction_type": "like"}'
```text
Подробная документация: см. `BLOG_API_DOCUMENTATION.md`

## 🎨 Представления (Views)

### Публичные страницы

#### BlogHomeView

Главная страница блога.

```python
URL: /blog/
Template: blog/home.html
Context:

  - featured_articles: QuerySet[Article] (до 6)
  - latest_articles: QuerySet[Article] (до 12)
  - popular_categories: QuerySet[Category] (до 8)
  - popular_tags: QuerySet[Tag] (до 20)
  - stats: dict (total_articles, total_views, total_comments)

```text
#### ArticleListView

Список всех статей с пагинацией.

```python
URL: /blog/articles/
Template: blog/article_list.html
Пагинация: 12 статей на страницу
Фильтры:

  - category: slug категории
  - difficulty: beginner/intermediate/advanced
  - tag: slug тега

Сортировка:

  - -published_at (по умолчанию)
  - -views_count (популярные)
  - -likes_count (рейтинг)

```text
#### ArticleDetailView

Детальная страница статьи.

```python
URL: /blog/articles/<slug>/
Template: blog/article_detail.html
Context:

  - article: Article
  - related_articles: QuerySet[Article] (до 5)
  - comments: QuerySet[Comment] (корневые, одобренные)
  - comment_form: CommentForm
  - user_reaction: str|None ('like'/'dislike'/None)
  - is_bookmarked: bool
  - reading_progress: int (0-100)

```text
#### CategoryDetailView, SeriesDetailView, TagDetailView

Страницы категорий, серий, тегов со списком статей.

### AJAX эндпоинты

#### AddCommentView

```python
URL: /blog/ajax/add-comment/
Method: POST
Auth: LoginRequiredMixin
Data: {article_id, content, parent_id?}
Response: {success, comment_html, comments_count}
```text
#### ToggleReactionView

```python
URL: /blog/ajax/toggle-reaction/
Method: POST
Auth: LoginRequiredMixin
Data: {article_id, reaction_type: 'like'/'dislike'}
Response: {success, likes_count, dislikes_count, user_reaction}
```text
#### ToggleBookmarkView

```python
URL: /blog/ajax/toggle-bookmark/
Method: POST
Auth: LoginRequiredMixin
Data: {article_id}
Response: {success, is_bookmarked}
```text
#### UpdateReadingProgressView

```python
URL: /blog/ajax/update-reading-progress/
Method: POST
Auth: LoginRequiredMixin
Data: {article_id, progress: 0-100}
Response: {success}
```text
Подробности: см. `views.py` (2994 строки, 24 представления)

## ⚡ Кеширование

Используется **Redis** для кеширования данных и повышения производительности.

### Кеш утилиты (`cache_utils.py`)

#### Декораторы кеширования

```python
from blog.cache_utils import (
    cache_article_list,      # 5 минут
    cache_article_detail,    # 15 минут
    cache_category_list,     # 30 минут
    cache_stats              # 10 минут
)

# Пример использования

@cache_article_list(timeout=300)
def get_featured_articles():
    return Article.objects.filter(is_featured=True)
```text
#### Функции

```python

# Получить ключ кеша

key = get_cache_key('article_list', category='python', page=1)

# Инвалидация кеша

invalidate_blog_cache(['article:*', 'category:python'])

# Прогрев кеша (популярные данные)

warm_cache()  # Вызывается автоматически каждые 5 минут
```text
### Celery задачи (`tasks.py`)

#### Периодические задачи

```python

# Прогрев кеша (каждые 5 минут)

@shared_task(name='blog.warm_cache')
def warm_cache_task():
    warm_cache()

# Обновление популярных статей (каждый час)

@shared_task(name='blog.update_popular_articles')
def update_popular_articles():
    articles = Article.objects.order_by('-views_count')[:20]
    cache.set('popular_articles', list(articles), timeout=3600)

# Очистка старого кеша (каждые 24 часа)

@shared_task(name='blog.cleanup_old_cache')
def cleanup_old_cache():

    # Удаление кеша старше 7 дней

    pass

# Генерация sitemap (каждые 24 часа)

@shared_task(name='blog.generate_sitemap')
def generate_sitemap_task():
    call_command('generate_sitemap')
```text
#### Асинхронные задачи

```python

# Обновление счетчика просмотров

@shared_task(name='blog.update_article_views')
def update_article_views(article_id, increment=1):
    Article.objects.filter(id=article_id).update(
        views_count=F('views_count') + increment
    )
```text
### Настройки кеша (settings.py)

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        'KEY_PREFIX': 'pyland',
        'TIMEOUT': 300,
    }
}

CACHE_TTL = {
    'article_list': 300,      # 5 минут
    'article_detail': 900,    # 15 минут
    'category_list': 1800,    # 30 минут
    'stats': 600,             # 10 минут
}
```text
## 🛡️ Rate Limiting

Защита API от чрезмерного использования.

### Middleware (`middleware.py`)

```python
class RateLimitMiddleware:
    """
    Ограничение количества запросов к API.

    Лимиты:

      - Анонимные: 100 запросов/час
      - Авторизованные: 1000 запросов/час

    Заголовки ответа:

      - X-RateLimit-Limit: Максимум запросов
      - X-RateLimit-Remaining: Осталось запросов
      - X-RateLimit-Reset: Время сброса (timestamp)

    При превышении: 429 Too Many Requests
    """
```text
Настройка в `.env`:

```bash
RATE_LIMIT_ANONYMOUS=100        # Запросов в час для анонимов
RATE_LIMIT_AUTHENTICATED=1000   # Запросов в час для авторизованных
```text
## 👨‍💼 Администрирование

Django Admin конфигурация с расширенными возможностями.

### Админ классы (`admin.py`)

#### ArticleAdmin

- **Список полей**: title, category, author, status, difficulty, is_featured, published_at, views_count
- **Фильтры**: status, category, difficulty, is_featured, published_at
- **Поиск**: title, content, slug
- **Inline редакторы**: нет
- **Массовые действия**:
  - Опубликовать статьи
  - Перевести в черновики
  - Архивировать статьи
  - Пересчитать время чтения
  - Сделать рекомендованными
- **Readonly поля**: views_count, reading_time, created_at, updated_at

#### CommentAdmin

- **Список полей**: article, author, content_preview, created_at, is_approved, likes_count
- **Фильтры**: is_approved, created_at
- **Поиск**: content, author__username
- **Массовые действия**:
  - Одобрить комментарии
  - Отклонить комментарии

#### CategoryAdmin, SeriesAdmin, AuthorAdmin, и др

Полная конфигурация для всех 11 моделей.

### Примеры использования админки

```python

# Массово опубликовать статьи

# 1. Выбрать статьи в списке

# 2. Выбрать действие "Опубликовать выбранные статьи"

# 3. Нажать "Выполнить"

# Пересчитать время чтения для всех статей

# 1. Выбрать все статьи (Ctrl+A)

# 2. Выбрать действие "Пересчитать время чтения"

# 3. Нажать "Выполнить"

```text
## 🧪 Тестирование

**149 юнит тестов** с **75% покрытием кода**.

### Структура тестов

```text
tests/
├── __init__.py
├── conftest.py           # Pytest fixtures (18 fixtures)
├── factories.py          # Factory Boy фабрики (11 фабрик)
├── test_models.py        # Тесты моделей (37 тестов)
├── test_views.py         # Тесты представлений (54 теста)
├── test_api.py           # Тесты API (38 тестов)
├── test_forms.py         # Тесты форм (12 тестов)
└── test_admin.py         # Тесты админки (8 тестов)
```text
Подробности: см. `tests/README.md`

### Запуск тестов

```bash

# Все тесты блога

pytest src/blog/tests/

# Конкретный файл

pytest src/blog/tests/test_models.py

# С покрытием кода

pytest src/blog/tests/ --cov=blog --cov-report=html

# Быстрый запуск (без warnings)

pytest src/blog/tests/ -q --tb=line
```text
### Текущий статус

```text
✅ 149 passed in 10.64s
📊 75% code coverage
⚠️  253 warnings (не критичные)
```text
## 🚀 Использование

### Добавление статьи через код

```python
from blog.models import Article, Category
from django.utils import timezone

# Получить/создать категорию

category, _ = Category.objects.get_or_create(
    slug='python',
    defaults={'name': 'Python', 'icon': '🐍'}
)

# Создать статью

article = Article.objects.create(
    title='Декораторы в Python',
    slug='python-decorators',
    content='''

# Декораторы в Python

Декораторы - это мощный инструмент для модификации функций.

## Пример

\`\`\`python
def my_decorator(func):
    def wrapper():
        print("До вызова функции")
        func()
        print("После вызова функции")
    return wrapper

@my_decorator
def say_hello():
    print("Hello!")
\`\`\`
    ''',
    excerpt='Введение в декораторы Python с примерами',
    category=category,
    difficulty='intermediate',
    status='published',
    published_at=timezone.now(),
    is_featured=True,
    allow_comments=True,
)

# Добавить теги

article.tags.add('python', 'decorators', 'programming')

# Автоматический расчет времени чтения

article.update_reading_time()

# Получить URL статьи

url = article.get_absolute_url()  # /blog/articles/python-decorators/
```text
### Работа с комментариями

```python
from blog.models import Comment

# Добавить комментарий

comment = Comment.objects.create(
    article=article,
    author=request.user,
    content='Отличное объяснение декораторов!'
)

# Ответить на комментарий

reply = Comment.objects.create(
    article=article,
    author=another_user,
    content='Согласен, очень понятно!',
    parent=comment
)

# Получить все комментарии статьи

comments = article.comments.filter(
    parent=None,  # Только корневые
    is_approved=True
).select_related('author').order_by('-created_at')
```text
### Использование API в JavaScript

```javascript
// Получить список статей
fetch('/api/blog/articles/?page=1&page_size=10')
  .then(response => response.json())
  .then(data => {
    console.log(`Всего статей: ${data.total}`);
    data.items.forEach(article => {
      console.log(article.title);
    });
  });

// Поставить лайк статье
fetch('/api/blog/articles/python-decorators/react/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${jwtToken}`,
    'X-CSRFToken': csrfToken,
  },
  body: JSON.stringify({ reaction_type: 'like' })
})
  .then(response => response.json())
  .then(data => {
    console.log(`Лайков: ${data.likes_count}`);
  });
```text
### Management команды

```bash
# Генерация sitemap.xml
poetry run python src/manage.py generate_sitemap

# С указанием пути
poetry run python src/manage.py generate_sitemap --output=/path/to/sitemap.xml
```text
## 📚 Дополнительная документация

- **API**: См. `/api/docs` или `BLOG_API_DOCUMENTATION.md`
- **Templates**: См. `templates/README.md`
- **Template Tags**: См. `templatetags/README.md`
- **Tests**: См. `tests/README.md`
- **Production**: См. `PRODUCTION_DEPLOYMENT.md`
- **Improvements**: См. `PRODUCTION_IMPROVEMENTS.md`

## 🔗 Зависимости

```toml

# Core

django = "^5.1.4"
psycopg2-binary = "^2.9.10"  # PostgreSQL

# API

django-ninja = "^1.3.0"

# Tags

django-taggit = "^6.1.0"

# Caching & Tasks

redis = "^5.2.1"
celery = "^5.4.0"

# Monitoring

sentry-sdk = {extras = ["django"], version = "^2.43.0"}

# Images

pillow = "^11.0.0"
```text
## 📝 Лицензия

Часть проекта PySchool. © 2025

## 👥 Авторы

PySchool Team

---

**Статус**: ✅ Production Ready | 🧪 149/149 tests passing | 📊 75% coverage
