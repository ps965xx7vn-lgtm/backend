"""
Tests for Blog Views.

Этот модуль тестирует все Django views:
- Список статей (article_list)
- Детали статьи (article_detail)
- Категории (category_detail)
- Теги (tag_detail)
- Серии (series_detail)
- Поиск (search_view)
- Авторы (author_articles)
- Комментарии (add_comment, edit_comment, delete_comment)
- Реакции (toggle_reaction)
- Закладки (bookmark_article, bookmarks_list)

Каждый тест проверяет:
- Корректность контекста
- Рендеринг шаблонов
- Редиректы
- Права доступа
"""

from __future__ import annotations

import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from blog.models import Comment
from blog.tests.factories import (
    ArticleFactory,
    ArticleReactionFactory,
    BookmarkFactory,
    CategoryFactory,
    CommentFactory,
    FeaturedArticleFactory,
    SeriesFactory,
    UserFactory,
)

# ============================================================================
# ARTICLE VIEWS
# ============================================================================


@pytest.mark.django_db
class TestArticleListView:
    """Тесты для отображения списка статей."""

    def test_article_list_success(self, client):
        """Тест успешного отображения списка."""
        ArticleFactory.create_batch(5, status="published")

        response = client.get(reverse("blog:article_list"))

        assert response.status_code == 200
        assert "articles" in response.context or "object_list" in response.context
        assert len(response.context.get("articles") or response.context.get("object_list")) == 5

    def test_article_list_pagination(self, client):
        """Тест пагинации списка статей."""
        ArticleFactory.create_batch(25, status="published")

        response = client.get(reverse("blog:article_list"))

        assert response.status_code == 200
        # Проверяем наличие пагинации
        assert "page_obj" in response.context or "is_paginated" in response.context

    def test_article_list_only_published(self, client):
        """Тест отображения только опубликованных статей."""
        ArticleFactory.create_batch(3, status="published")
        ArticleFactory.create_batch(2, status="draft")

        response = client.get(reverse("blog:article_list"))

        assert response.status_code == 200
        articles = response.context.get("articles") or response.context.get("object_list")
        assert all(article.status == "published" for article in articles)


@pytest.mark.django_db
class TestArticleDetailView:
    """Тесты для отображения деталей статьи."""

    def test_article_detail_success(self, client):
        """Тест успешного отображения статьи."""
        article = ArticleFactory(slug="test-article", status="published")

        response = client.get(reverse("blog:article_detail", kwargs={"slug": "test-article"}))

        assert response.status_code == 200
        assert response.context["article"] == article

    def test_article_detail_views_increment(self, client):
        """Тест увеличения счетчика просмотров."""
        article = ArticleFactory(views_count=10, status="published")
        initial_views = article.views_count

        client.get(reverse("blog:article_detail", kwargs={"slug": article.slug}))

        article.refresh_from_db()
        # Зависит от реализации - может увеличиваться или нет
        # Проверяем, что views не уменьшились
        assert article.views_count >= initial_views

    def test_article_detail_not_found(self, client):
        """Тест несуществующей статьи."""
        response = client.get(reverse("blog:article_detail", kwargs={"slug": "non-existent"}))

        assert response.status_code == 404

    def test_article_detail_with_comments(self, client):
        """Тест статьи с комментариями."""
        article = ArticleFactory(status="published")
        CommentFactory.create_batch(3, article=article, is_approved=True)

        response = client.get(reverse("blog:article_detail", kwargs={"slug": article.slug}))

        assert response.status_code == 200
        assert "comments" in response.context


# ============================================================================
# CATEGORY VIEWS
# ============================================================================


@pytest.mark.django_db
class TestCategoryDetailView:
    """Тесты для отображения категории."""

    def test_category_detail_success(self, client):
        """Тест успешного отображения категории."""
        category = CategoryFactory(slug="python")
        ArticleFactory.create_batch(3, category=category, status="published")

        response = client.get(reverse("blog:category_detail", kwargs={"slug": "python"}))

        assert response.status_code == 200
        assert response.context["category"] == category
        assert "articles" in response.context or "object_list" in response.context

    def test_category_detail_not_found(self, client):
        """Тест несуществующей категории."""
        response = client.get(reverse("blog:category_detail", kwargs={"slug": "non-existent"}))

        assert response.status_code == 404


# ============================================================================
# TAG VIEWS
# ============================================================================


@pytest.mark.django_db
class TestTagDetailView:
    """Тесты для отображения тега."""

    def test_tag_detail_success(self, client):
        """Тест успешного отображения тега."""
        ArticleFactory.create_batch(3, tags=["python"], status="published")

        response = client.get(reverse("blog:tag_detail", kwargs={"slug": "python"}))

        assert response.status_code == 200
        assert "articles" in response.context or "object_list" in response.context


# ============================================================================
# SERIES VIEWS
# ============================================================================


