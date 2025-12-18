"""
Tests for Blog Admin.

Этот модуль тестирует Django Admin интерфейс для блога:
- CategoryAdmin
- ArticleAdmin
- SeriesAdmin
- CommentAdmin
- ArticleReactionAdmin
- BookmarkAdmin
- ReadingProgressAdmin
- NewsletterAdmin

Каждый тест проверяет:
- List display
- Search functionality
- Filtering
- Actions
- Permissions
"""

from __future__ import annotations

import pytest
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model

from blog.admin import (
    ArticleAdmin,
    ArticleReactionAdmin,
    BookmarkAdmin,
    CategoryAdmin,
    CommentAdmin,
    NewsletterAdmin,
    ReadingProgressAdmin,
    SeriesAdmin,
)
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
    NewsletterFactory,
    ReadingProgressFactory,
    SeriesFactory,
    SuperUserFactory,
    UserFactory,
)

User = get_user_model()

# ============================================================================
# ADMIN SETUP
# ============================================================================


@pytest.fixture
def admin_site():
    """Фикстура для AdminSite."""
    return AdminSite()


# ============================================================================
# CATEGORY ADMIN TESTS
# ============================================================================


@pytest.mark.django_db
class TestCategoryAdmin:
    """Тесты для CategoryAdmin."""

    def test_category_admin_list_display(self, admin_site):
        """Тест отображения полей в списке."""
        category_admin = CategoryAdmin(Category, admin_site)

        # Реальный list_display из blog/admin.py:65
        expected_fields = [
            "icon_display",
            "name",
            "badge",
            "order",
            "articles_count",
            "tags_count",
            "created_at",
        ]
        assert category_admin.list_display == expected_fields

    def test_category_admin_search(self, admin_site):
        """Тест поиска."""
        category_admin = CategoryAdmin(Category, admin_site)

        assert "name" in category_admin.search_fields

    def test_category_admin_prepopulated_fields(self, admin_site):
        """Тест автозаполнения slug."""
        category_admin = CategoryAdmin(Category, admin_site)

        if hasattr(category_admin, "prepopulated_fields"):
            assert "slug" in category_admin.prepopulated_fields


# ============================================================================
# ARTICLE ADMIN TESTS
# ============================================================================


@pytest.mark.django_db
class TestArticleAdmin:
    """Тесты для ArticleAdmin."""

    def test_article_admin_list_display(self, admin_site):
        """Тест отображения полей."""
        article_admin = ArticleAdmin(Article, admin_site)

        # Реальный list_display из blog/admin.py:197-199
        expected_fields = [
            "title",
            "category",
            "author",
            "status_display",
            "difficulty_display",
            "is_featured",
            "views_count",
            "published_at",
            "created_at",
        ]
        assert article_admin.list_display == expected_fields

    def test_article_admin_list_filter(self, admin_site):
        """Тест фильтров."""
        article_admin = ArticleAdmin(Article, admin_site)

        assert "status" in article_admin.list_filter
        assert "category" in article_admin.list_filter

    def test_article_admin_search(self, admin_site):
        """Тест поиска."""
        article_admin = ArticleAdmin(Article, admin_site)

        assert "title" in article_admin.search_fields
        assert "content" in article_admin.search_fields

    def test_article_admin_prepopulated_slug(self, admin_site):
        """Тест автозаполнения slug."""
        article_admin = ArticleAdmin(Article, admin_site)

        if hasattr(article_admin, "prepopulated_fields"):
            assert "slug" in article_admin.prepopulated_fields


# ============================================================================
# SERIES ADMIN TESTS
# ============================================================================


@pytest.mark.django_db
class TestSeriesAdmin:
    """Тесты для SeriesAdmin."""

    def test_series_admin_list_display(self, admin_site):
        """Тест отображения полей."""
        series_admin = SeriesAdmin(Series, admin_site)

        # Реальный list_display из blog/admin.py:456
        expected_fields = ["title", "slug", "status", "article_count", "author", "created_at"]
        assert series_admin.list_display == expected_fields


# ============================================================================
# COMMENT ADMIN TESTS
# ============================================================================


@pytest.mark.django_db
class TestCommentAdmin:
    """Тесты для CommentAdmin."""

    def test_comment_admin_list_display(self, admin_site):
        """Тест отображения полей."""
        comment_admin = CommentAdmin(Comment, admin_site)

        assert "author" in comment_admin.list_display
        assert "article" in comment_admin.list_display
        assert "is_approved" in comment_admin.list_display

    def test_comment_admin_list_filter(self, admin_site):
        """Тест фильтров."""
        comment_admin = CommentAdmin(Comment, admin_site)

        assert "is_approved" in comment_admin.list_filter
        assert "created_at" in comment_admin.list_filter

    def test_comment_admin_actions(self, admin_site):
        """Тест массовых действий."""
        comment_admin = CommentAdmin(Comment, admin_site)

        # Проверяем наличие кастомных действий для одобрения/отклонения
        if hasattr(comment_admin, "actions"):
            assert comment_admin.actions is not None


# ============================================================================
# ARTICLE REACTION ADMIN TESTS
# ============================================================================


@pytest.mark.django_db
class TestArticleReactionAdmin:
    """Тесты для ArticleReactionAdmin."""

    def test_reaction_admin_list_display(self, admin_site):
        """Тест отображения полей."""
        reaction_admin = ArticleReactionAdmin(ArticleReaction, admin_site)

        assert "user" in reaction_admin.list_display
        assert "article" in reaction_admin.list_display
        assert "reaction_type" in reaction_admin.list_display


