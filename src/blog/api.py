"""
Blog API - Современное REST API для блога.

Этот модуль содержит все эндпоинты для работы с блогом через REST API.
Используется Django Ninja для автоматической генерации документации и валидации.

Особенности:
    - Полная типизация с помощью Pydantic схем
    - Обработка всех возможных ошибок
    - Логирование всех операций
    - JWT аутентификация для защищенных эндпоинтов
    - Пагинация для больших списков
    - Фильтрация и поиск
    - Оптимизированные запросы с select_related/prefetch_related

Архитектура:
    - Public endpoints: Доступны всем (GET запросы)
    - Protected endpoints: Требуют JWT токен (POST, PATCH, DELETE)
    - Admin endpoints: Только для администраторов

Автор: PySchool Team
Дата: 2025
"""

from __future__ import annotations

import logging
from math import ceil
from typing import TYPE_CHECKING, Any, Optional

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db.models import Count, Q, QuerySet
from ninja import Router
from ninja.errors import HttpError

from .cache_utils import cache_page_data, cache_stats
from .models import Article, ArticleReaction, Bookmark, Category, ReadingProgress, Series
from .schemas import (  # Article schemas; Author schemas; Category schemas; Common schemas; Series schemas; Tag schemas
    ArticleDetailOut,
    ArticleListOut,
    AuthorOut,
    BlogStatsOut,
    CategoryOut,
    MessageSchema,
    PagedArticles,
    PaginationMeta,
    SeriesDetailOut,
    SeriesOut,
    TagOut,
)

# Настройка логирования
logger = logging.getLogger(__name__)

# ============================================================================
# CACHED HELPER FUNCTIONS
# ============================================================================


@cache_stats(timeout=600)
def get_cached_blog_stats():
    """
    Получает статистику блога с кешированием (10 минут).

    Returns:
        dict: Статистика блога
    """
    try:
        from .models import Author, Comment

        return {
            "total_articles": Article.objects.filter(status="published").count(),
            "total_categories": Category.objects.annotate(
                article_count=Count("articles", filter=Q(articles__status="published"))
            )
            .filter(article_count__gt=0)
            .count(),
            "total_comments": Comment.objects.filter(is_approved=True).count(),
            "total_authors": Author.objects.filter(is_active=True).count(),
        }
    except Exception as e:
        logger.error(f"API: Ошибка получения статистики блога: {e}")
        return {
            "total_articles": 0,
            "total_categories": 0,
            "total_comments": 0,
            "total_authors": 0,
        }


@cache_page_data(timeout=300, key_prefix="api_categories")
def get_cached_categories():
    """
    Получает список категорий с кешированием (5 минут).

    Returns:
        list: Список категорий
    """
    try:
        return list(
            Category.objects.annotate(
                article_count=Count("articles", filter=Q(articles__status="published"))
            )
            .filter(article_count__gt=0)
            .order_by("name")
        )
    except Exception as e:
        logger.error(f"API: Ошибка получения категорий: {e}")
        return []


@cache_stats(timeout=600)
def get_cached_detailed_stats():
    """
    Получает детальную статистику блога с кешированием (10 минут).

    Returns:
        dict: Детальная статистика
    """
    try:
        from django.db.models import Sum

        total_articles = Article.objects.count()
        published_articles = Article.objects.filter(status="published").count()
        total_categories = Category.objects.count()
        total_views = sum(Article.objects.values_list("views_count", flat=True) or [0])
        total_likes = ArticleReaction.objects.filter(article__isnull=False).count()
        total_authors = User.objects.filter(blog_articles__isnull=False).distinct().count()

        # Статистика по категориям
        categories_stats = []
        for category in Category.objects.all():
            articles_count = category.articles.filter(status="published").count()
            if articles_count > 0:
                total_category_views = sum(
                    category.articles.filter(status="published").values_list(
                        "views_count", flat=True
                    )
                    or [0]
                )
                total_category_likes = (
                    category.articles.filter(status="published").aggregate(total=Sum("reactions"))[
                        "total"
                    ]
                    or 0
                )

                from .schemas import serialize_category

                categories_stats.append(
                    {
                        "category": serialize_category(category),
                        "articles_count": articles_count,
                        "total_views": total_category_views,
                        "total_likes": total_category_likes,
                    }
                )

        return {
            "total_articles": total_articles,
            "published_articles": published_articles,
            "total_categories": total_categories,
            "total_views": total_views,
            "total_likes": total_likes,
            "total_authors": total_authors,
            "categories_stats": categories_stats,
        }
    except Exception as e:
        logger.error(f"API: Ошибка получения детальной статистики: {e}")
        return {
            "total_articles": 0,
            "published_articles": 0,
            "total_categories": 0,
            "total_views": 0,
            "total_likes": 0,
            "total_authors": 0,
            "categories_stats": [],
        }


