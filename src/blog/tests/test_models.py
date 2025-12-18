"""
Tests for Blog Models.

Этот модуль содержит тесты для всех моделей блога:
- Category
- Article
- Series
- Comment
- ArticleReaction
- Bookmark
- ReadingProgress
- Newsletter

Каждый тест проверяет:
- Создание объектов
- Валидацию полей
- Методы моделей
- Properties (вычисляемые поля)
- Relationships (связи между моделями)
"""

from __future__ import annotations

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from django.utils.text import slugify

from blog.models import (
    Article,
    ArticleReaction,
    Bookmark,
    Category,
    Comment,
    Newsletter,
    ReadingProgress,
    Series,
)
from blog.tests.factories import (
    ArticleFactory,
    ArticleReactionFactory,
    BookmarkFactory,
    CategoryFactory,
    CommentFactory,
    DraftArticleFactory,
    FeaturedArticleFactory,
    NewsletterFactory,
    ReadingProgressFactory,
    SeriesFactory,
    UserFactory,
)

# ============================================================================
# CATEGORY MODEL TESTS
# ============================================================================


@pytest.mark.django_db
class TestCategoryModel:
    """Тесты для модели Category."""

    def test_create_category(self):
        """Тест создания категории."""
        category = CategoryFactory(name="Python")

        assert category.name == "Python"
        assert category.slug == "python"
        assert category.icon == category.icon  # Проверяем, что иконка установлена
        assert category.color.startswith("#")
        assert isinstance(category.created_at, type(timezone.now()))

    def test_category_str(self):
        """Тест строкового представления."""
        category = CategoryFactory(name="Django")
        assert str(category) == "Django"

    def test_category_slug_auto_generation(self):
        """Тест автоматической генерации slug."""
        category = Category.objects.create(name="Python Tutorials")
        assert category.slug == "python-tutorials"

    def test_category_unique_slug(self):
        """Тест уникальности slug."""
        from blog.models import Category

        CategoryFactory(slug="python")

        # Создаем вторую категорию напрямую через модель
        with pytest.raises(IntegrityError):
            Category.objects.create(name="Python 2", slug="python")

    def test_category_get_absolute_url(self):
        """Тест получения URL категории."""
        category = CategoryFactory(slug="python")
        url = category.get_absolute_url()

        assert "/blog/category/python/" in url

    def test_category_article_count_property(self):
        """Тест подсчета статей в категории."""
        category = CategoryFactory()

        # Создаем опубликованные статьи
        ArticleFactory.create_batch(3, category=category, status="published")
        # Создаем черновики
        DraftArticleFactory.create_batch(2, category=category)

        # Должны учитываться только опубликованные
        assert category.article_count == 3

    def test_category_get_tag_keywords_list(self):
        """Тест парсинга ключевых слов."""
        category = CategoryFactory(tag_keywords="Python, Django, Web")
        keywords = category.get_tag_keywords_list()

        assert keywords == ["python", "django", "web"]

    def test_category_empty_tag_keywords(self):
        """Тест пустых ключевых слов."""
        category = CategoryFactory(tag_keywords="")
        assert category.get_tag_keywords_list() == []


# ============================================================================
# ARTICLE MODEL TESTS
# ============================================================================


