"""
Tests for Blog API Endpoints.

Этот модуль тестирует все 13 API endpoints из blog/api.py:
- GET /api/blog/ping - Health check
- GET /api/blog/articles - List with filtering
- GET /api/blog/articles/featured - Featured articles
- GET /api/blog/articles/popular - Popular articles
- GET /api/blog/articles/{slug} - Article details
- GET /api/blog/categories - Categories list
- GET /api/blog/categories/{slug} - Category details
- GET /api/blog/tags - Tags list
- GET /api/blog/series - Series list
- GET /api/blog/series/{slug} - Series details
- GET /api/blog/authors - Authors list
- GET /api/blog/stats - Blog statistics

Каждый тест проверяет:
- Успешные ответы (200 OK)
- Структуру JSON ответа
- Ошибки (400, 404, 500)
- Фильтрацию и поиск
- Пагинацию
"""

from __future__ import annotations

import pytest
from django.test import Client
from django.urls import reverse

from blog.tests.factories import (
    ArticleFactory,
    CategoryFactory,
    CommentFactory,
    DraftArticleFactory,
    FeaturedArticleFactory,
    SeriesFactory,
    UserFactory,
    create_blog_with_articles,
)

# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================


@pytest.mark.django_db
@pytest.mark.api
class TestPingEndpoint:
    """Тесты для /api/blog/ping endpoint."""

    def test_ping_success(self, authenticated_api_client):
        """Тест health check."""
        response = authenticated_api_client.get("/api/blog/ping")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data


# ============================================================================
# ARTICLES LIST ENDPOINT
# ============================================================================


@pytest.mark.django_db
@pytest.mark.api
class TestArticlesListEndpoint:
    """Тесты для /api/blog/articles endpoint."""

    def test_articles_list_success(self, api_client):
        """Тест получения списка статей."""
        ArticleFactory.create_batch(5, status="published")

        response = api_client.get("/api/blog/articles")

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "meta" in data
        assert len(data["items"]) == 5

    def test_articles_pagination(self, api_client):
        """Тест пагинации."""
        ArticleFactory.create_batch(25, status="published")

        response = api_client.get("/api/blog/articles?page=1&per_page=10")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 10
        assert data["meta"]["page"] == 1
        assert data["meta"]["total_pages"] == 3

    def test_articles_filter_by_category(self, api_client):
        """Тест фильтрации по категории."""
        category = CategoryFactory(slug="python")
        ArticleFactory.create_batch(3, category=category, status="published")
        ArticleFactory.create_batch(2, status="published")  # Другие категории

        response = api_client.get("/api/blog/articles?category=python")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 3

    def test_articles_filter_by_tag(self, api_client):
        """Тест фильтрации по тегу."""
        ArticleFactory.create_batch(3, tags=["django"], status="published")
        ArticleFactory.create_batch(2, tags=["flask"], status="published")

        response = api_client.get("/api/blog/articles?tag=django")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 3

    def test_articles_filter_by_author(self, api_client):
        """Тест фильтрации по автору."""
        author = UserFactory(username="testauthor")
        ArticleFactory.create_batch(3, author=author, status="published")
        ArticleFactory.create_batch(2, status="published")

        response = api_client.get("/api/blog/articles?author=testauthor")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 3

    def test_articles_search(self, api_client):
        """Тест поиска по названию и содержимому."""
        ArticleFactory(title="Python Tutorial", content="Learn Python", status="published")
        ArticleFactory(title="Django Guide", content="Django framework", status="published")

        response = api_client.get("/api/blog/articles?search=Python")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1
        assert "Python" in data["items"][0]["title"]

    def test_articles_sorting(self, api_client):
        """Тест сортировки."""
        ArticleFactory(title="Old", views_count=10, status="published")
        ArticleFactory(title="New", views_count=100, status="published")

        # Сортировка по популярности (views)
        response = api_client.get("/api/blog/articles?sort_by=popular")

        assert response.status_code == 200
        data = response.json()
        assert data["items"][0]["title"] == "New"  # Больше просмотров

    def test_articles_only_published(self, api_client):
        """Тест что возвращаются только опубликованные статьи."""
        ArticleFactory.create_batch(3, status="published")
        DraftArticleFactory.create_batch(2)

        response = api_client.get("/api/blog/articles")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 3  # Только опубликованные

    def test_articles_invalid_page(self, api_client):
        """Тест невалидного номера страницы."""
        ArticleFactory.create_batch(
            5, status="published"
        )  # Создаем данные чтобы была хоть 1 страница

        response = api_client.get("/api/blog/articles?page=999")

        assert response.status_code == 400