if TYPE_CHECKING:
    User = AbstractUser
else:
    User = get_user_model()

# Создание роутера с тегами для Swagger документации
router = Router(tags=["Blog"])

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def get_pagination_meta(
    queryset: QuerySet, page: int, per_page: int
) -> tuple[QuerySet, PaginationMeta]:
    """
    Создание метаданных пагинации и получение страницы данных.

    Args:
        queryset: QuerySet для пагинации
        page: Номер страницы (начиная с 1)
        per_page: Количество элементов на странице

    Returns:
        tuple: (QuerySet страницы, метаданные пагинации)

    Example:
        >>> articles = Article.objects.all()
        >>> page_data, meta = get_pagination_meta(articles, 1, 20)
        >>> print(meta.total_pages)
        5
    """
    try:
        total = queryset.count()
        total_pages = ceil(total / per_page) if per_page > 0 else 0

        # Валидация номера страницы
        if total > 0 and page > total_pages:
            raise HttpError(400, f"Страница {page} не существует. Всего страниц: {total_pages}")

        offset = (page - 1) * per_page

        paginated_qs = queryset[offset : offset + per_page]

        meta = PaginationMeta(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        )

        return paginated_qs, meta
    except HttpError:
        raise
    except Exception as e:
        logger.error(f"Ошибка пагинации: {e}")
        raise HttpError(500, "Ошибка при обработке пагинации")


def serialize_author(user: User, include_article_count: bool = False) -> dict[str, Any]:
    """
    Сериализация автора в словарь.

    Args:
        user: Объект пользователя Django
        include_article_count: Включить количество опубликованных статей

    Returns:
        dict: Словарь с данными автора
    """
    try:
        profile = getattr(user, "student", None)
        result = {
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "full_name": user.get_full_name() or user.username,
            "avatar_url": profile.avatar.url if profile and profile.avatar else None,
            "bio": profile.bio if profile else None,
        }

        if include_article_count:
            result["article_count"] = user.blog_articles.filter(status="published").count()

        return result
    except Exception as e:
        logger.error(f"Ошибка сериализации автора {user.id}: {e}")
        return {
            "id": user.id,
            "username": user.username,
            "first_name": "",
            "last_name": "",
            "full_name": user.username,
            "avatar_url": None,
            "bio": None,
        }


def serialize_category(category: Optional[Category]) -> Optional[dict[str, Any]]:
    """
    Сериализация категории в словарь.

    Args:
        category: Объект категории или None

    Returns:
        dict | None: Словарь с данными категории или None
    """
    if not category:
        return None

    try:
        return {
            "id": category.id,
            "name": category.name,
            "slug": category.slug,
            "description": category.description,
            "icon": category.icon,
            "color": category.color,
            "article_count": category.articles.filter(status="published").count(),
            "created_at": category.created_at,
            "updated_at": category.updated_at,
        }
    except Exception as e:
        logger.error(f"Ошибка сериализации категории {category.id}: {e}")
        return None