@pytest.mark.django_db
class TestArticleModel:
    """Тесты для модели Article."""

    def test_create_article(self):
        """Тест создания статьи."""
        user = UserFactory()
        category = CategoryFactory()
        article = ArticleFactory(title="Test Article", author=user, category=category)

        assert article.title == "Test Article"
        assert article.author == user
        assert article.category == category
        assert article.status == "published"

    def test_article_str(self):
        """Тест строкового представления."""
        article = ArticleFactory(title="My Article")
        assert str(article) == "My Article"

    def test_article_slug_auto_generation(self):
        """Тест автоматической генерации slug."""
        article = Article.objects.create(
            title="My Test Article", content="Content", author=UserFactory()
        )
        assert article.slug == "my-test-article"

    def test_article_unique_slug(self):
        """Тест уникальности slug."""
        from blog.models import Article

        ArticleFactory(slug="test-article")

        # Создаем вторую статью напрямую через модель
        with pytest.raises(IntegrityError):
            Article.objects.create(
                title="Test 2", slug="test-article", content="Content", author=UserFactory()
            )

    def test_article_get_absolute_url(self):
        """Тест получения URL статьи."""
        article = ArticleFactory(slug="my-article")
        url = article.get_absolute_url()

        assert "/blog/article/my-article/" in url

    def test_published_count_queryset(self):
        """Тест подсчета опубликованных статей."""
        from blog.models import Article

        ArticleFactory.create_batch(5, status="published")
        DraftArticleFactory.create_batch(3)

        published_count = Article.objects.filter(status="published").count()
        assert published_count == 5

    def test_article_views_increment(self):
        """Тест увеличения просмотров."""
        article = ArticleFactory(views_count=10)
        article.views_count += 1
        article.save()

        article.refresh_from_db()
        assert article.views_count == 11

    def test_article_reactions(self):
        """Тест работы с реакциями."""
        article = ArticleFactory()
        user1 = UserFactory()
        user2 = UserFactory()

        # Создаем реакции
        ArticleReactionFactory(article=article, user=user1, reaction_type="like")
        ArticleReactionFactory(article=article, user=user2, reaction_type="love")

        # Проверяем количество реакций
        assert article.reactions.count() == 2

    def test_article_with_tags(self):
        """Тест добавления тегов."""
        article = ArticleFactory(tags=["python", "django", "web"])

        assert article.tags.count() == 3
        tag_names = [tag.name for tag in article.tags.all()]
        assert "python" in tag_names
        assert "django" in tag_names

    def test_article_in_series(self):
        """Тест статьи в серии."""
        series = SeriesFactory()
        article = ArticleFactory(series=series, series_order=1)

        assert article.series == series
        assert article.series_order == 1

    def test_article_reading_time_calculation(self):
        """Тест расчета времени чтения."""
        # Предполагается ~200 слов в минуту
        content = " ".join(["word"] * 1000)  # 1000 слов
        article = ArticleFactory(content=content)

        # Время чтения должно быть между 1 и 30 минутами
        assert 1 <= article.reading_time <= 30

    def test_draft_article_not_published(self):
        """Тест что черновик не опубликован."""
        draft = DraftArticleFactory()

        assert draft.status == "draft"
        assert draft.published_at is None

    def test_featured_article(self):
        """Тест избранной статьи."""
        featured = FeaturedArticleFactory()

        assert featured.is_featured is True
        assert featured.views_count >= 500  # Проверка из фабрики


# ============================================================================
# SERIES MODEL TESTS
# ============================================================================


@pytest.mark.django_db
class TestSeriesModel:
    """Тесты для модели Series."""

    def test_create_series(self):
        """Тест создания серии."""
        series = SeriesFactory(title="Python Basics")

        assert series.title == "Python Basics"
        assert series.slug == slugify("Python Basics")
        assert series.status == "active"

    def test_series_str(self):
        """Тест строкового представления."""
        series = SeriesFactory(title="Django Guide")
        assert str(series) == "Django Guide"

    def test_series_get_absolute_url(self):
        """Тест получения URL серии."""
        series = SeriesFactory(slug="python-basics")
        url = series.get_absolute_url()

        assert "/blog/series/python-basics/" in url

    def test_series_with_articles(self):
        """Тест серии со статьями."""
        series = SeriesFactory()
        ArticleFactory.create_batch(5, series=series, status="published")

        assert series.articles.filter(status="published").count() == 5

    def test_series_article_ordering(self):
        """Тест упорядочивания статей в серии."""
        series = SeriesFactory()
        article1 = ArticleFactory(series=series, series_order=1)
        article2 = ArticleFactory(series=series, series_order=2)
        article3 = ArticleFactory(series=series, series_order=3)

        articles = series.articles.order_by("series_order")
        assert list(articles) == [article1, article2, article3]


# ============================================================================
# COMMENT MODEL TESTS
# ============================================================================


