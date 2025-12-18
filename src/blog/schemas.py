"""
Pydantic схемы для Blog API.

Этот модуль содержит все схемы для валидации входных/выходных данных API.
Используется Django Ninja с Pydantic для автоматической валидации и документации.

Архитектура:
    - Input схемы: *In - для входящих данных (POST, PATCH)
    - Output схемы: *Out - для исходящих данных (GET)
    - Filter схемы: *Filter - для фильтрации и поиска
    - Pagination схемы: Page* - для пагинированных ответов
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from ninja import Field, Schema
from pydantic import field_validator

# ============================================================================
# ENUMS
# ============================================================================


class ArticleStatus(str, Enum):
    """Статусы статьи."""

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class DifficultyLevel(str, Enum):
    """Уровни сложности статьи."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class ReactionType(str, Enum):
    """Типы реакций на статью."""

    LIKE = "like"
    LOVE = "love"
    HELPFUL = "helpful"
    INSIGHTFUL = "insightful"
    AMAZING = "amazing"


class SortOrder(str, Enum):
    """Порядок сортировки."""

    ASC = "asc"
    DESC = "desc"


class ArticleSortBy(str, Enum):
    """Поля для сортировки статей."""

    CREATED = "created_at"
    PUBLISHED = "published_at"
    UPDATED = "updated_at"
    TITLE = "title"
    VIEWS = "views"
    LIKES = "likes"
    READING_TIME = "reading_time"


# ============================================================================
# BASE SCHEMAS
# ============================================================================


class ErrorSchema(Schema):
    """Схема ответа при ошибке."""

    detail: str = Field(..., description="Описание ошибки")
    code: Optional[str] = Field(None, description="Код ошибки")


class MessageSchema(Schema):
    """Схема простого сообщения."""

    message: str = Field(..., description="Текст сообщения")


class PaginationMeta(Schema):
    """Метаданные пагинации."""

    page: int = Field(..., ge=1, description="Текущая страница")
    per_page: int = Field(..., ge=1, le=100, description="Элементов на странице")
    total: int = Field(..., ge=0, description="Всего элементов")
    total_pages: int = Field(..., ge=0, description="Всего страниц")
    has_next: bool = Field(..., description="Есть ли следующая страница")
    has_prev: bool = Field(..., description="Есть ли предыдущая страница")


# ============================================================================
# CATEGORY SCHEMAS
# ============================================================================


class CategoryBase(Schema):
    """Базовая схема категории."""

    name: str = Field(..., min_length=1, max_length=100, description="Название категории")
    slug: str = Field(..., min_length=1, max_length=100, description="URL slug")
    description: Optional[str] = Field(None, description="Описание категории")
    icon: str = Field(default="📝", max_length=50, description="Иконка категории")
    color: str = Field(default="#3498db", max_length=7, description="Цвет в формате HEX")


class CategoryOut(CategoryBase):
    """Схема вывода категории."""

    id: int = Field(..., description="ID категории")
    article_count: int = Field(..., ge=0, description="Количество статей")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата обновления")
    articles: Optional[list] = Field(None, description="Список статей категории")


class CategoryDetailOut(CategoryOut):
    """Детальная схема категории с дополнительной информацией."""

    tag_keywords: Optional[str] = Field(None, description="Ключевые слова для тегов")
    badge: Optional[str] = Field(None, description="Бейдж категории")
    order: int = Field(default=0, description="Порядок отображения")


class CategoryIn(Schema):
    """Схема создания категории."""

    name: str = Field(..., min_length=1, max_length=100, description="Название категории")
    description: Optional[str] = Field(None, description="Описание категории")
    icon: str = Field(default="📝", max_length=50, description="Иконка категории")
    color: str = Field(default="#3498db", max_length=7, description="Цвет в формате HEX")
    tag_keywords: Optional[str] = Field(None, description="Ключевые слова для тегов")
    badge: Optional[str] = Field(None, description="Бейдж категории")

    @field_validator("color")
    @classmethod
    def validate_hex_color(cls, v: str) -> str:
        """Валидация HEX цвета."""
        if not v.startswith("#") or len(v) != 7:
            raise ValueError("Color must be in HEX format (#RRGGBB)")
        try:
            int(v[1:], 16)
        except ValueError:
            raise ValueError("Invalid HEX color")
        return v.lower()