def serialize_tags(tags: QuerySet) -> list[dict[str, Any]]:
    """
    Сериализация списка тегов.

    Args:
        tags: QuerySet тегов

    Returns:
        list: Список словарей с данными тегов
    """
    result = []
    for tag in tags:
        try:
            result.append(
                {
                    "id": tag.id,
                    "name": tag.name,
                    "slug": tag.slug,
                    "article_count": tag.taggit_taggeditem_items.filter(
                        content_type__model="article"
                    ).count(),
                }
            )
        except Exception as e:
            logger.error(f"Ошибка сериализации тега {tag.id}: {e}")
    return result


def serialize_series(series: Optional[Series]) -> Optional[dict[str, Any]]:
    """
    Сериализация серии в словарь.

    Args:
        series: Объект серии или None

    Returns:
        dict | None: Словарь с данными серии или None
    """
    if not series:
        return None

    try:
        return {
            "id": series.id,
            "title": series.title,
            "slug": series.slug,
            "description": series.description,
            "article_count": series.articles.filter(status="published").count(),
            "total_reading_time": sum(
                a.reading_time for a in series.articles.filter(status="published")
            ),
            "created_at": series.created_at,
        }
    except Exception as e:
        logger.error(f"Ошибка сериализации серии {series.id}: {e}")
        return None


def serialize_article_list(article: Article, user: Optional[User] = None) -> dict[str, Any]:
    """
    Сериализация статьи для списка (краткая информация).

    Args:
        article: Объект статьи
        user: Текущий пользователь (для проверки лайков/закладок)

    Returns:
        dict: Словарь с данными статьи
    """
    try:
        return {
            "id": article.id,
            "title": article.title,
            "slug": article.slug,
            "excerpt": article.excerpt,
            "featured_image": article.featured_image.url if article.featured_image else None,
            "category": serialize_category(article.category),
            "author": serialize_author(article.author),
            "tags": serialize_tags(article.tags.all()),
            "status": article.status,
            "difficulty": article.difficulty,
            "reading_time": article.reading_time,
            "views": article.views_count,
            "likes": article.total_reactions,
            "comments_count": article.comments.filter(parent__isnull=True).count(),
            "is_featured": article.is_featured,
            "published_at": article.published_at,
            "created_at": article.created_at,
            "updated_at": article.updated_at,
        }
    except Exception as e:
        logger.error(f"Ошибка сериализации статьи {article.id}: {e}")
        raise


def serialize_article_detail(article: Article, user: Optional[User] = None) -> dict[str, Any]:
    """
    Сериализация статьи с полной информацией.

    Args:
        article: Объект статьи
        user: Текущий пользователь (для проверки лайков/закладок)

    Returns:
        dict: Словарь с полными данными статьи
    """
    try:
        base_data = serialize_article_list(article, user)

        # Дополнительные поля для детальной информации
        base_data.update(
            {
                "content": article.content,
                "meta_description": article.meta_description,
                "meta_keywords": article.meta_keywords,
                "series": serialize_series(article.series),
                "series_order": article.series_order,
                "is_featured": article.is_featured,
                "allow_comments": article.allow_comments,
                "user_has_liked": False,
                "user_has_bookmarked": False,
                "user_reading_progress": None,
            }
        )

        # Проверка действий пользователя
        if user and user.is_authenticated:
            from .models import ArticleReaction

            base_data["user_has_liked"] = ArticleReaction.objects.filter(
                user=user, article=article
            ).exists()
            base_data["user_has_bookmarked"] = Bookmark.objects.filter(
                user=user, article=article
            ).exists()

            progress = ReadingProgress.objects.filter(user=user, article=article).first()
            if progress:
                base_data["user_reading_progress"] = progress.progress_percentage

        return base_data
    except Exception as e:
        logger.error(f"Ошибка детальной сериализации статьи {article.id}: {e}")
        raise


# ============================================================================
# ARTICLE ENDPOINTS
# ============================================================================