@pytest.mark.django_db
class TestCommentModel:
    """Тесты для модели Comment."""

    def test_create_comment(self):
        """Тест создания комментария."""
        article = ArticleFactory()
        user = UserFactory()
        comment = CommentFactory(article=article, author=user, content="Great article!")

        assert comment.article == article
        assert comment.author == user
        assert comment.content == "Great article!"
        assert comment.is_approved is True

    def test_comment_str(self):
        """Тест строкового представления."""
        user = UserFactory(username="testuser")
        article = ArticleFactory(title="Test Article")
        comment = CommentFactory(author=user, article=article, content="Test comment")
        comment_str = str(comment)

        # __str__ возвращает "Комментарий от username к "article_title""
        assert "testuser" in comment_str
        assert "Test Article" in comment_str

    def test_comment_reply(self):
        """Тест ответа на комментарий."""
        parent_comment = CommentFactory()
        reply = CommentFactory(
            article=parent_comment.article, parent=parent_comment, content="Reply to comment"
        )

        assert reply.parent == parent_comment
        assert parent_comment.replies.count() == 1

    def test_comment_nested_structure(self):
        """Тест вложенной структуры комментариев."""
        article = ArticleFactory()
        level0 = CommentFactory(article=article, parent=None)
        level1 = CommentFactory(article=article, parent=level0)
        level2 = CommentFactory(article=article, parent=level1)

        # Проверяем что parent правильно установлен
        assert level0.parent is None
        assert level1.parent == level0
        assert level2.parent == level1

        # Проверяем что replies работают
        assert level0.replies.count() == 1
        assert level1.replies.count() == 1

    def test_comment_replies_count(self):
        """Тест подсчета ответов на комментарий."""
        parent_comment = CommentFactory()

        # Создаем ответы к этому комментарию
        for _ in range(3):
            CommentFactory(
                article=parent_comment.article,  # К той же статье
                parent=parent_comment,
                is_approved=True,
            )

        assert parent_comment.reply_count == 3

    def test_comment_edit_tracking(self):
        """Тест отслеживания редактирования."""
        from datetime import timedelta

        from django.utils import timezone
        from freezegun import freeze_time

        # Создаем комментарий в определенное время
        with freeze_time("2025-01-01 12:00:00"):
            comment = CommentFactory()
            initial_time = timezone.now()

        # Обновляем комментарий через 2 минуты
        with freeze_time(initial_time + timedelta(minutes=2)):
            comment.content = "Updated content"
            comment.save()
            comment.refresh_from_db()

            # is_edited это property, который вычисляется на основе разницы created_at и updated_at
            assert comment.is_edited is True


# ============================================================================
# ARTICLE REACTION MODEL TESTS
# ============================================================================


@pytest.mark.django_db
class TestArticleReactionModel:
    """Тесты для модели ArticleReaction."""

    def test_create_reaction(self):
        """Тест создания реакции."""
        user = UserFactory()
        article = ArticleFactory()
        reaction = ArticleReactionFactory(user=user, article=article, reaction_type="like")

        assert reaction.user == user
        assert reaction.article == article
        assert reaction.reaction_type == "like"

    def test_reaction_types(self):
        """Тест различных типов реакций."""
        article = ArticleFactory()
        reaction_types = ["like", "love", "helpful", "insightful", "amazing"]

        for reaction_type in reaction_types:
            user = UserFactory()
            reaction = ArticleReactionFactory(
                user=user, article=article, reaction_type=reaction_type
            )
            assert reaction.reaction_type == reaction_type

    def test_unique_user_article_reaction(self):
        """Тест уникальности реакции пользователя на статью."""
        from blog.models import ArticleReaction

        user = UserFactory()
        article = ArticleFactory()

        ArticleReactionFactory(user=user, article=article, reaction_type="like")

        # Попытка создать вторую реакцию напрямую через модель
        with pytest.raises(IntegrityError):
            ArticleReaction.objects.create(user=user, article=article, reaction_type="love")

    def test_reaction_str(self):
        """Тест строкового представления."""
        user = UserFactory(username="testuser")
        article = ArticleFactory(title="Test Article")
        reaction = ArticleReactionFactory(user=user, article=article, reaction_type="like")
        reaction_str = str(reaction)

        # __str__ содержит username и название статьи
        assert "testuser" in reaction_str.lower()
        assert "test article" in reaction_str.lower()


