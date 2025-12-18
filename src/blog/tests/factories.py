"""
Factory Boy Factories для тестовых данных.

Этот модуль содержит фабрики для создания тестовых объектов моделей.
Factory Boy позволяет легко создавать сложные объекты с минимальным кодом.

Использование:
    >>> from blog.tests.factories import ArticleFactory
    >>> article = ArticleFactory()
    >>> article.title
    'Test Article 1'

    >>> # С кастомными параметрами
    >>> article = ArticleFactory(title='My Custom Title', status='published')

    >>> # Создание множества объектов
    >>> articles = ArticleFactory.create_batch(10)
"""

from __future__ import annotations

import factory
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.text import slugify
from factory import Faker, SubFactory, post_generation
from factory.django import DjangoModelFactory

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

User = get_user_model()

# ============================================================================
# USER FACTORY
# ============================================================================


class UserFactory(DjangoModelFactory):
    """Фабрика для создания пользователей."""

    class Meta:
        model = User
        django_get_or_create = ("username",)

    username = Faker("user_name")
    email = Faker("email")
    first_name = Faker("first_name")
    last_name = Faker("last_name")
    is_active = True
    is_staff = False
    is_superuser = False

    @factory.lazy_attribute
    def password(self):
        """Хэшированный пароль."""
        return factory.django.Password("testpass123")


class StaffUserFactory(UserFactory):
    """Фабрика для staff пользователей."""

    is_staff = True


class SuperUserFactory(UserFactory):
    """Фабрика для суперпользователей."""

    is_staff = True
    is_superuser = True


# ============================================================================
# CATEGORY FACTORY
# ============================================================================


class CategoryFactory(DjangoModelFactory):
    """Фабрика для создания категорий."""

    class Meta:
        model = Category
        django_get_or_create = ("slug",)

    name = Faker("word")
    description = Faker("text", max_nb_chars=200)
    icon = factory.Iterator(["📝", "🐍", "💻", "🚀", "🔥", "⚡", "🎯", "📚"])
    color = factory.Iterator(["#3498db", "#e74c3c", "#2ecc71", "#f39c12", "#9b59b6"])
    badge = Faker("word")
    order = factory.Sequence(lambda n: n)

    @factory.lazy_attribute
    def slug(self):
        """Автоматическая генерация slug из названия."""
        return slugify(self.name)


# ============================================================================
# SERIES FACTORY
# ============================================================================


class SeriesFactory(DjangoModelFactory):
    """Фабрика для создания серий статей."""

    class Meta:
        model = Series

    title = Faker("sentence", nb_words=4)
    description = Faker("text", max_nb_chars=300)
    status = "active"
    author = SubFactory(UserFactory)
    is_featured = False

    @factory.lazy_attribute
    def slug(self):
        """Автоматическая генерация slug из заголовка."""
        return slugify(self.title)


# ============================================================================
# ARTICLE FACTORY
# ============================================================================


class ArticleFactory(DjangoModelFactory):
    """Фабрика для создания статей."""

    class Meta:
        model = Article
        django_get_or_create = ("slug",)

    title = Faker("sentence", nb_words=6)
    content = Faker("text", max_nb_chars=2000)
    excerpt = Faker("text", max_nb_chars=200)
    author = SubFactory(UserFactory)
    category = SubFactory(CategoryFactory)
    series = None
    series_order = None

    status = "published"
    difficulty = factory.Iterator(["beginner", "intermediate", "advanced"])
    reading_time = factory.Faker("random_int", min=1, max=30)

    is_featured = False
    allow_comments = True

    views_count = factory.Faker("random_int", min=0, max=1000)

    published_at = factory.LazyFunction(timezone.now)

    @factory.lazy_attribute
    def slug(self):
        """Автоматическая генерация slug из заголовка."""
        return slugify(self.title)

    @post_generation
    def tags(self, create, extracted, **kwargs):
        """
        Добавление тегов к статье.

        Usage:
            ArticleFactory(tags=['python', 'django'])
        """
        if not create:
            return

        if extracted:
            from taggit.models import Tag

            for tag_name in extracted:
                tag, _ = Tag.objects.get_or_create(name=tag_name, slug=slugify(tag_name))
                self.tags.add(tag)


class DraftArticleFactory(ArticleFactory):
    """Фабрика для черновиков статей."""

    status = "draft"
    published_at = None


class FeaturedArticleFactory(ArticleFactory):
    """Фабрика для избранных статей."""

    is_featured = True
    views_count = factory.Faker("random_int", min=500, max=5000)