@router.get(
    "/articles",
    response=PagedArticles,
    summary="Список статей",
    description="Получение пагинированного списка статей с фильтрацией и поиском",
    auth=None,  # Публичный эндпоинт
)
def list_articles(
    request,
    category: Optional[str] = None,
    category_id: Optional[int] = None,
    tag: Optional[str] = None,
    tag_ids: Optional[str] = None,
    author: Optional[str] = None,
    author_id: Optional[int] = None,
    series_id: Optional[int] = None,
    difficulty: Optional[str] = None,
    status: str = "published",
    is_featured: Optional[bool] = None,
    search: Optional[str] = None,
    sort_by: str = "published_at",
    order: str = "desc",
    page: int = 1,
    per_page: int = 20,
) -> PagedArticles:
    """
    Получение списка статей с фильтрацией и пагинацией.

    Поддерживаемые фильтры:
        - category_id: ID категории
        - tag_ids: ID тегов через запятую (например: "1,2,3")
        - author_id: ID автора
        - series_id: ID серии
        - difficulty: Уровень сложности (beginner, intermediate, advanced)
        - status: Статус (published, draft, archived)
        - is_featured: Только избранные (true/false)
        - search: Поиск по заголовку и контенту

    Сортировка:
        - sort_by: Поле (created_at, published_at, title, views, likes, reading_time)
        - order: Направление (asc, desc)

    Args:
        request: HTTP запрос
        category_id: Фильтр по категории
        tag_ids: Фильтр по тегам (строка с ID через запятую)
        author_id: Фильтр по автору
        series_id: Фильтр по серии
        difficulty: Фильтр по сложности
        status: Фильтр по статусу (по умолчанию published)
        is_featured: Только избранные статьи
        search: Поисковый запрос
        sort_by: Поле для сортировки
        order: Порядок сортировки
        page: Номер страницы
        per_page: Элементов на странице

    Returns:
        PagedArticles: Пагинированный список статей

    Raises:
        HttpError 400: Неверные параметры запроса
        HttpError 500: Внутренняя ошибка сервера
    """
    try:
        logger.info(f"Запрос списка статей: page={page}, filters={locals()}")

        # Валидация параметров
        if per_page > 100:
            raise HttpError(400, "per_page не может быть больше 100")
        if page < 1:
            raise HttpError(400, "page должен быть >= 1")

        # Базовый QuerySet с оптимизацией
        queryset = Article.objects.select_related("category", "author", "series").prefetch_related(
            "tags"
        )

        # Фильтр по статусу
        queryset = queryset.filter(status=status)

        # Фильтр по категории (поддержка как slug так и id)
        if category:
            # Пытаемся определить - это slug или ID
            if category.isdigit():
                queryset = queryset.filter(category_id=int(category))
            else:
                queryset = queryset.filter(category__slug=category)
        elif category_id:
            queryset = queryset.filter(category_id=category_id)

        # Фильтр по тегам (поддержка slug и id)
        if tag:
            queryset = queryset.filter(tags__slug=tag).distinct()
        elif tag_ids:
            try:
                tag_id_list = [int(tid.strip()) for tid in tag_ids.split(",")]
                queryset = queryset.filter(tags__id__in=tag_id_list).distinct()
            except ValueError:
                raise HttpError(400, "Неверный формат tag_ids")

        # Фильтр по автору (поддержка username и id)
        if author:
            queryset = queryset.filter(author__username=author)
        elif author_id:
            queryset = queryset.filter(author_id=author_id)

        # Фильтр по серии
        if series_id:
            queryset = queryset.filter(series_id=series_id)

        # Фильтр по сложности
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)

        # Фильтр по избранным
        if is_featured is not None:
            queryset = queryset.filter(is_featured=is_featured)

        # Поиск
        if search and len(search) >= 2:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(content__icontains=search)
                | Q(excerpt__icontains=search)
            )

        # Сортировка
        order_prefix = "-" if order.lower() == "desc" else ""

        # Мапинг для обратной совместимости и удобных алиасов
        sort_field_mapping = {
            "views": "views_count",
            "popular": "views_count",
            "likes": "reactions_count",
        }

        # Применяем мапинг
        sort_by = sort_field_mapping.get(sort_by, sort_by)

        valid_sort_fields = [
            "created_at",
            "published_at",
            "updated_at",
            "title",
            "views_count",
            "reading_time",
            "reactions_count",
        ]
        if sort_by not in valid_sort_fields:
            sort_by = "published_at"

        # Для сортировки по лайкам используем аннотацию
        if sort_by == "reactions_count":
            queryset = queryset.annotate(reactions_total=Count("reactions"))
            queryset = queryset.order_by(f"{order_prefix}reactions_total")
        else:
            queryset = queryset.order_by(f"{order_prefix}{sort_by}")

        # Пагинация
        paginated_articles, meta = get_pagination_meta(queryset, page, per_page)

        # Сериализация
        user = request.user if request.user.is_authenticated else None
        items = [serialize_article_list(article, user) for article in paginated_articles]

        logger.info(f"Возвращено {len(items)} статей (страница {page})")
        return PagedArticles(items=items, meta=meta)

    except HttpError:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения списка статей: {e}", exc_info=True)
        raise HttpError(500, "Ошибка при получении списка статей")