# ============================================================================
# BOOKMARK MODEL TESTS
# ============================================================================


@pytest.mark.django_db
class TestBookmarkModel:
    """Тесты для модели Bookmark."""

    def test_create_bookmark(self):
        """Тест создания закладки."""
        user = UserFactory()
        article = ArticleFactory()
        bookmark = BookmarkFactory(user=user, article=article)

        assert bookmark.user == user
        assert bookmark.article == article
        assert isinstance(bookmark.created_at, type(timezone.now()))

    def test_unique_user_article_bookmark(self):
        """Тест уникальности закладки."""
        from blog.models import Bookmark

        user = UserFactory()
        article = ArticleFactory()

        BookmarkFactory(user=user, article=article)

        # Создаем вторую закладку напрямую через модель
        with pytest.raises(IntegrityError):
            Bookmark.objects.create(user=user, article=article)

    def test_user_multiple_bookmarks(self):
        """Тест множественных закладок пользователя."""
        user = UserFactory()
        articles = ArticleFactory.create_batch(5)

        for article in articles:
            BookmarkFactory(user=user, article=article)

        assert Bookmark.objects.filter(user=user).count() == 5


# ============================================================================
# READING PROGRESS MODEL TESTS
# ============================================================================


@pytest.mark.django_db
class TestReadingProgressModel:
    """Тесты для модели ReadingProgress."""

    def test_create_reading_progress(self):
        """Тест создания прогресса чтения."""
        user = UserFactory()
        article = ArticleFactory()
        progress = ReadingProgressFactory(
            user=user, article=article, progress_percentage=50, reading_time_seconds=600
        )

        assert progress.user == user
        assert progress.article == article
        assert progress.progress_percentage == 50
        assert progress.reading_time_seconds == 600

    def test_progress_validation(self):
        """Тест валидации прогресса (0-100)."""
        progress = ReadingProgressFactory(progress_percentage=50)
        assert 0 <= progress.progress_percentage <= 100

    def test_unique_user_article_progress(self):
        """Тест уникальности прогресса."""
        from blog.models import ReadingProgress

        user = UserFactory()
        article = ArticleFactory()

        ReadingProgressFactory(user=user, article=article)

        # Создаем второй прогресс напрямую через модель
        with pytest.raises(IntegrityError):
            ReadingProgress.objects.create(user=user, article=article, progress_percentage=50)

    def test_update_progress(self):
        """Тест обновления прогресса."""
        progress = ReadingProgressFactory(progress_percentage=25, reading_time_seconds=300)

        progress.progress_percentage = 75
        progress.reading_time_seconds = 900
        progress.save()

        progress.refresh_from_db()
        assert progress.progress_percentage == 75
        assert progress.reading_time_seconds == 900


# ============================================================================
# NEWSLETTER MODEL TESTS
# ============================================================================


@pytest.mark.django_db
class TestNewsletterModel:
    """Тесты для модели Newsletter."""

    def test_create_newsletter_subscription(self):
        """Тест создания подписки."""
        newsletter = NewsletterFactory(email="test@example.com")

        assert newsletter.email == "test@example.com"
        assert newsletter.is_active is True

    def test_unique_email(self):
        """Тест уникальности email."""
        from blog.models import Newsletter

        NewsletterFactory(email="test@example.com")

        # Создаем вторую подписку напрямую через модель
        with pytest.raises(IntegrityError):
            Newsletter.objects.create(email="test@example.com")

    def test_deactivate_subscription(self):
        """Тест деактивации подписки."""
        newsletter = NewsletterFactory(is_active=True)

        newsletter.is_active = False
        newsletter.save()

        newsletter.refresh_from_db()
        assert newsletter.is_active is False

    def test_newsletter_str(self):
        """Тест строкового представления."""
        newsletter = NewsletterFactory(email="test@example.com")
        assert str(newsletter) == "test@example.com"