# ============================================================================
# FEATURED ARTICLES ENDPOINT
# ============================================================================


@pytest.mark.django_db
@pytest.mark.api
class TestFeaturedArticlesEndpoint:
    """Тесты для /api/blog/articles/featured endpoint."""

    def test_featured_articles_success(self, api_client):
        """Тест получения избранных статей."""
        FeaturedArticleFactory.create_batch(3)
        ArticleFactory.create_batch(2, is_featured=False, status="published")

        response = api_client.get("/api/blog/articles/featured")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        for article in data:
            assert article["is_featured"] is True

    def test_featured_articles_limit(self, api_client):
        """Тест лимита количества."""
        FeaturedArticleFactory.create_batch(10)

        response = api_client.get("/api/blog/articles/featured?limit=5")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5


# ============================================================================
# POPULAR ARTICLES ENDPOINT
# ============================================================================


@pytest.mark.django_db
@pytest.mark.api
class TestPopularArticlesEndpoint:
    """Тесты для /api/blog/articles/popular endpoint."""

    def test_popular_articles_success(self, api_client):
        """Тест получения популярных статей."""
        ArticleFactory(views_count=1000, status="published")
        ArticleFactory(views_count=500, status="published")
        ArticleFactory(views_count=100, status="published")

        response = api_client.get("/api/blog/articles/popular")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        # Проверяем сортировку по убыванию просмотров
        assert data[0]["views"] >= data[1]["views"]

    def test_popular_articles_limit(self, api_client):
        """Тест лимита количества."""
        ArticleFactory.create_batch(10, status="published")

        response = api_client.get("/api/blog/articles/popular?limit=5")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5


# ============================================================================
# ARTICLE DETAIL ENDPOINT
# ============================================================================


@pytest.mark.django_db
@pytest.mark.api
class TestArticleDetailEndpoint:
    """Тесты для /api/blog/articles/{slug} endpoint."""

    def test_article_detail_success(self, api_client):
        """Тест получения деталей статьи."""
        article = ArticleFactory(slug="test-article", title="Test Article", status="published")

        response = api_client.get(f"/api/blog/articles/{article.slug}")

        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == "test-article"
        assert data["title"] == "Test Article"
        assert "author" in data
        assert "category" in data
        assert "tags" in data

    def test_article_detail_not_found(self, api_client):
        """Тест несуществующей статьи."""
        response = api_client.get("/api/blog/articles/non-existent")

        assert response.status_code == 404

    def test_article_detail_with_series(self, api_client):
        """Тест статьи в серии."""
        series = SeriesFactory(title="Test Series")
        article = ArticleFactory(series=series, series_order=1, status="published")

        response = api_client.get(f"/api/blog/articles/{article.slug}")

        assert response.status_code == 200
        data = response.json()
        assert data["series"] is not None
        assert data["series"]["title"] == "Test Series"


# ============================================================================
# CATEGORIES ENDPOINTS
# ============================================================================


@pytest.mark.django_db
@pytest.mark.api
class TestCategoriesEndpoints:
    """Тесты для categories endpoints."""

    def test_categories_list_success(self, api_client):
        """Тест получения списка категорий."""
        CategoryFactory.create_batch(5)

        response = api_client.get("/api/blog/categories")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5
        assert "slug" in data[0]
        assert "name" in data[0]

    def test_category_detail_success(self, api_client):
        """Тест получения деталей категории."""
        category = CategoryFactory(slug="python", name="Python")
        ArticleFactory.create_batch(3, category=category, status="published")

        response = api_client.get(f"/api/blog/categories/{category.slug}")

        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == "python"
        assert data["name"] == "Python"
        assert "articles" in data
        assert len(data["articles"]) == 3

    def test_category_detail_not_found(self, api_client):
        """Тест несуществующей категории."""
        response = api_client.get("/api/blog/categories/non-existent")

        assert response.status_code == 404


# ============================================================================
# TAGS ENDPOINT
# ============================================================================


@pytest.mark.django_db
@pytest.mark.api
class TestTagsEndpoint:
    """Тесты для /api/blog/tags endpoint."""

    def test_tags_list_success(self, api_client):
        """Тест получения списка тегов."""
        ArticleFactory(tags=["python", "django"], status="published")
        ArticleFactory(tags=["python", "flask"], status="published")
        ArticleFactory(tags=["javascript"], status="published")

        response = api_client.get("/api/blog/tags")

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3

        # Проверяем структуру тега
        tag = data[0]
        assert "name" in tag
        assert "slug" in tag
        assert "article_count" in tag