@router.get(
    "/articles/featured",
    response=list[ArticleListOut],
    summary="Избранные статьи",
    description="Получение списка избранных статей",
    auth=None,  # Публичный эндпоинт
)
def featured_articles(request, limit: int = 10) -> list[ArticleListOut]:
    """
    Получение избранных статей.

    Args:
        request: HTTP запрос
        limit: Максимальное количество статей (по умолчанию 10)

    Returns:
        list[ArticleListOut]: Список избранных статей
    """
    try:
        logger.info(f"Запрос избранных статей: limit={limit}")

        if limit > 50:
            raise HttpError(400, "limit не может быть больше 50")

        articles = (
            Article.objects.filter(status="published", is_featured=True)
            .select_related("category", "author", "series")
            .prefetch_related("tags")
            .order_by("-published_at")[:limit]
        )

        user = request.user if request.user.is_authenticated else None
        result = [serialize_article_list(article, user) for article in articles]

        logger.info(f"Возвращено {len(result)} избранных статей")
        return result

    except HttpError:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения избранных статей: {e}", exc_info=True)
        raise HttpError(500, "Ошибка при получении избранных статей")


@router.get(
    "/articles/popular",
    response=list[ArticleListOut],
    summary="Популярные статьи",
    description="Получение списка популярных статей по просмотрам",
    auth=None,  # Публичный эндпоинт
)
def popular_articles(request, limit: int = 10) -> list[ArticleListOut]:
    """
    Получение популярных статей.

    Args:
        request: HTTP запрос
        limit: Максимальное количество статей (по умолчанию 10)

    Returns:
        list[ArticleListOut]: Список популярных статей
    """
    try:
        logger.info(f"Запрос популярных статей: limit={limit}")

        if limit > 50:
            raise HttpError(400, "limit не может быть больше 50")

        from django.db.models import Count

        articles = (
            Article.objects.filter(status="published")
            .select_related("category", "author", "series")
            .prefetch_related("tags")
            .annotate(reactions_total=Count("reactions"))
            .order_by("-views_count", "-reactions_total")[:limit]
        )

        user = request.user if request.user.is_authenticated else None
        result = [serialize_article_list(article, user) for article in articles]

        logger.info(f"Возвращено {len(result)} популярных статей")
        return result

    except HttpError:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения популярных статей: {e}", exc_info=True)
        raise HttpError(500, "Ошибка при получении популярных статей")