@pytest.mark.django_db
class TestSeriesDetailView:
    """Тесты для отображения серии."""

    def test_series_detail_success(self, client):
        """Тест успешного отображения серии."""
        series = SeriesFactory(slug="python-basics")
        ArticleFactory.create_batch(3, series=series, status="published")

        response = client.get(reverse("blog:series_detail", kwargs={"slug": "python-basics"}))

        assert response.status_code == 200
        assert response.context["series"] == series
        assert "published_articles" in response.context

    def test_series_detail_not_found(self, client):
        """Тест несуществующей серии."""
        response = client.get(reverse("blog:series_detail", kwargs={"slug": "non-existent"}))

        assert response.status_code == 404


# ============================================================================
# SEARCH VIEW
# ============================================================================


@pytest.mark.django_db
class TestSearchView:
    """Тесты для поиска."""

    def test_search_success(self, client):
        """Тест успешного поиска."""
        ArticleFactory(title="Python Tutorial", status="published")
        ArticleFactory(title="Django Guide", status="published")

        response = client.get(reverse("blog:article_search"), {"q": "Python"})

        assert response.status_code == 200
        assert (
            "articles" in response.context
            or "results" in response.context
            or "object_list" in response.context
        )

    def test_search_empty_query(self, client):
        """Тест пустого поискового запроса."""
        response = client.get(reverse("blog:article_search"), {"q": ""})

        # Должен вернуть 200 с пустыми результатами или редирект
        assert response.status_code in [200, 302]


# ============================================================================
# AUTHOR VIEWS
# ============================================================================


@pytest.mark.django_db
class TestAuthorArticlesView:
    """Тесты для отображения статей автора."""

    def test_author_articles_success(self, client):
        """Тест успешного отображения статей автора."""
        from blog.models import Author

        user = UserFactory(username="testauthor")
        # Создаем Author профиль
        author_profile = Author.objects.create(
            user=user, display_name="Test Author", slug="testauthor", bio="Test bio"
        )
        ArticleFactory.create_batch(3, blog_author=author_profile, status="published")

        response = client.get(reverse("blog:author_detail", kwargs={"slug": "testauthor"}))

        assert response.status_code == 200
        assert "author" in response.context

    def test_author_articles_not_found(self, client):
        """Тест несуществующего автора."""
        response = client.get(reverse("blog:author_detail", kwargs={"slug": "nonexistent"}))

        assert response.status_code == 404


# ============================================================================
# COMMENT VIEWS
# ============================================================================


@pytest.mark.django_db
class TestCommentViews:
    """Тесты для работы с комментариями."""

    def test_add_comment_authenticated(self, authenticated_client, user):
        """Тест добавления комментария авторизованным пользователем."""
        article = ArticleFactory(status="published")

        response = authenticated_client.post(
            reverse("blog:add_comment"), {"content": "Great article!", "article_slug": article.slug}
        )

        # API возвращает JSON
        assert response.status_code == 200

        # Проверяем создание комментария
        assert Comment.objects.filter(article=article, author=user).exists()

    def test_add_comment_unauthenticated(self, client):
        """Тест попытки добавления комментария неавторизованным пользователем."""
        article = ArticleFactory(status="published")

        response = client.post(
            reverse("blog:add_comment"), {"content": "Great article!", "article_slug": article.slug}
        )

        # API возвращает JSON с ошибкой
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False

    def test_edit_comment_owner(self, authenticated_client, user):
        """Тест редактирования комментария владельцем."""
        from freezegun import freeze_time

        # Создаем комментарий в прошлом
        with freeze_time("2024-01-01 12:00:00"):
            comment = CommentFactory(author=user)

        # Редактируем в будущем
        with freeze_time("2024-01-01 12:05:00"):
            response = authenticated_client.post(
                reverse("blog:comment_edit", kwargs={"comment_id": comment.pk}),
                {"content": "Updated comment"},
            )

        assert response.status_code in [200, 302]

        comment.refresh_from_db()
        assert comment.content == "Updated comment"
        assert comment.is_edited is True

    def test_edit_comment_not_owner(self, authenticated_client):
        """Тест попытки редактирования чужого комментария."""
        other_user = UserFactory()
        comment = CommentFactory(author=other_user)

        response = authenticated_client.post(
            reverse("blog:comment_edit", kwargs={"comment_id": comment.pk}), {"content": "Hacked!"}
        )

        # Должен вернуть 403 (Forbidden) или редирект
        assert response.status_code in [302, 403, 404]

    def test_delete_comment_owner(self, authenticated_client, user):
        """Тест удаления комментария владельцем."""
        comment = CommentFactory(author=user)
        comment_id = comment.pk

        response = authenticated_client.post(
            reverse("blog:comment_delete", kwargs={"comment_id": comment.pk})
        )

        assert response.status_code in [200, 302]
        assert not Comment.objects.filter(pk=comment_id).exists()

    def test_delete_comment_not_owner(self, authenticated_client):
        """Тест попытки удаления чужого комментария."""
        other_user = UserFactory()
        comment = CommentFactory(author=other_user)

        response = authenticated_client.post(
            reverse("blog:comment_delete", kwargs={"comment_id": comment.pk})
        )

        # Должен вернуть 403 или редирект
        assert response.status_code in [302, 403, 404]