class ArticleInSeriesFactory(ArticleFactory):
    """Фабрика для статей в серии."""

    series = SubFactory(SeriesFactory)
    series_order = factory.Sequence(lambda n: n + 1)


# ============================================================================
# COMMENT FACTORY
# ============================================================================


class CommentFactory(DjangoModelFactory):
    """Фабрика для создания комментариев."""

    class Meta:
        model = Comment

    article = SubFactory(ArticleFactory)
    author = SubFactory(UserFactory)
    content = Faker("text", max_nb_chars=500)
    parent = None
    is_approved = True


class ReplyCommentFactory(CommentFactory):
    """Фабрика для ответов на комментарии."""

    parent = SubFactory(CommentFactory)


# ============================================================================
# REACTION FACTORY
# ============================================================================


class ArticleReactionFactory(DjangoModelFactory):
    """Фабрика для создания реакций на статьи."""

    class Meta:
        model = ArticleReaction
        django_get_or_create = ("user", "article")

    user = SubFactory(UserFactory)
    article = SubFactory(ArticleFactory)
    reaction_type = factory.Iterator(["like", "love", "helpful", "insightful", "amazing"])


# ============================================================================
# BOOKMARK FACTORY
# ============================================================================


class BookmarkFactory(DjangoModelFactory):
    """Фабрика для создания закладок."""

    class Meta:
        model = Bookmark
        django_get_or_create = ("user", "article")

    user = SubFactory(UserFactory)
    article = SubFactory(ArticleFactory)


# ============================================================================
# READING PROGRESS FACTORY
# ============================================================================


class ReadingProgressFactory(DjangoModelFactory):
    """Фабрика для создания прогресса чтения."""

    class Meta:
        model = ReadingProgress
        django_get_or_create = ("user", "article")

    user = SubFactory(UserFactory)
    article = SubFactory(ArticleFactory)
    progress_percentage = factory.Faker("random_int", min=0, max=100)
    reading_time_seconds = factory.Faker("random_int", min=0, max=3600)
    status = factory.Iterator(["not_started", "in_progress", "completed"])


# ============================================================================
# NEWSLETTER FACTORY
# ============================================================================


class NewsletterFactory(DjangoModelFactory):
    """Фабрика для создания подписок на newsletter."""

    class Meta:
        model = Newsletter
        django_get_or_create = ("email",)

    email = Faker("email")
    is_active = True


# ============================================================================
# BATCH CREATION HELPERS
# ============================================================================


def create_blog_with_articles(
    num_categories: int = 3, num_articles_per_category: int = 5, num_users: int = 3
) -> dict:
    """
    Создание полного блога с категориями, статьями и пользователями.

    Args:
        num_categories: Количество категорий
        num_articles_per_category: Количество статей в каждой категории
        num_users: Количество пользователей-авторов

    Returns:
        dict: Словарь с созданными объектами

    Example:
        >>> blog = create_blog_with_articles(3, 5, 2)
        >>> len(blog['articles'])
        15
    """
    # Создание пользователей
    users = UserFactory.create_batch(num_users)

    # Создание категорий
    categories = CategoryFactory.create_batch(num_categories)

    # Создание статей
    import random

    articles = []
    for category in categories:
        for _ in range(num_articles_per_category):
            article = ArticleFactory(category=category, author=random.choice(users))
            articles.append(article)

    return {"users": users, "categories": categories, "articles": articles}


def create_article_with_engagement(
    num_comments: int = 5, num_reactions: int = 10, num_bookmarks: int = 3
) -> dict:
    """
    Создание статьи со всеми типами взаимодействия.

    Args:
        num_comments: Количество комментариев
        num_reactions: Количество реакций
        num_bookmarks: Количество закладок

    Returns:
        dict: Словарь с статьей и связанными объектами

    Example:
        >>> data = create_article_with_engagement(5, 10, 3)
        >>> article = data['article']
        >>> len(data['comments'])
        5
    """
    article = ArticleFactory()

    # Создание комментариев
    comments = CommentFactory.create_batch(num_comments, article=article)

    # Создание реакций
    reactions = []
    for _ in range(num_reactions):
        user = UserFactory()
        reaction = ArticleReactionFactory(article=article, user=user)
        reactions.append(reaction)

    # Создание закладок
    bookmarks = []
    for _ in range(num_bookmarks):
        user = UserFactory()
        bookmark = BookmarkFactory(article=article, user=user)
        bookmarks.append(bookmark)

    # Создание прогресса чтения
    progress = ReadingProgressFactory(article=article)

    return {
        "article": article,
        "comments": comments,
        "reactions": reactions,
        "bookmarks": bookmarks,
        "progress": progress,
    }