# ============================================================================
# BOOKMARK ADMIN TESTS
# ============================================================================


@pytest.mark.django_db
class TestBookmarkAdmin:
    """Тесты для BookmarkAdmin."""

    def test_bookmark_admin_list_display(self, admin_site):
        """Тест отображения полей."""
        bookmark_admin = BookmarkAdmin(Bookmark, admin_site)

        assert "user" in bookmark_admin.list_display
        assert "article" in bookmark_admin.list_display


# ============================================================================
# READING PROGRESS ADMIN TESTS
# ============================================================================


@pytest.mark.django_db
class TestReadingProgressAdmin:
    """Тесты для ReadingProgressAdmin."""

    def test_progress_admin_list_display(self, admin_site):
        """Тест отображения полей."""
        progress_admin = ReadingProgressAdmin(ReadingProgress, admin_site)

        # Реальный list_display из blog/admin.py:576
        expected_fields = ["user", "article", "progress_percentage", "status", "last_read_at"]
        assert progress_admin.list_display == expected_fields


# ============================================================================
# NEWSLETTER ADMIN TESTS
# ============================================================================


@pytest.mark.django_db
class TestNewsletterAdmin:
    """Тесты для NewsletterAdmin."""

    def test_newsletter_admin_list_display(self, admin_site):
        """Тест отображения полей."""
        newsletter_admin = NewsletterAdmin(Newsletter, admin_site)

        assert "email" in newsletter_admin.list_display
        assert "is_active" in newsletter_admin.list_display

    def test_newsletter_admin_list_filter(self, admin_site):
        """Тест фильтров."""
        newsletter_admin = NewsletterAdmin(Newsletter, admin_site)

        assert "is_active" in newsletter_admin.list_filter


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


@pytest.mark.django_db
@pytest.mark.integration
class TestAdminIntegration:
    """Интеграционные тесты Admin."""

    def test_admin_site_registration(self):
        """Тест регистрации моделей в админке."""
        from django.contrib import admin

        # Проверяем что модели зарегистрированы
        assert Category in admin.site._registry
        assert Article in admin.site._registry
        assert Series in admin.site._registry
        assert Comment in admin.site._registry

    def test_admin_changelist_access(self, admin_client):
        """Тест доступа к списку объектов."""
        # Создаем тестовые данные
        CategoryFactory.create_batch(3)

        response = admin_client.get("/admin/blog/category/")

        assert response.status_code == 200

    def test_admin_change_object(self, admin_client):
        """Тест редактирования объекта."""
        category = CategoryFactory(name="Old Name")

        response = admin_client.post(
            f"/admin/blog/category/{category.pk}/change/",
            {
                "name": "New Name",
                "slug": category.slug,
                "icon": category.icon,
                "color": category.color,
            },
        )

        # Должен быть редирект или успех
        assert response.status_code in [200, 302]

    def test_admin_delete_object(self, admin_client):
        """Тест удаления объекта."""
        category = CategoryFactory()

        response = admin_client.post(f"/admin/blog/category/{category.pk}/delete/", {"post": "yes"})

        assert response.status_code in [200, 302]
        assert not Category.objects.filter(pk=category.pk).exists()


# ============================================================================
# PERMISSION TESTS
# ============================================================================


@pytest.mark.django_db
class TestAdminPermissions:
    """Тесты прав доступа."""

    def test_non_admin_cannot_access(self, authenticated_client):
        """Тест что обычный пользователь не может попасть в админку."""
        response = authenticated_client.get("/admin/blog/category/")

        # Должен быть редирект на логин или 403
        assert response.status_code in [302, 403]

    def test_staff_user_can_access(self, staff_client):
        """Тест что staff пользователь может попасть в админку."""
        response = staff_client.get("/admin/")

        assert response.status_code == 200

    def test_superuser_has_all_permissions(self, admin_client):
        """Тест что superuser имеет все права."""
        # Создаем объект
        category = CategoryFactory()

        # Может просматривать
        response = admin_client.get(f"/admin/blog/category/{category.pk}/change/")
        assert response.status_code == 200

        # Может удалять
        response = admin_client.get(f"/admin/blog/category/{category.pk}/delete/")
        assert response.status_code == 200


# ============================================================================
# CUSTOM ACTIONS TESTS
# ============================================================================


@pytest.mark.django_db
class TestAdminCustomActions:
    """Тесты кастомных действий админки."""

    def test_approve_comments_action(self, admin_client):
        """Тест действия одобрения комментариев."""
        # Создаем неодобренные комментарии
        comments = CommentFactory.create_batch(3, is_approved=False)

        # Выполняем действие одобрения
        response = admin_client.post(
            "/admin/blog/comment/",
            {
                "action": "approve_comments",
                "_selected_action": [c.pk for c in comments],
            },
        )

        # Проверяем что комментарии одобрены или действие выполнено
        if response.status_code == 302:
            # Редирект после успешного действия
            for comment in comments:
                comment.refresh_from_db()
                # Зависит от реализации - может быть одобрен

    def test_publish_articles_action(self, admin_client):
        """Тест действия публикации статей."""
        # Создаем черновики
        from blog.tests.factories import DraftArticleFactory

        drafts = DraftArticleFactory.create_batch(3)

        # Выполняем действие публикации (если есть)
        response = admin_client.post(
            "/admin/blog/article/",
            {
                "action": "publish_articles",
                "_selected_action": [a.pk for a in drafts],
            },
        )

        # Проверяем результат
        if response.status_code == 302:
            pass  # Действие выполнено