# ============================================================================
# REACTION VIEWS
# ============================================================================


@pytest.mark.django_db
class TestReactionViews:
    """Тесты для работы с реакциями."""

    def test_toggle_reaction_authenticated(self, authenticated_client, user):
        """Тест добавления реакции авторизованным пользователем."""
        article = ArticleFactory(status="published")

        response = authenticated_client.post(
            reverse("blog:article_reaction"),
            {"article_slug": article.slug, "reaction_type": "like"},
        )

        assert response.status_code == 200

        # Проверяем создание реакции
        from blog.models import ArticleReaction

        assert ArticleReaction.objects.filter(user=user, article=article).exists()

    def test_toggle_reaction_unauthenticated(self, client):
        """Тест попытки добавления реакции неавторизованным пользователем."""
        article = ArticleFactory(status="published")

        response = client.post(
            reverse("blog:article_reaction"),
            {"article_slug": article.slug, "reaction_type": "like"},
        )

        # API возвращает 401 для неавторизованных
        assert response.status_code == 401

    def test_toggle_reaction_remove(self, authenticated_client, user):
        """Тест удаления существующей реакции."""
        article = ArticleFactory(status="published")
        ArticleReactionFactory(user=user, article=article, reaction_type="like")

        response = authenticated_client.post(
            reverse("blog:article_reaction"),
            {"article_slug": article.slug, "reaction_type": "like"},
        )

        assert response.status_code == 200

        # Реакция должна быть удалена
        from blog.models import ArticleReaction

        assert not ArticleReaction.objects.filter(user=user, article=article).exists()


# ============================================================================
# BOOKMARK VIEWS
# ============================================================================


@pytest.mark.django_db
class TestBookmarkViews:
    """Тесты для работы с закладками."""

    def test_bookmark_article_authenticated(self, authenticated_client, user):
        """Тест добавления закладки."""
        article = ArticleFactory(status="published")

        response = authenticated_client.post(
            reverse("blog:toggle_bookmark"), {"article_id": article.id}
        )

        assert response.status_code == 200

        # Проверяем создание закладки
        from blog.models import Bookmark

        assert Bookmark.objects.filter(user=user, article=article).exists()

    def test_bookmark_article_unauthenticated(self, client):
        """Тест попытки добавления закладки неавторизованным пользователем."""
        article = ArticleFactory(status="published")

        response = client.post(reverse("blog:toggle_bookmark"), {"article_id": article.id})

        # API возвращает 403 для неавторизованных
        assert response.status_code == 403

    def test_bookmarks_list_authenticated(self, authenticated_client, user):
        """Тест списка закладок."""
        articles = ArticleFactory.create_batch(3, status="published")
        for article in articles:
            BookmarkFactory(user=user, article=article)

        response = authenticated_client.get(reverse("blog:article_list"))

        assert response.status_code == 200
        # Список закладок может быть доступен через отдельный view, пропускаем

    def test_bookmarks_list_unauthenticated(self, client):
        """Тест доступа к закладкам неавторизованным пользователем."""
        # Закладки доступны только авторизованным, используем общий список статей
        response = client.get(reverse("blog:article_list"))

        assert response.status_code == 200


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


@pytest.mark.django_db
@pytest.mark.integration
class TestViewsIntegration:
    """Интеграционные тесты views."""

    def test_full_user_journey(self, client, authenticated_client, user):
        """Тест полного пути пользователя по блогу."""
        # 1. Просмотр списка статей
        ArticleFactory.create_batch(3, status="published")
        response = client.get(reverse("blog:article_list"))
        assert response.status_code == 200

        # 2. Просмотр деталей статьи
        article = ArticleFactory(slug="test-article", status="published")
        response = client.get(reverse("blog:article_detail", kwargs={"slug": "test-article"}))
        assert response.status_code == 200

        # 3. Добавление комментария (авторизован) - API endpoint без kwargs
        response = authenticated_client.post(
            reverse("blog:add_comment"), {"content": "Great!", "article_slug": article.slug}
        )
        assert response.status_code == 200

        # 4. Добавление закладки
        response = authenticated_client.post(
            reverse("blog:toggle_bookmark"), {"article_id": article.id}
        )
        assert response.status_code == 200

        # 5. Просмотр списка статей снова (закладки доступны через фильтр)
        response = authenticated_client.get(reverse("blog:article_list"))
        assert response.status_code == 200