@router.get(
    "/articles/{slug}",
    response=ArticleDetailOut,
    summary="Детали статьи",
    description="Получение полной информации о статье по slug",
    auth=None,  # Публичный эндпоинт
)
def get_article(request, slug: str) -> ArticleDetailOut:
    """
    Получение детальной информации о статье.

    Увеличивает счетчик просмотров на 1.

    Args:
        request: HTTP запрос
        slug: URL slug статьи

    Returns:
        ArticleDetailOut: Детальная информация о статье

    Raises:
        HttpError 404: Статья не найдена
        HttpError 500: Внутренняя ошибка сервера
    """
    try:
        logger.info(f"Запрос статьи: slug={slug}")

        article = (
            Article.objects.select_related("category", "author", "series")
            .prefetch_related("tags")
            .filter(slug=slug)
            .first()
        )

        if not article:
            raise HttpError(404, "Статья не найдена")

        # Увеличение просмотров
        article.views_count += 1
        article.save(update_fields=["views_count"])

        user = request.user if request.user.is_authenticated else None
        result = serialize_article_detail(article, user)

        logger.info(f"Статья {slug} успешно получена")
        return result

    except HttpError:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения статьи {slug}: {e}", exc_info=True)
        raise HttpError(500, "Ошибка при получении статьи")


@router.get(
    "/categories",
    response=list[CategoryOut],
    summary="Список категорий",
    description="Получение списка всех категорий",
    auth=None,  # Публичный эндпоинт
)
def list_categories(request) -> list[CategoryOut]:
    """
    Получение списка всех категорий.

    Args:
        request: HTTP запрос

    Returns:
        list[CategoryOut]: Список категорий
    """
    try:
        logger.info("Запрос списка категорий")

        categories = Category.objects.all().order_by("name")
        result = [serialize_category(cat) for cat in categories if cat]

        logger.info(f"Возвращено {len(result)} категорий")
        return result

    except Exception as e:
        logger.error(f"Ошибка получения категорий: {e}", exc_info=True)
        raise HttpError(500, "Ошибка при получении категорий")


@router.get(
    "/categories/{slug}",
    response=CategoryOut,
    summary="Детали категории",
    description="Получение полной информации о категории",
    auth=None,  # Публичный эндпоинт
)
def get_category(request, slug: str) -> CategoryOut:
    """
    Получение детальной информации о категории.

    Args:
        request: HTTP запрос
        slug: URL slug категории

    Returns:
        CategoryOut: Детальная информация о категории

    Raises:
        HttpError 404: Категория не найдена
    """
    try:
        logger.info(f"Запрос категории: slug={slug}")

        category = Category.objects.filter(slug=slug).first()
        if not category:
            raise HttpError(404, "Категория не найдена")

        result = serialize_category(category)

        # Добавляем статьи категории
        articles = (
            category.articles.filter(status="published")
            .select_related("author", "category")
            .prefetch_related("tags")[:10]
        )  # Ограничиваем 10 статьями

        user = request.user if request.user.is_authenticated else None
        result["articles"] = [serialize_article_list(article, user) for article in articles]

        logger.info(f"Категория {slug} успешно получена")
        return result

    except HttpError:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения категории {slug}: {e}", exc_info=True)
        raise HttpError(500, "Ошибка при получении категории")


@router.get(
    "/tags",
    response=list[TagOut],
    summary="Список тегов",
    description="Получение списка всех тегов",
    auth=None,  # Публичный эндпоинт
)
def list_tags(request, limit: Optional[int] = None) -> list[TagOut]:
    """
    Получение списка тегов.

    Args:
        request: HTTP запрос
        limit: Максимальное количество тегов (необязательно)

    Returns:
        list[TagOut]: Список тегов
    """
    try:
        logger.info("Запрос списка тегов")

        from taggit.models import Tag

        tags = Tag.objects.all().order_by("name")
        if limit and limit > 0:
            tags = tags[:limit]

        result = serialize_tags(tags)

        logger.info(f"Возвращено {len(result)} тегов")
        return result

    except Exception as e:
        logger.error(f"Ошибка получения тегов: {e}", exc_info=True)
        raise HttpError(500, "Ошибка при получении тегов")


@router.get(
    "/series",
    response=list[SeriesOut],
    summary="Список серий",
    description="Получение списка всех серий статей",
    auth=None,  # Публичный эндпоинт
)
def list_series(request) -> list[SeriesOut]:
    """
    Получение списка всех серий статей.

    Args:
        request: HTTP запрос

    Returns:
        list[SeriesOut]: Список серий
    """
    try:
        logger.info("Запрос списка серий")

        series_list = Series.objects.all().order_by("-created_at")
        result = [serialize_series(s) for s in series_list if serialize_series(s)]

        logger.info(f"Возвращено {len(result)} серий")
        return result

    except Exception as e:
        logger.error(f"Ошибка получения серий: {e}", exc_info=True)
        raise HttpError(500, "Ошибка при получении серий")


