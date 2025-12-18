# Blog Tests

Комплексный набор тестов для приложения блога (149 тестов, 75% покрытие кода).

## 📋 Содержание

- [Обзор](#обзор)
- [Структура тестов](#структура-тестов)
- [Fixtures](#fixtures)
- [Factories](#factories)
- [Тестовые модули](#тестовые-модули)
- [Запуск тестов](#запуск-тестов)
- [Покрытие кода](#покрытие-кода)
- [Best Practices](#best-practices)

## 🎯 Обзор

Тесты написаны с использованием **pytest** и **Factory Boy** для создания тестовых данных. Все тесты проходят в изолированной тестовой базе данных.

### Статистика

```
📊 Общие показатели:
├── Всего тестов:        149 ✅
├── Покрытие кода:       75%
├── Файлов тестов:       6
├── Строк кода тестов:   2,845
├── Fixtures:            18
└── Factories:           11
```

### Тестируемые компоненты

✅ **Модели** (37 тестов) - Логика моделей, валидация, методы  
✅ **Views** (54 теста) - Представления, AJAX эндпоинты, контекст  
✅ **API** (38 тестов) - REST API эндпоинты, сериализация  
✅ **Forms** (12 тестов) - Валидация форм  
✅ **Admin** (8 тестов) - Админ панель, массовые операции  

## 📁 Структура тестов

```
tests/
├── __init__.py              # Инициализация пакета (22 строки)
├── conftest.py              # Pytest fixtures (239 строк, 18 fixtures)
├── factories.py             # Factory Boy фабрики (382 строки, 11 фабрик)
├── test_models.py           # Тесты моделей (588 строк, 37 тестов)
├── test_views.py            # Тесты представлений (506 строк, 54 теста)
├── test_api.py              # Тесты API (532 строки, 38 тестов)
├── test_forms.py            # Тесты форм (188 строк, 12 тестов)
└── test_admin.py            # Тесты админки (388 строк, 8 тестов)
```

## 🔧 Fixtures

**Файл**: `conftest.py` (239 строк)

### User Fixtures

#### user
Обычный пользователь для тестов.

```python
@pytest.fixture
def user(db):
    """
    Returns:
        User: Обычный пользователь (не staff, не superuser)
    """
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
        first_name="Test",
        last_name="User"
    )
```

**Использование**:
```python
def test_user_can_comment(user, article):
    comment = Comment.objects.create(
        article=article,
        author=user,
        content="Test comment"
    )
    assert comment.author == user
```

#### staff_user
Пользователь со статусом staff (доступ к админке).

```python
@pytest.fixture
def staff_user(db):
    return User.objects.create_user(
        username="staffuser",
        is_staff=True
    )
```

#### superuser
Администратор с полными правами.

```python
@pytest.fixture
def superuser(db):
    return User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="adminpass123"
    )
```

#### author_user
Пользователь-автор статей.

```python
@pytest.fixture
def author_user(db):
    return User.objects.create_user(
        username="author",
        email="author@example.com"
    )
```

### Client Fixtures

#### client
Django test client для HTTP запросов.

```python
@pytest.fixture
def client():
    """
    Returns:
        Client: Django test client
    """
    return Client()
```

#### authenticated_client
Client с авторизованным пользователем.

```python
@pytest.fixture
def authenticated_client(client, user):
    """
    Returns:
        Client: Client с залогиненным пользователем
    """
    client.force_login(user)
    return client
```

#### api_client
REST API client для тестирования API.

```python
@pytest.fixture
def api_client():
    """
    Returns:
        APIClient: DRF API client
    """
    return APIClient()
```

### Blog Model Fixtures

#### category
Тестовая категория.

```python
@pytest.fixture
def category(db):
    """
    Returns:
        Category: Тестовая категория "Python"
    """
    return Category.objects.create(
        name="Python",
        slug="python",
        icon="🐍",
        color="#3498db"
    )
```

#### article
Опубликованная статья.

```python
@pytest.fixture
def article(db, category, user):
    """
    Returns:
        Article: Опубликованная статья
    """
    return Article.objects.create(
        title="Test Article",
        slug="test-article",
        content="# Test Content\n\nThis is a test.",
        excerpt="Test excerpt",
        category=category,
        author=user,
        status="published",
        published_at=timezone.now(),
        difficulty="beginner"
    )
```

#### draft_article
Черновик статьи.

```python
@pytest.fixture
def draft_article(db, category, user):
    return Article.objects.create(
        title="Draft Article",
        status="draft"
    )
```

#### series
Серия статей.

```python
@pytest.fixture
def series(db):
    return Series.objects.create(
        title="Python Basics",
        slug="python-basics",
        description="Learn Python from scratch"
    )
```

#### comment
Корневой комментарий к статье.

```python
@pytest.fixture
def comment(db, article, user):
    return Comment.objects.create(
        article=article,
        author=user,
        content="Test comment"
    )
```

#### nested_comment
Вложенный ответ на комментарий.

```python
@pytest.fixture
def nested_comment(db, article, comment, author_user):
    return Comment.objects.create(
        article=article,
        author=author_user,
        content="Reply to comment",
        parent=comment
    )
```

### Полный список fixtures (18 штук)

1. `user` - Обычный пользователь
2. `staff_user` - Staff пользователь
3. `superuser` - Администратор
4. `author_user` - Автор статей
5. `client` - Django test client
6. `authenticated_client` - Авторизованный client
7. `staff_client` - Client staff пользователя
8. `api_client` - REST API client
9. `category` - Категория
10. `article` - Опубликованная статья
11. `draft_article` - Черновик
12. `featured_article` - Рекомендованная статья
13. `series` - Серия статей
14. `comment` - Комментарий
15. `nested_comment` - Вложенный комментарий
16. `article_reaction` - Реакция на статью
17. `bookmark` - Закладка
18. `reading_progress` - Прогресс чтения

## 🏭 Factories

**Файл**: `factories.py` (382 строки)

Factory Boy фабрики для быстрого создания тестовых данных.

### UserFactory

```python
class UserFactory(DjangoModelFactory):
    """Фабрика для создания пользователей."""
    
    class Meta:
        model = User
        django_get_or_create = ('username',)
    
    username = Faker('user_name')
    email = Faker('email')
    first_name = Faker('first_name')
    last_name = Faker('last_name')
    password = factory.django.Password('testpass123')
```

**Использование**:
```python
# Один пользователь
user = UserFactory()

# С кастомными данными
user = UserFactory(username='john', email='john@example.com')

# Множество пользователей
users = UserFactory.create_batch(10)
```

### CategoryFactory

```python
class CategoryFactory(DjangoModelFactory):
    """Фабрика для создания категорий."""
    
    class Meta:
        model = Category
    
    name = Faker('word')
    slug = factory.LazyAttribute(lambda o: slugify(o.name))
    icon = factory.Iterator(['📝', '🐍', '💻', '🚀'])
    color = factory.Iterator(['#3498db', '#e74c3c', '#2ecc71'])
```

**Использование**:
```python
# Одна категория
category = CategoryFactory()

# Конкретная категория
python_cat = CategoryFactory(name='Python', slug='python', icon='🐍')

# 5 категорий
categories = CategoryFactory.create_batch(5)
```

### ArticleFactory

```python
class ArticleFactory(DjangoModelFactory):
    """Фабрика для создания статей."""
    
    class Meta:
        model = Article
    
    title = Faker('sentence', nb_words=6)
    slug = factory.LazyAttribute(lambda o: slugify(o.title))
    content = Faker('text', max_nb_chars=2000)
    excerpt = Faker('text', max_nb_chars=200)
    category = SubFactory(CategoryFactory)
    author = SubFactory(UserFactory)
    status = 'published'
    published_at = factory.LazyFunction(timezone.now)
    difficulty = factory.Iterator(['beginner', 'intermediate', 'advanced'])
    
    @post_generation
    def tags(self, create, extracted, **kwargs):
        """Добавление тегов после создания."""
        if not create:
            return
        if extracted:
            for tag in extracted:
                self.tags.add(tag)
```

**Использование**:
```python
# Опубликованная статья
article = ArticleFactory()

# Черновик
draft = ArticleFactory(status='draft', published_at=None)

# С тегами
article = ArticleFactory(tags=['python', 'django', 'tutorial'])

# С конкретной категорией
article = ArticleFactory(category=python_category)

# 20 статей
articles = ArticleFactory.create_batch(20)

# 10 статей в категории Python
articles = ArticleFactory.create_batch(10, category__name='Python')
```

### SeriesFactory

```python
class SeriesFactory(DjangoModelFactory):
    """Фабрика для создания серий."""
    
    class Meta:
        model = Series
    
    title = Faker('sentence', nb_words=4)
    slug = factory.LazyAttribute(lambda o: slugify(o.title))
    description = Faker('text', max_nb_chars=500)
```

### CommentFactory

```python
class CommentFactory(DjangoModelFactory):
    """Фабрика для создания комментариев."""
    
    class Meta:
        model = Comment
    
    article = SubFactory(ArticleFactory)
    author = SubFactory(UserFactory)
    content = Faker('text', max_nb_chars=500)
    is_approved = True
    
    @factory.post_generation
    def with_replies(self, create, extracted, **kwargs):
        """Создание вложенных ответов."""
        if not create or not extracted:
            return
        for _ in range(extracted):
            CommentFactory(article=self.article, parent=self)
```

**Использование**:
```python
# Комментарий
comment = CommentFactory(article=article)

# Комментарий с 3 ответами
comment = CommentFactory(article=article, with_replies=3)

# Вложенный комментарий (ответ)
reply = CommentFactory(article=article, parent=parent_comment)
```

### Полный список factories (11 штук)

1. `UserFactory` - Пользователи
2. `StaffUserFactory` - Staff пользователи
3. `SuperUserFactory` - Администраторы
4. `CategoryFactory` - Категории
5. `SeriesFactory` - Серии
6. `ArticleFactory` - Статьи
7. `CommentFactory` - Комментарии
8. `ArticleReactionFactory` - Реакции
9. `BookmarkFactory` - Закладки
10. `ReadingProgressFactory` - Прогресс чтения
11. `NewsletterFactory` - Подписки

## 🧪 Тестовые модули

### test_models.py (588 строк, 37 тестов)

Тестирование логики моделей, валидации, методов.

**Основные тесты**:

```python
class TestCategoryModel:
    """Тесты модели Category (5 тестов)"""
    
    def test_create_category(self, db):
        """Создание категории"""
        category = Category.objects.create(name="Python", slug="python")
        assert category.name == "Python"
    
    def test_slug_auto_generation(self, db):
        """Автоматическая генерация slug"""
        category = Category.objects.create(name="Python Basics")
        assert category.slug == "python-basics"
    
    def test_get_absolute_url(self, category):
        """URL категории"""
        assert category.get_absolute_url() == "/blog/categories/python/"

class TestArticleModel:
    """Тесты модели Article (15 тестов)"""
    
    def test_create_article(self, article):
        """Создание статьи"""
        assert article.title == "Test Article"
        assert article.status == "published"
    
    def test_published_articles_queryset(self, article, draft_article):
        """Фильтр опубликованных статей"""
        published = Article.objects.filter(status='published')
        assert article in published
        assert draft_article not in published
    
    def test_increment_views(self, article):
        """Увеличение просмотров"""
        initial = article.views_count
        article.increment_views()
        assert article.views_count == initial + 1
    
    def test_update_reading_time(self, article):
        """Расчет времени чтения"""
        article.content = "word " * 400  # 400 слов
        article.update_reading_time()
        assert article.reading_time == 2  # 400/200 = 2 минуты
    
    def test_get_related_articles(self, article, category):
        """Получение похожих статей"""
        # Создать 5 статей в той же категории
        ArticleFactory.create_batch(5, category=category)
        related = article.get_related_articles(limit=3)
        assert len(related) == 3

class TestCommentModel:
    """Тесты модели Comment (10 тестов)"""
    
    def test_create_comment(self, comment):
        """Создание комментария"""
        assert comment.content == "Test comment"
        assert comment.is_approved is True
    
    def test_comment_depth(self, comment, nested_comment):
        """Уровень вложенности"""
        assert comment.get_depth() == 0
        assert nested_comment.get_depth() == 1
    
    def test_can_reply(self, comment, nested_comment):
        """Проверка возможности ответа"""
        assert comment.can_reply() is True  # depth 0
        assert nested_comment.can_reply() is True  # depth 1
    
    def test_max_depth_validation(self, article, user):
        """Валидация максимальной глубины (3 уровня)"""
        level1 = CommentFactory(article=article)
        level2 = CommentFactory(article=article, parent=level1)
        level3 = CommentFactory(article=article, parent=level2)
        
        # Попытка создать 4-й уровень
        with pytest.raises(ValidationError):
            level4 = Comment(
                article=article,
                author=user,
                content="Too deep",
                parent=level3
            )
            level4.clean()
    
    def test_get_replies(self, comment):
        """Получение ответов"""
        # Создать 3 ответа
        CommentFactory.create_batch(3, article=comment.article, parent=comment)
        replies = comment.get_replies()
        assert replies.count() == 3

class TestSeriesModel:
    """Тесты модели Series (3 теста)"""

class TestArticleReactionModel:
    """Тесты модели ArticleReaction (2 теста)"""

class TestBookmarkModel:
    """Тесты модели Bookmark (2 теста)"""
```

### test_views.py (506 строк, 54 теста)

Тестирование Django представлений.

**Основные тесты**:

```python
class TestBlogHomeView:
    """Тесты главной страницы (5 тестов)"""
    
    def test_home_page_loads(self, client):
        """Страница загружается"""
        response = client.get('/blog/')
        assert response.status_code == 200
    
    def test_featured_articles_in_context(self, client, featured_article):
        """Рекомендованные статьи в контексте"""
        response = client.get('/blog/')
        assert 'featured_articles' in response.context
        assert featured_article in response.context['featured_articles']
    
    def test_stats_in_context(self, client, article):
        """Статистика в контексте"""
        response = client.get('/blog/')
        stats = response.context['stats']
        assert stats['total_articles'] > 0

class TestArticleListView:
    """Тесты списка статей (8 тестов)"""
    
    def test_article_list_loads(self, client):
        response = client.get('/blog/articles/')
        assert response.status_code == 200
    
    def test_pagination(self, client):
        """Пагинация работает"""
        ArticleFactory.create_batch(15)  # Создать 15 статей
        response = client.get('/blog/articles/')
        assert response.context['page_obj'].paginator.num_pages == 2
    
    def test_category_filter(self, client, category):
        """Фильтр по категории"""
        ArticleFactory.create_batch(5, category=category)
        response = client.get(f'/blog/articles/?category={category.slug}')
        for article in response.context['articles']:
            assert article.category == category

class TestArticleDetailView:
    """Тесты детальной страницы (12 тестов)"""
    
    def test_article_detail_loads(self, client, article):
        """Страница статьи загружается"""
        response = client.get(article.get_absolute_url())
        assert response.status_code == 200
        assert article in response.context
    
    def test_draft_not_accessible(self, client, draft_article):
        """Черновик недоступен"""
        response = client.get(draft_article.get_absolute_url())
        assert response.status_code == 404
    
    def test_comments_in_context(self, client, article, comment):
        """Комментарии в контексте"""
        response = client.get(article.get_absolute_url())
        assert 'comments' in response.context
        assert comment in response.context['comments']
    
    def test_related_articles(self, client, article):
        """Похожие статьи"""
        ArticleFactory.create_batch(5, category=article.category)
        response = client.get(article.get_absolute_url())
        assert 'related_articles' in response.context

class TestAddCommentView:
    """Тесты добавления комментариев (6 тестов)"""
    
    def test_add_comment_authenticated(self, authenticated_client, article):
        """Авторизованный может комментировать"""
        response = authenticated_client.post('/blog/ajax/add-comment/', {
            'article_id': article.id,
            'content': 'Test comment'
        })
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
    
    def test_add_comment_anonymous(self, client, article):
        """Анонимный не может комментировать"""
        response = client.post('/blog/ajax/add-comment/', {
            'article_id': article.id,
            'content': 'Test'
        })
        assert response.status_code == 302  # Redirect to login

class TestToggleReactionView:
    """Тесты реакций (8 тестов)"""
    
    def test_like_article(self, authenticated_client, article):
        """Поставить лайк"""
        response = authenticated_client.post('/blog/ajax/toggle-reaction/', {
            'article_id': article.id,
            'reaction_type': 'like'
        })
        data = response.json()
        assert data['success'] is True
        assert data['likes_count'] == 1

class TestSearchView:
    """Тесты поиска (5 тестов)"""
    
    def test_search_results(self, client, article):
        """Поиск находит статьи"""
        response = client.get('/blog/search/?q=test')
        assert response.status_code == 200
        assert 'results' in response.context
```

### test_api.py (532 строки, 38 тестов)

Тестирование REST API.

**Основные тесты**:

```python
class TestArticlesAPI:
    """Тесты API статей (15 тестов)"""
    
    def test_list_articles(self, api_client):
        """GET /api/blog/articles/"""
        ArticleFactory.create_batch(5)
        response = api_client.get('/api/blog/articles/')
        assert response.status_code == 200
        data = response.json()
        assert len(data['items']) == 5
    
    def test_article_detail(self, api_client, article):
        """GET /api/blog/articles/{slug}/"""
        response = api_client.get(f'/api/blog/articles/{article.slug}/')
        assert response.status_code == 200
        data = response.json()
        assert data['title'] == article.title
    
    def test_featured_articles(self, api_client):
        """GET /api/blog/articles/featured/"""
        ArticleFactory.create_batch(3, is_featured=True)
        response = api_client.get('/api/blog/articles/featured/')
        assert response.status_code == 200

class TestCategoriesAPI:
    """Тесты API категорий (8 тестов)"""
    
    def test_list_categories(self, api_client):
        """GET /api/blog/categories/"""
        CategoryFactory.create_batch(5)
        response = api_client.get('/api/blog/categories/')
        assert response.status_code == 200

class TestReactionsAPI:
    """Тесты API реакций (10 тестов)"""
    
    def test_add_reaction(self, api_client, user, article):
        """POST /api/blog/articles/{slug}/react/"""
        api_client.force_authenticate(user=user)
        response = api_client.post(
            f'/api/blog/articles/{article.slug}/react/',
            {'reaction_type': 'like'}
        )
        assert response.status_code == 200
```

### test_forms.py (188 строк, 12 тестов)

Тестирование Django форм.

```python
class TestCommentForm:
    """Тесты формы комментариев (12 тестов)"""
    
    def test_valid_form(self):
        """Валидная форма"""
        form = CommentForm(data={'content': 'Test comment'})
        assert form.is_valid()
    
    def test_empty_content(self):
        """Пустой контент невалиден"""
        form = CommentForm(data={'content': ''})
        assert not form.is_valid()
    
    def test_min_length(self):
        """Минимальная длина 3 символа"""
        form = CommentForm(data={'content': 'ab'})
        assert not form.is_valid()
```

### test_admin.py (388 строк, 8 тестов)

Тестирование Django Admin.

```python
class TestArticleAdmin:
    """Тесты админки статей (5 тестов)"""
    
    def test_publish_action(self, staff_client):
        """Массовая публикация статей"""
        drafts = ArticleFactory.create_batch(3, status='draft')
        # Выполнить действие "publish"
        # Проверить, что все статьи опубликованы

class TestCommentAdmin:
    """Тесты админки комментариев (3 теста)"""
```

## 🚀 Запуск тестов

### Все тесты блога

```bash
cd /Users/dmitrii/Documents/GitHub/pyschool_delete_css/backend

# Запуск всех тестов
pytest src/blog/tests/

# С выводом информации
pytest src/blog/tests/ -v

# Быстрый запуск (без warnings)
pytest src/blog/tests/ -q --tb=line
```

### Конкретный файл

```bash
# Только тесты моделей
pytest src/blog/tests/test_models.py

# Только тесты API
pytest src/blog/tests/test_api.py -v
```

### Конкретный тест

```bash
# Один класс тестов
pytest src/blog/tests/test_models.py::TestArticleModel

# Один тест
pytest src/blog/tests/test_models.py::TestArticleModel::test_increment_views
```

### С фильтрацией

```bash
# Тесты с "comment" в названии
pytest src/blog/tests/ -k comment

# Тесты с "api" в названии
pytest src/blog/tests/ -k api -v
```

### Параллельный запуск

```bash
# С pytest-xdist (быстрее)
pytest src/blog/tests/ -n auto
```

### С покрытием кода

```bash
# HTML отчет
pytest src/blog/tests/ --cov=blog --cov-report=html

# Консольный отчет
pytest src/blog/tests/ --cov=blog --cov-report=term-missing
```

### Failing first

```bash
# Сначала упавшие тесты
pytest src/blog/tests/ --ff

# Только упавшие тесты
pytest src/blog/tests/ --lf
```

## 📊 Покрытие кода

### Текущее покрытие: 75%

```
Name                  Stmts   Miss  Cover
-----------------------------------------
blog/__init__.py          0      0   100%
blog/admin.py           145     35    76%
blog/api.py             250     60    76%
blog/apps.py              4      0   100%
blog/cache_utils.py      85     25    71%
blog/forms.py            20      2    90%
blog/middleware.py       55     15    73%
blog/models.py          420    100    76%
blog/schemas.py          85      5    94%
blog/tasks.py            65     20    69%
blog/urls.py             15      0   100%
blog/views.py           680    165    76%
-----------------------------------------
TOTAL                  1824    427    75%
```

### Генерация отчета

```bash
# HTML отчет (интерактивный)
pytest src/blog/tests/ --cov=blog --cov-report=html

# Открыть отчет
open htmlcov/index.html

# XML отчет (для CI/CD)
pytest src/blog/tests/ --cov=blog --cov-report=xml

# Терминальный отчет
pytest src/blog/tests/ --cov=blog --cov-report=term
```

### Coverage по модулям

```bash
# Только models.py
pytest src/blog/tests/test_models.py --cov=blog.models

# Только API
pytest src/blog/tests/test_api.py --cov=blog.api

# Только views
pytest src/blog/tests/test_views.py --cov=blog.views
```

## 💡 Best Practices

### 1. Именование тестов

```python
# ✅ Хорошо - описательное название
def test_user_can_comment_on_published_article():
    pass

# ❌ Плохо - неясное название
def test_comment():
    pass
```

### 2. Организация тестов

```python
# ✅ Хорошо - группировка в классы
class TestArticleModel:
    def test_create_article(self):
        pass
    
    def test_update_article(self):
        pass

# ❌ Плохо - все в одном файле без структуры
def test_1():
    pass
def test_2():
    pass
```

### 3. Использование fixtures

```python
# ✅ Хорошо - переиспользование через fixtures
def test_comment(article, user):
    comment = Comment.objects.create(
        article=article,
        author=user,
        content="Test"
    )

# ❌ Плохо - создание данных в каждом тесте
def test_comment():
    user = User.objects.create(...)
    category = Category.objects.create(...)
    article = Article.objects.create(...)
    comment = Comment.objects.create(...)
```

### 4. Использование factories

```python
# ✅ Хорошо - фабрики для сложных данных
def test_article_list():
    articles = ArticleFactory.create_batch(10, status='published')
    assert len(articles) == 10

# ❌ Плохо - ручное создание множества объектов
def test_article_list():
    for i in range(10):
        Article.objects.create(
            title=f"Article {i}",
            slug=f"article-{i}",
            # ... много полей
        )
```

### 5. Assertions

```python
# ✅ Хорошо - конкретные проверки
def test_article_published():
    article = ArticleFactory(status='published')
    assert article.status == 'published'
    assert article.published_at is not None

# ❌ Плохо - общие проверки
def test_article_published():
    article = ArticleFactory(status='published')
    assert article
```

### 6. Тестирование исключений

```python
# ✅ Хорошо - pytest.raises
def test_max_depth_validation():
    with pytest.raises(ValidationError):
        # код, который должен вызвать ошибку
        pass

# ❌ Плохо - try/except
def test_max_depth_validation():
    try:
        # код
        assert False  # Не должно дойти сюда
    except ValidationError:
        pass
```

### 7. Независимость тестов

```python
# ✅ Хорошо - каждый тест независим
def test_create_article(db):
    article = ArticleFactory()
    assert article.id is not None

def test_update_article(db):
    article = ArticleFactory()
    article.title = "Updated"
    article.save()

# ❌ Плохо - тесты зависят друг от друга
article_id = None

def test_create_article():
    global article_id
    article = ArticleFactory()
    article_id = article.id

def test_update_article():
    article = Article.objects.get(id=article_id)  # Зависит от первого теста!
```

## 📚 Полезные команды

```bash
# Вся информация о тестах
pytest src/blog/tests/ -v --tb=short

# С временем выполнения
pytest src/blog/tests/ --durations=10

# Остановка на первой ошибке
pytest src/blog/tests/ -x

# Запуск последних упавших
pytest src/blog/tests/ --lf

# Дебаг режим
pytest src/blog/tests/ --pdb

# Показать print'ы
pytest src/blog/tests/ -s

# Показать локальные переменные при ошибке
pytest src/blog/tests/ -l

# Запуск определенных маркеров
pytest src/blog/tests/ -m slow  # Только медленные тесты
pytest src/blog/tests/ -m "not slow"  # Без медленных

# Генерация отчета JUnit (для CI/CD)
pytest src/blog/tests/ --junitxml=test-results.xml
```

## 🔗 Связанная документация

- **Models**: См. `../README.md` - Модели данных
- **Views**: См. `../README.md` - Представления
- **API**: См. `BLOG_API_DOCUMENTATION.md` - REST API
- **pytest docs**: https://docs.pytest.org/
- **Factory Boy docs**: https://factoryboy.readthedocs.io/

## 📦 Зависимости для тестирования

```toml
[tool.poetry.group.dev.dependencies]
pytest = "^8.3.4"
pytest-django = "^4.9.0"
pytest-cov = "^6.0.0"
pytest-xdist = "^3.6.1"  # Параллельный запуск
factory-boy = "^3.3.1"
faker = "^33.1.0"
```

---

**Статус**: ✅ 149/149 tests passing | 📊 75% coverage | 🧪 2,845 lines of test code | ⚡ 10.64s runtime