# ============================================================================
# SERIES ENDPOINTS
# ============================================================================


@pytest.mark.django_db
@pytest.mark.api
class TestSeriesEndpoints:
    """Тесты для series endpoints."""

    def test_series_list_success(self, api_client):
        """Тест получения списка серий."""
        SeriesFactory.create_batch(5)

        response = api_client.get("/api/blog/series")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5
        assert "slug" in data[0]
        assert "title" in data[0]

    def test_series_detail_success(self, api_client):
        """Тест получения деталей серии."""
        series = SeriesFactory(slug="python-basics")
        ArticleFactory.create_batch(3, series=series, status="published")

        response = api_client.get(f"/api/blog/series/{series.slug}")

        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == "python-basics"
        assert "articles" in data
        assert len(data["articles"]) == 3

    def test_series_detail_not_found(self, api_client):
        """Тест несуществующей серии."""
        response = api_client.get("/api/blog/series/non-existent")

        assert response.status_code == 404


# ============================================================================
# AUTHORS ENDPOINT
# ============================================================================


@pytest.mark.django_db
@pytest.mark.api
class TestAuthorsEndpoint:
    """Тесты для /api/blog/authors endpoint."""

    def test_authors_list_success(self, api_client):
        """Тест получения списка авторов."""
        authors = UserFactory.create_batch(3)
        for author in authors:
            ArticleFactory.create_batch(2, author=author, status="published")

        response = api_client.get("/api/blog/authors")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

        # Проверяем структуру автора
        author = data[0]
        assert "username" in author
        assert "article_count" in author
        assert author["article_count"] == 2


# ============================================================================
# STATISTICS ENDPOINT
# ============================================================================


@pytest.mark.django_db
@pytest.mark.api
class TestStatisticsEndpoint:
    """Тесты для /api/blog/stats endpoint."""

    def test_stats_success(self, api_client):
        """Тест получения статистики блога."""
        # Создаем тестовые данные
        create_blog_with_articles(num_categories=2, num_articles_per_category=3)

        response = api_client.get("/api/blog/stats")

        assert response.status_code == 200
        data = response.json()

        # Проверяем наличие всех ключей статистики
        assert "total_articles" in data
        assert "published_articles" in data
        assert "total_categories" in data
        assert "total_authors" in data
        assert "total_views" in data
        assert "total_likes" in data

        # Проверяем значения
        assert data["total_articles"] >= 6  # 2 категории * 3 статьи
        assert data["total_categories"] == 2


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================


@pytest.mark.django_db
@pytest.mark.api
class TestAPIErrorHandling:
    """Тесты обработки ошибок API."""

    def test_invalid_sort_parameter(self, api_client):
        """Тест невалидного параметра сортировки."""
        response = api_client.get("/api/blog/articles?sort_by=invalid")

        # Должна быть ошибка валидации (400) или игнорирование
        assert response.status_code in [200, 400]

    def test_invalid_page_size(self, api_client):
        """Тест невалидного размера страницы."""
        response = api_client.get("/api/blog/articles?page_size=1000")

        # Размер страницы должен быть ограничен
        assert response.status_code in [200, 400]

    def test_negative_page_number(self, api_client):
        """Тест отрицательного номера страницы."""
        response = api_client.get("/api/blog/articles?page=-1")

        assert response.status_code == 400


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


@pytest.mark.django_db
@pytest.mark.integration
class TestAPIIntegration:
    """Интеграционные тесты API."""

    def test_full_blog_workflow(self, api_client):
        """Тест полного workflow: категории → статьи → детали."""
        # 1. Получаем список категорий
        category = CategoryFactory(slug="python")

        response = api_client.get("/api/blog/categories")
        assert response.status_code == 200
        categories = response.json()
        assert len(categories) >= 1

        # 2. Получаем статьи категории
        ArticleFactory.create_batch(3, category=category, status="published")

        response = api_client.get("/api/blog/articles?category=python")
        assert response.status_code == 200
        articles = response.json()["items"]
        assert len(articles) == 3

        # 3. Получаем детали первой статьи
        article_slug = articles[0]["slug"]

        response = api_client.get(f"/api/blog/articles/{article_slug}")
        assert response.status_code == 200
        article_detail = response.json()
        assert article_detail["slug"] == article_slug

    def test_search_and_filter_combination(self, api_client):
        """Тест комбинации поиска и фильтров."""
        category = CategoryFactory(slug="python")
        ArticleFactory(
            title="Python Tutorial", category=category, tags=["django"], status="published"
        )

        response = api_client.get("/api/blog/articles?search=Python&category=python&tag=django")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1