class CategoryUpdate(Schema):
    """Схема обновления категории."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, max_length=7)
    tag_keywords: Optional[str] = None
    badge: Optional[str] = None
    order: Optional[int] = Field(None, ge=0)


# ============================================================================
# TAG SCHEMAS
# ============================================================================


class TagOut(Schema):
    """Схема вывода тега."""

    id: int = Field(..., description="ID тега")
    name: str = Field(..., description="Название тега")
    slug: str = Field(..., description="URL slug")
    article_count: int = Field(..., ge=0, description="Количество статей")


class TagDetailOut(TagOut):
    """Детальная схема тега."""

    description: Optional[str] = Field(None, description="Описание тега")


# ============================================================================
# AUTHOR SCHEMAS
# ============================================================================


class AuthorOut(Schema):
    """Схема вывода автора."""

    id: int = Field(..., description="ID автора")
    username: str = Field(..., description="Username автора")
    first_name: str = Field(..., description="Имя")
    last_name: str = Field(..., description="Фамилия")
    full_name: str = Field(..., description="Полное имя")
    avatar_url: Optional[str] = Field(None, description="URL аватара")
    bio: Optional[str] = Field(None, description="Биография")
    article_count: Optional[int] = Field(None, ge=0, description="Количество статей")


class AuthorDetailOut(AuthorOut):
    """Детальная схема автора."""

    article_count: int = Field(..., ge=0, description="Количество статей")
    total_views: int = Field(..., ge=0, description="Всего просмотров")
    total_likes: int = Field(..., ge=0, description="Всего лайков")


# ============================================================================
# SERIES SCHEMAS
# ============================================================================


class SeriesOut(Schema):
    """Схема вывода серии."""

    id: int = Field(..., description="ID серии")
    title: str = Field(..., description="Название серии")
    slug: str = Field(..., description="URL slug")
    description: Optional[str] = Field(None, description="Описание серии")
    article_count: int = Field(..., ge=0, description="Количество статей")
    total_reading_time: int = Field(..., ge=0, description="Общее время чтения")
    created_at: datetime = Field(..., description="Дата создания")


class SeriesDetailOut(SeriesOut):
    """Детальная схема серии с статьями."""

    is_completed: bool = Field(..., description="Серия завершена")
    articles: Optional[list] = Field(None, description="Список статей серии")


class SeriesIn(Schema):
    """Схема создания серии."""

    title: str = Field(..., min_length=1, max_length=200, description="Название серии")
    description: Optional[str] = Field(None, description="Описание серии")
    is_completed: bool = Field(default=False, description="Серия завершена")


class SeriesUpdate(Schema):
    """Схема обновления серии."""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    is_completed: Optional[bool] = None


# ============================================================================
# ARTICLE SCHEMAS
# ============================================================================


class ArticleListOut(Schema):
    """Схема для списка статей (краткая информация)."""

    id: int = Field(..., description="ID статьи")
    title: str = Field(..., description="Заголовок")
    slug: str = Field(..., description="URL slug")
    excerpt: str = Field(..., description="Краткое описание")
    featured_image: Optional[str] = Field(None, description="URL главного изображения")
    category: Optional[CategoryOut] = Field(None, description="Категория")
    author: AuthorOut = Field(..., description="Автор")
    tags: list[TagOut] = Field(default_factory=list, description="Теги")
    status: ArticleStatus = Field(..., description="Статус публикации")
    difficulty: Optional[DifficultyLevel] = Field(None, description="Уровень сложности")
    reading_time: int = Field(..., ge=0, description="Время чтения (минуты)")
    views: int = Field(..., ge=0, description="Количество просмотров")
    likes: int = Field(..., ge=0, description="Количество лайков")
    comments_count: int = Field(..., ge=0, description="Количество комментариев")
    is_featured: bool = Field(..., description="Избранная статья")
    published_at: Optional[datetime] = Field(None, description="Дата публикации")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата обновления")


class ArticleDetailOut(ArticleListOut):
    """Детальная схема статьи."""

    content: str = Field(..., description="Полный контент статьи")
    meta_description: Optional[str] = Field(None, description="META описание")
    meta_keywords: Optional[str] = Field(None, description="META ключевые слова")
    series: Optional[SeriesOut] = Field(None, description="Серия статей")
    series_order: Optional[int] = Field(None, description="Порядок в серии")
    is_featured: bool = Field(..., description="Избранная статья")
    allow_comments: bool = Field(..., description="Комментарии разрешены")
    user_has_liked: Optional[bool] = Field(None, description="Лайкнул ли текущий пользователь")
    user_has_bookmarked: Optional[bool] = Field(None, description="Добавил ли в закладки")
    user_reading_progress: Optional[int] = Field(
        None, ge=0, le=100, description="Прогресс чтения %"
    )


class ArticleIn(Schema):
    """Схема создания статьи."""

    title: str = Field(..., min_length=1, max_length=200, description="Заголовок")
    content: str = Field(..., min_length=10, description="Контент статьи")
    excerpt: Optional[str] = Field(None, max_length=500, description="Краткое описание")
    category_id: Optional[int] = Field(None, description="ID категории")
    tag_ids: list[int] = Field(default_factory=list, description="ID тегов")
    series_id: Optional[int] = Field(None, description="ID серии")
    series_order: Optional[int] = Field(None, ge=1, description="Порядок в серии")
    difficulty: Optional[DifficultyLevel] = Field(None, description="Уровень сложности")
    featured_image: Optional[str] = Field(None, description="URL изображения")
    meta_description: Optional[str] = Field(None, max_length=160, description="META описание")
    meta_keywords: Optional[str] = Field(None, description="META ключевые слова")
    is_featured: bool = Field(default=False, description="Избранная статья")
    allow_comments: bool = Field(default=True, description="Разрешить комментарии")
    status: ArticleStatus = Field(default=ArticleStatus.DRAFT, description="Статус публикации")


class ArticleUpdate(Schema):
    """Схема обновления статьи."""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=10)
    excerpt: Optional[str] = Field(None, max_length=500)
    category_id: Optional[int] = None
    tag_ids: Optional[list[int]] = None
    series_id: Optional[int] = None
    series_order: Optional[int] = Field(None, ge=1)
    difficulty: Optional[DifficultyLevel] = None
    featured_image: Optional[str] = None
    meta_description: Optional[str] = Field(None, max_length=160)
    meta_keywords: Optional[str] = None
    is_featured: Optional[bool] = None
    allow_comments: Optional[bool] = None
    status: Optional[ArticleStatus] = None


class ArticleFilter(Schema):
    """Схема фильтрации статей."""

    category_id: Optional[int] = Field(None, description="Фильтр по категории")
    tag_ids: Optional[list[int]] = Field(None, description="Фильтр по тегам")
    author_id: Optional[int] = Field(None, description="Фильтр по автору")
    series_id: Optional[int] = Field(None, description="Фильтр по серии")
    difficulty: Optional[DifficultyLevel] = Field(None, description="Фильтр по сложности")
    status: Optional[ArticleStatus] = Field(None, description="Фильтр по статусу")
    is_featured: Optional[bool] = Field(None, description="Только избранные")
    search: Optional[str] = Field(
        None, min_length=2, max_length=100, description="Поисковый запрос"
    )
    sort_by: ArticleSortBy = Field(
        default=ArticleSortBy.PUBLISHED, description="Сортировка по полю"
    )
    order: SortOrder = Field(default=SortOrder.DESC, description="Порядок сортировки")
    page: int = Field(default=1, ge=1, description="Номер страницы")
    per_page: int = Field(default=20, ge=1, le=100, description="Элементов на странице")


# ============================================================================
# COMMENT SCHEMAS
# ============================================================================


class CommentOut(Schema):
    """Схема вывода комментария."""

    id: int = Field(..., description="ID комментария")
    author: AuthorOut = Field(..., description="Автор комментария")
    content: str = Field(..., description="Текст комментария")
    parent_id: Optional[int] = Field(None, description="ID родительского комментария")
    replies_count: int = Field(..., ge=0, description="Количество ответов")
    likes: int = Field(..., ge=0, description="Количество лайков")
    is_edited: bool = Field(..., description="Был ли отредактирован")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата обновления")


class CommentIn(Schema):
    """Схема создания комментария."""

    article_slug: str = Field(..., min_length=1, description="Slug статьи")
    content: str = Field(..., min_length=2, max_length=1000, description="Текст комментария")
    parent_id: Optional[int] = Field(None, description="ID родительского комментария")


class CommentUpdate(Schema):
    """Схема обновления комментария."""

    content: str = Field(..., min_length=2, max_length=1000, description="Текст комментария")


# ============================================================================
# REACTION SCHEMAS
# ============================================================================


class ReactionIn(Schema):
    """Схема добавления реакции."""

    article_slug: str = Field(..., min_length=1, description="Slug статьи")
    reaction_type: ReactionType = Field(..., description="Тип реакции")


class ReactionOut(Schema):
    """Схема вывода статистики реакций."""

    article_slug: str = Field(..., description="Slug статьи")
    reactions: dict[str, int] = Field(..., description="Количество каждого типа реакции")
    total: int = Field(..., ge=0, description="Всего реакций")
    user_reaction: Optional[ReactionType] = Field(None, description="Реакция текущего пользователя")


# ============================================================================
# BOOKMARK SCHEMAS
# ============================================================================


class BookmarkOut(Schema):
    """Схема вывода закладки."""

    id: int = Field(..., description="ID закладки")
    article: ArticleListOut = Field(..., description="Статья")
    created_at: datetime = Field(..., description="Дата добавления")


class BookmarkIn(Schema):
    """Схема создания закладки."""

    article_slug: str = Field(..., min_length=1, description="Slug статьи")


# ============================================================================
# READING PROGRESS SCHEMAS
# ============================================================================


class ReadingProgressOut(Schema):
    """Схема вывода прогресса чтения."""

    article_slug: str = Field(..., description="Slug статьи")
    progress: int = Field(..., ge=0, le=100, description="Прогресс в процентах")
    last_position: int = Field(..., ge=0, description="Последняя позиция в пикселях")
    updated_at: datetime = Field(..., description="Дата обновления")


class ReadingProgressIn(Schema):
    """Схема обновления прогресса чтения."""

    article_slug: str = Field(..., min_length=1, description="Slug статьи")
    progress: int = Field(..., ge=0, le=100, description="Прогресс в процентах")
    last_position: int = Field(..., ge=0, description="Позиция в пикселях")


# ============================================================================
# PAGINATION SCHEMAS
# ============================================================================


class PagedArticles(Schema):
    """Пагинированный список статей."""

    items: list[ArticleListOut] = Field(..., description="Список статей")
    meta: PaginationMeta = Field(..., description="Метаданные пагинации")


class PagedComments(Schema):
    """Пагинированный список комментариев."""

    items: list[CommentOut] = Field(..., description="Список комментариев")
    meta: PaginationMeta = Field(..., description="Метаданные пагинации")


class PagedBookmarks(Schema):
    """Пагинированный список закладок."""

    items: list[BookmarkOut] = Field(..., description="Список закладок")
    meta: PaginationMeta = Field(..., description="Метаданные пагинации")


# ============================================================================
# STATISTICS SCHEMAS
# ============================================================================


class ArticleStatsOut(Schema):
    """Схема статистики статьи."""

    views: int = Field(..., ge=0, description="Просмотры")
    likes: int = Field(..., ge=0, description="Лайки")
    comments: int = Field(..., ge=0, description="Комментарии")
    bookmarks: int = Field(..., ge=0, description="Закладки")
    reactions: dict[str, int] = Field(..., description="Реакции по типам")
    reading_time: int = Field(..., ge=0, description="Среднее время чтения")


class CategoryStatsOut(Schema):
    """Схема статистики категории."""

    category: CategoryOut = Field(..., description="Категория")
    articles_count: int = Field(..., ge=0, description="Количество статей")
    total_views: int = Field(..., ge=0, description="Всего просмотров")
    total_likes: int = Field(..., ge=0, description="Всего лайков")


class BlogStatsOut(Schema):
    """Общая статистика блога."""

    total_articles: int = Field(..., ge=0, description="Всего статей")
    published_articles: int = Field(..., ge=0, description="Опубликованных статей")
    total_categories: int = Field(..., ge=0, description="Всего категорий")
    total_views: int = Field(..., ge=0, description="Всего просмотров")
    total_likes: int = Field(..., ge=0, description="Всего лайков")
    total_authors: int = Field(..., ge=0, description="Всего авторов")
    categories_stats: list[CategoryStatsOut] = Field(..., description="Статистика по категориям")