@router.get(
    "/series/{slug}",
    response=SeriesDetailOut,
    summary="Детали серии",
    description="Получение полной информации о серии с её статьями",
    auth=None,  # Публичный эндпоинт
)
def get_series(request, slug: str) -> SeriesDetailOut:
    """
    Получение детальной информации о серии.

    Args:
        request: HTTP запрос
        slug: URL slug серии

    Returns:
        SeriesDetailOut: Детальная информация о серии

    Raises:
        HttpError 404: Серия не найдена
    """
    try:
        logger.info(f"Запрос серии: slug={slug}")

        series = Series.objects.filter(slug=slug).first()
        if not series:
            raise HttpError(404, "Серия не найдена")

        result = serialize_series(series)
        if result:
            result["is_completed"] = series.status == "completed"

            # Добавляем статьи серии
            articles = (
                series.articles.filter(status="published")
                .order_by("series_order")
                .select_related("author", "category")
                .prefetch_related("tags")
            )

            user = request.user if request.user.is_authenticated else None
            result["articles"] = [serialize_article_list(article, user) for article in articles]

        logger.info(f"Серия {slug} успешно получена")
        return result

    except HttpError:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения серии {slug}: {e}", exc_info=True)
        raise HttpError(500, "Ошибка при получении серии")


@router.get(
    "/authors",
    response=list[AuthorOut],
    summary="Список авторов",
    description="Получение списка всех авторов блога",
    auth=None,  # Публичный эндпоинт
)
def list_authors(request) -> list[AuthorOut]:
    """
    Получение списка всех авторов с опубликованными статьями.

    Args:
        request: HTTP запрос

    Returns:
        list[AuthorOut]: Список авторов
    """
    try:
        logger.info("Запрос списка авторов")

        # Получаем только авторов с опубликованными статьями
        authors = (
            User.objects.filter(blog_articles__status="published")
            .distinct()
            .order_by("first_name", "last_name")
        )

        result = [serialize_author(author, include_article_count=True) for author in authors]

        logger.info(f"Возвращено {len(result)} авторов")
        return result

    except Exception as e:
        logger.error(f"Ошибка получения авторов: {e}", exc_info=True)
        raise HttpError(500, "Ошибка при получении авторов")


@router.get(
    "/stats",
    response=BlogStatsOut,
    summary="Статистика блога",
    description="Получение общей статистики блога",
    auth=None,  # Публичный эндпоинт
)
def get_blog_stats(request) -> BlogStatsOut:
    """
    Получение общей статистики блога с кешированием.

    Args:
        request: HTTP запрос

    Returns:
        BlogStatsOut: Статистика блога (кешируется на 10 минут)
    """
    try:
        logger.info("Запрос статистики блога (с кешированием)")

        # Получаем статистику из кеша (10 минут)
        result = get_cached_detailed_stats()

        logger.info("Статистика блога успешно получена")
        return result

    except Exception as e:
        logger.error(f"Ошибка получения статистики: {e}", exc_info=True)
        raise HttpError(500, "Ошибка при получении статистики")


# ============================================================================
# PING ENDPOINT (для проверки работоспособности API)
# ============================================================================


@router.get(
    "/ping",
    response=MessageSchema,
    summary="Проверка работы API",
    description="Простой эндпоинт для проверки доступности API",
    auth=None,  # Публичный эндпоинт
)
def ping(request) -> MessageSchema:
    """
    Проверка работы API.

    Args:
        request: HTTP запрос

    Returns:
        MessageSchema: Сообщение о работоспособности
    """
    logger.info("Ping запрос")
    return MessageSchema(message="Blog API is working!")
