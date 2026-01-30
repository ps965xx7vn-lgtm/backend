"""
Административный интерфейс Django для управления блогом.

Этот модуль содержит настройки Django Admin для всех моделей блога,
включая кастомные действия, отображение полей, фильтры и методы.

ModelAdmin классы:
    - CategoryAdmin: Управление категориями статей
    - ArticleAdmin: Управление статьями с полным набором функций
    - CommentAdmin: Модерация комментариев
    - SeriesAdmin: Управление сериями статей
    - ArticleReactionAdmin: Просмотр реакций пользователей
    - BookmarkAdmin: Просмотр закладок пользователей
    - ReadingProgressAdmin: Просмотр прогресса чтения
    - ArticleViewAdmin: Аналитика просмотров статей
    - AuthorAdmin: Управление профилями авторов
    - ArticleReportAdmin: Обработка жалоб на статьи
"""

from __future__ import annotations

from django.contrib import admin
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html

from .models import (
    Article,
    ArticleReaction,
    ArticleReport,
    ArticleView,
    Author,
    Bookmark,
    Category,
    Comment,
    ReadingProgress,
    Series,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для управления категориями статей.

    Функции:
    - Отображение иконок и цветов категорий
    - Подсчёт статей и связанных тегов
    - Drag-and-drop изменение порядка (через list_editable)
    - Автогенерация slug из названия
    - Группировка полей для удобства

    List Display:
        - icon_display: Цветная иконка категории
        - name: Название категории
        - badge: Бейдж для страницы тегов
        - order: Порядок сортировки (редактируемое поле)
        - articles_count: Количество опубликованных статей (кликабельная ссылка)
        - tags_count: Количество связанных тегов по ключевым словам
        - created_at: Дата создания

    Filters:
        - created_at: Фильтр по дате создания

    Custom Methods:
        - icon_display(): Отображает иконку с увеличенным размером
        - articles_count(): Подсчитывает статьи и создаёт ссылку на их список
        - tags_count(): Подсчитывает теги по ключевым словам category.tag_keywords
    """

    list_display = [
        "icon_display",
        "name",
        "badge",
        "order",
        "articles_count",
        "tags_count",
        "created_at",
    ]
    list_filter = ["created_at"]
    search_fields = ["name", "description", "tag_keywords"]
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ["order"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        ("Основная информация", {"fields": ("name", "slug", "description")}),
        ("Внешний вид", {"fields": ("icon", "color")}),
        (
            "Настройки для страницы тегов",
            {
                "fields": ("badge", "tag_keywords", "order"),
                "description": "order > 0 для показа на странице тегов. Ключевые слова через запятую.",
            },
        ),
        ("Временные метки", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    @admin.display(
        description="Иконка"
    )
    def icon_display(self, obj):
        return format_html('<span style="font-size: 18px;">{}</span>', obj.icon)


    @admin.display(
        description="Цвет"
    )
    def color_display(self, obj):
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border-radius: 3px; display: inline-block;"></div>',
            obj.color,
        )


    @admin.display(
        description="Статьи"
    )
    def articles_count(self, obj):
        count = obj.articles.filter(status="published").count()
        if count > 0:
            url = reverse("admin:blog_article_changelist") + f"?category__id__exact={obj.id}"
            return format_html('<a href="{}">{} статей</a>', url, count)
        return "0 статей"


    @admin.display(
        description="Теги"
    )
    def tags_count(self, obj):
        from taggit.models import Tag

        keywords = obj.get_tag_keywords_list()
        if not keywords:
            return "-"

        # Подсчитываем теги, содержащие ключевые слова
        count = 0
        for tag in Tag.objects.all():
            if any(kw in tag.name.lower() for kw in keywords):
                count += 1

        return f"{count} тегов" if count > 0 else "-"



@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для управления статьями блога.

    Основной и самый функциональный admin класс с полным набором возможностей
    для управления жизненным циклом статей от создания до публикации.

    Features:
    - Полное управление статусами (draft, published, archived)
    - Массовые действия для публикации и выделения статей
    - Цветовая индикация статусов и уровней сложности
    - Предварительный просмотр статьи на сайте
    - Автоматический расчёт времени чтения
    - Поддержка SEO и Open Graph метаданных
    - Интеграция с серией статей
    - Иерархия по дате публикации (date_hierarchy)

    List Display:
        - title: Название статьи
        - category: Категория
        - author: Автор (User)
        - status_display: Цветной статус (черновик/опубликовано/архив)
        - difficulty_display: Цветной бейдж сложности
        - is_featured: Флаг "рекомендуемая"
        - views_count: Количество просмотров
        - published_at: Дата публикации
        - created_at: Дата создания

    Filters:
        - status: По статусу публикации
        - difficulty: По уровню сложности
        - category: По категории
        - is_featured: По флагу "рекомендуемая"
        - allow_comments: По разрешению комментариев
        - created_at, published_at: По датам

    Fieldsets:
        - Основная информация: title, slug, subtitle
        - Контент: content, excerpt
        - Медиа: featured_image, featured_image_alt
        - Классификация: category, series, tags, difficulty
        - Авторство: author, blog_author
        - Настройки публикации: status, is_featured, allow_comments
        - SEO: meta_description, meta_keywords, schema_type
        - Social Media: og_title, og_description, og_image
        - Статистика: views_count, reading_time, published_at
        - Временные метки: created_at, updated_at
        - Предпросмотр: article_preview (ссылка на сайт)

    Custom Actions:
        - publish_articles: Массовая публикация статей
        - unpublish_articles: Снятие с публикации
        - feature_articles: Добавление в рекомендуемые
        - unfeature_articles: Удаление из рекомендуемых

    Custom Methods:
        - status_display(): Цветная индикация статуса (●)
        - difficulty_display(): Цветной бейдж уровня сложности
        - published_at_display(): Форматированная дата публикации
        - article_preview(): Кнопка предпросмотра статьи на сайте
    """

    list_display = [
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
    list_filter = [
        "status",
        "difficulty",
        "category",
        "is_featured",
        "allow_comments",
        "created_at",
        "published_at",
    ]
    search_fields = ["title", "content", "tags__name"]
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = [
        "created_at",
        "updated_at",
        "views_count",
        "reading_time",
        "published_at_display",
        "article_preview",
    ]
    # filter_horizontal = ['tags']  # Не работает с TaggableManager
    date_hierarchy = "published_at"

    fieldsets = (
        ("Основная информация", {"fields": ("title", "slug", "subtitle")}),
        ("Контент", {"fields": ("content", "excerpt"), "classes": ("wide",)}),
        ("Медиа", {"fields": ("featured_image", "featured_image_alt"), "classes": ("collapse",)}),
        ("Классификация", {"fields": ("category", "series", "series_order", "tags", "difficulty")}),
        ("Авторство", {"fields": ("author", "blog_author")}),
        ("Настройки публикации", {"fields": ("status", "is_featured", "allow_comments")}),
        (
            "SEO",
            {
                "fields": ("meta_description", "meta_keywords", "schema_type"),
                "classes": ("collapse",),
            },
        ),
        (
            "Social Media",
            {"fields": ("og_title", "og_description", "og_image"), "classes": ("collapse",)},
        ),
        (
            "Статистика",
            {
                "fields": ("views_count", "reading_time", "published_at_display"),
                "classes": ("collapse",),
            },
        ),
        ("Временные метки", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
        ("Предварительный просмотр", {"fields": ("article_preview",), "classes": ("collapse",)}),
    )

    actions = ["publish_articles", "unpublish_articles", "feature_articles", "unfeature_articles"]

    @admin.display(
        description="Статус"
    )
    def status_display(self, obj):
        colors = {"draft": "#f39c12", "published": "#27ae60", "archived": "#95a5a6"}
        return format_html(
            '<span style="color: {}; font-weight: bold;">● {}</span>',
            colors.get(obj.status, "#000"),
            obj.get_status_display(),
        )


    @admin.display(
        description="Сложность"
    )
    def difficulty_display(self, obj):
        colors = {
            "beginner": "#2ecc71",
            "intermediate": "#f39c12",
            "advanced": "#e74c3c",
            "expert": "#9b59b6",
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            colors.get(obj.difficulty, "#000"),
            obj.get_difficulty_display(),
        )


    @admin.display(
        description="Опубликовано"
    )
    def published_at_display(self, obj):
        if obj.published_at:
            return obj.published_at.strftime("%d.%m.%Y %H:%M")
        return "Не опубликовано"


    @admin.display(
        description="Предварительный просмотр"
    )
    def article_preview(self, obj):
        if obj.pk:
            preview_url = obj.get_absolute_url()
            return format_html(
                '<a href="{}" target="_blank" class="button">Посмотреть на сайте</a>', preview_url
            )
        return "Сохраните статью для предварительного просмотра"


    @admin.action(
        description="Опубликовать выбранные статьи"
    )
    def publish_articles(self, request, queryset):
        updated = queryset.update(status="published", published_at=timezone.now())
        self.message_user(request, f"{updated} статей опубликовано.")


    @admin.action(
        description="Снять с публикации"
    )
    def unpublish_articles(self, request, queryset):
        updated = queryset.update(status="draft")
        self.message_user(request, f"{updated} статей отправлено в черновики.")


    @admin.action(
        description="Добавить в рекомендуемые"
    )
    def feature_articles(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f"{updated} статей добавлено в рекомендуемые.")


    @admin.action(
        description="Убрать из рекомендуемых"
    )
    def unfeature_articles(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f"{updated} статей удалено из рекомендуемых.")



@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для модерации комментариев к статьям.

    Позволяет администраторам модерировать комментарии, одобрять или скрывать их,
    а также отслеживать вложенную структуру ответов.

    List Display:
        - __str__: Строковое представление (автор - статья - отрывок)
        - article: Статья, к которой оставлен комментарий
        - author: Автор комментария
        - is_approved: Флаг одобрения
        - created_at: Дата создания

    Filters:
        - is_approved: По статусу одобрения
        - created_at: По дате создания
        - article__category: По категории статьи

    Custom Actions:
        - approve_comments: Массовое одобрение комментариев
        - disapprove_comments: Массовое скрытие комментариев

    Note:
        Поддерживается вложенность через поле parent для ответов на комментарии
    """

    list_display = ["__str__", "article", "author", "is_approved", "created_at"]
    list_filter = ["is_approved", "created_at", "article__category"]
    search_fields = ["content", "author__username", "article__title"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        ("Основная информация", {"fields": ("article", "author", "parent")}),
        ("Содержание", {"fields": ("content",), "classes": ("wide",)}),
        ("Настройки", {"fields": ("is_approved",)}),
        ("Временные метки", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    actions = ["approve_comments", "disapprove_comments"]

    @admin.action(
        description="Одобрить комментарии"
    )
    def approve_comments(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"{updated} комментариев одобрено.")


    @admin.action(
        description="Скрыть комментарии"
    )
    def disapprove_comments(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f"{updated} комментариев скрыто.")



@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для управления сериями статей.

    Серии позволяют группировать связанные статьи в последовательные курсы
    или учебные материалы с определённым порядком чтения.

    List Display:
        - title: Название серии
        - slug: URL-слаг
        - status: Статус серии
        - article_count: Количество статей в серии
        - author: Автор серии
        - created_at: Дата создания

    Filters:
        - status: По статусу серии
        - created_at: По дате создания
        - author: По автору

    Features:
        - Автогенерация slug из названия
        - Автоматический подсчёт статей в серии (article_count readonly)
        - Поддержка обложки серии (cover_image)
        - SEO-оптимизация (meta_description)

    Note:
        Статьи в серии упорядочиваются через поле Article.series_order
    """

    list_display = ["title", "slug", "status", "article_count", "author", "created_at"]
    list_filter = ["status", "created_at", "author"]
    search_fields = ["title", "description"]
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ["created_at", "updated_at", "article_count"]

    fieldsets = (
        ("Основная информация", {"fields": ("title", "slug", "description", "cover_image")}),
        ("Настройки", {"fields": ("status", "author")}),
        ("SEO", {"fields": ("meta_description",), "classes": ("collapse",)}),
        (
            "Статистика",
            {"fields": ("article_count", "created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(ArticleReaction)
class ArticleReactionAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для просмотра реакций пользователей на статьи.

    Реакции (эмодзи) позволяют пользователям выражать своё отношение к статье:
    👍 Нравится, ❤️ Супер, 💡 Полезно, 🤔 Интересно, 🤩 Потрясающе

    List Display:
        - user: Пользователь, оставивший реакцию
        - article: Статья
        - reaction_type: Тип реакции (like, love, helpful, insightful, amazing)
        - created_at: Дата создания

    Filters:
        - reaction_type: По типу реакции
        - created_at: По дате создания

    Permissions:
        - has_add_permission: False (реакции создаются только через API)

    Note:
        Один пользователь может оставить только одну реакцию на статью
        (ограничение unique_together в модели)
    """

    list_display = ["user", "article", "reaction_type", "created_at"]
    list_filter = ["reaction_type", "created_at"]
    search_fields = ["user__username", "article__title"]
    readonly_fields = ["created_at"]

    def has_add_permission(self, request):
        return False  # Реакции создаются только через API


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для просмотра закладок пользователей.

    Закладки позволяют пользователям сохранять интересные статьи для
    последующего чтения, добавлять личные заметки и организовывать по папкам.

    List Display:
        - user: Пользователь, создавший закладку
        - article: Добавленная в закладки статья
        - folder: Папка для группировки (может быть пустой)
        - created_at: Дата добавления в закладки

    Filters:
        - folder: По названию папки
        - created_at: По дате создания

    Search:
        - user__username: По имени пользователя
        - article__title: По названию статьи
        - notes: По содержимому личных заметок

    Note:
        Используется для персонализации опыта пользователя и аналитики
        популярности контента
    """

    list_display = ["user", "article", "folder", "created_at"]
    list_filter = ["folder", "created_at"]
    search_fields = ["user__username", "article__title", "notes"]
    readonly_fields = ["created_at"]


@admin.register(ReadingProgress)
class ReadingProgressAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для просмотра прогресса чтения статей.

    Отслеживает, сколько пользователь прочитал каждой статьи, сколько времени
    потратил на чтение, и текущий статус (не начато, в процессе, завершено).

    List Display:
        - user: Пользователь
        - article: Читаемая статья
        - progress_percentage: Прогресс в процентах (0-100)
        - status: Статус чтения (not_started, in_progress, completed)
        - last_read_at: Дата последнего сеанса чтения

    Filters:
        - status: По статусу чтения
        - last_read_at: По дате последнего чтения

    Readonly Fields:
        - started_at: Дата начала чтения
        - completed_at: Дата завершения
        - last_read_at: Дата последнего обновления (auto_now)

    Permissions:
        - has_add_permission: False (прогресс создаётся автоматически)

    Note:
        Используется для аналитики вовлечённости пользователей и возобновления
        чтения с последнего места
    """

    list_display = ["user", "article", "progress_percentage", "status", "last_read_at"]
    list_filter = ["status", "last_read_at"]
    search_fields = ["user__username", "article__title"]
    readonly_fields = ["started_at", "completed_at", "last_read_at"]

    def has_add_permission(self, request):
        return False  # Прогресс создается автоматически


@admin.register(ArticleView)
class ArticleViewAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для детальной аналитики просмотров статей.

    Собирает расширенную информацию о каждом просмотре статьи, включая
    технические данные (IP, User-Agent), поведенческие метрики (время на странице,
    глубина прокрутки) и источник перехода.

    List Display:
        - article: Просмотренная статья
        - user_display: Пользователь или 'Анонимный' (custom method)
        - ip_address: IP-адрес посетителя
        - time_on_page: Время на странице в секундах
        - scroll_depth: Глубина прокрутки в процентах
        - viewed_at: Дата и время просмотра

    Filters:
        - is_unique: По флагу уникальности просмотра
        - viewed_at: По дате просмотра

    Search:
        - article__title: По названию статьи
        - user__username: По имени пользователя
        - ip_address: По IP-адресу

    Permissions:
        - has_add_permission: False (просмотры создаются автоматически)

    Custom Methods:
        - user_display(): Показывает username или 'Анонимный' для неавторизованных

    Note:
        Используется для глубокой аналитики поведения пользователей,
        определения популярности контента и источников трафика
    """

    list_display = [
        "article",
        "user_display",
        "ip_address",
        "time_on_page",
        "scroll_depth",
        "viewed_at",
    ]
    list_filter = ["is_unique", "viewed_at"]
    search_fields = ["article__title", "user__username", "ip_address"]
    readonly_fields = ["viewed_at"]

    @admin.display(
        description="Пользователь"
    )
    def user_display(self, obj):
        return obj.user.username if obj.user else "Анонимный"


    def has_add_permission(self, request):
        return False  # Просмотры создаются автоматически


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для управления профилями авторов блога.

    Расширенные профили авторов с профессиональной информацией, социальными сетями,
    статистикой публикаций и настройками видимости.

    List Display:
        - display_name: Отображаемое имя автора
        - user_email: Email пользователя (custom method)
        - job_title: Должность
        - company: Компания
        - articles_count: Количество опубликованных статей
        - total_views: Общее количество просмотров статей автора
        - is_featured: Флаг "рекомендуемый автор"
        - created_at: Дата создания профиля

    Filters:
        - is_featured: По флагу "рекомендуемый"
        - accept_guest_posts: По принятию гостевых постов
        - created_at: По дате создания

    Fieldsets:
        - Основная информация: user, display_name, slug
        - Профессиональная информация: job_title, company, specializations, bio
        - Изображения: avatar, cover_image
        - Социальные сети: website, twitter, github, linkedin, youtube, telegram
        - Настройки: is_featured, show_email, accept_guest_posts
        - Статистика: articles_count, total_views, total_reactions (readonly)
        - Временные метки: created_at, updated_at

    Custom Actions:
        - update_statistics: Пересчёт статистики для выбранных авторов
        - feature_authors: Массовое добавление в рекомендуемые
        - unfeature_authors: Массовое удаление из рекомендуемых

    Custom Methods:
        - user_email(): Отображает email связанного User объекта

    Note:
        Автогенерация slug из display_name. Статистика обновляется автоматически
        при публикации статей через метод Author.update_statistics()
    """

    list_display = [
        "display_name",
        "user_email",
        "job_title",
        "company",
        "articles_count",
        "total_views",
        "is_featured",
        "created_at",
    ]
    list_filter = ["is_featured", "accept_guest_posts", "created_at"]
    search_fields = ["display_name", "user__email", "bio", "job_title", "company"]
    prepopulated_fields = {"slug": ("display_name",)}
    readonly_fields = [
        "created_at",
        "updated_at",
        "articles_count",
        "total_views",
        "total_reactions",
    ]

    fieldsets = (
        ("Основная информация", {"fields": ("user", "display_name", "slug")}),
        (
            "Профессиональная информация",
            {"fields": ("job_title", "company", "specializations", "bio")},
        ),
        ("Изображения", {"fields": ("avatar", "cover_image")}),
        (
            "Социальные сети",
            {
                "fields": ("website", "twitter", "github", "linkedin", "youtube", "telegram"),
                "classes": ("collapse",),
            },
        ),
        ("Настройки", {"fields": ("is_featured", "show_email", "accept_guest_posts")}),
        (
            "Статистика",
            {
                "fields": ("articles_count", "total_views", "total_reactions"),
                "classes": ("collapse",),
            },
        ),
        ("Временные метки", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    actions = ["update_statistics", "feature_authors", "unfeature_authors"]

    @admin.display(
        description="Email"
    )
    def user_email(self, obj):
        return obj.user.email


    @admin.action(
        description="Обновить статистику"
    )
    def update_statistics(self, request, queryset):
        for author in queryset:
            author.update_statistics()
        self.message_user(request, f"Статистика обновлена для {queryset.count()} авторов.")


    @admin.action(
        description="Добавить в рекомендуемые"
    )
    def feature_authors(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f"{updated} авторов добавлено в рекомендуемые.")


    @admin.action(
        description="Убрать из рекомендуемых"
    )
    def unfeature_authors(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f"{updated} авторов убрано из рекомендуемых.")



@admin.register(ArticleReport)
class ArticleReportAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для обработки жалоб на статьи.

    Позволяет пользователям сообщать о проблемах со статьями (спам, неподходящий
    контент, дезинформация, нарушение авторских прав). Администраторы могут
    просматривать жалобы, добавлять заметки и изменять статус обработки.

    List Display:
        - article: Статья, на которую подана жалоба
        - reporter_display: Отправитель (username или 'Анонимный' с серым цветом)
        - reason_type: Тип жалобы (spam, inappropriate, misinformation, copyright, other)
        - status: Статус обработки (pending, reviewed, resolved, rejected)
        - reported_at: Дата подачи жалобы

    Filters:
        - status: По статусу обработки
        - reason_type: По типу жалобы
        - reported_at: По дате подачи

    Fieldsets:
        - Информация о жалобе: article, reporter, reason_type, reason, reported_at
        - Обработка: status, admin_notes, reviewed_at

    Custom Actions:
        - mark_as_reviewed: Массовая отметка как "рассмотрено"
        - mark_as_resolved: Массовая отметка как "решено"
        - mark_as_rejected: Массовая отметка как "отклонено"

    Custom Methods:
        - reporter_display(): Показывает username или стилизованное 'Анонимный'

    Workflow:
        1. Пользователь создаёт жалобу (status='pending')
        2. Администратор рассматривает (action: mark_as_reviewed)
        3. Администратор принимает решение (mark_as_resolved или mark_as_rejected)
        4. reviewed_at устанавливается автоматически при изменении статуса

    Note:
        Жалобы могут быть анонимными (reporter=None) для незарегистрированных
        пользователей. Используется для модерации контента и защиты от нарушений.
    """

    list_display = ["article", "reporter_display", "reason_type", "status", "reported_at"]
    list_filter = ["status", "reason_type", "reported_at"]
    search_fields = ["article__title", "reporter__username", "reason"]
    readonly_fields = ["reported_at"]

    fieldsets = (
        (
            "Информация о жалобе",
            {"fields": ("article", "reporter", "reason_type", "reason", "reported_at")},
        ),
        ("Обработка", {"fields": ("status", "admin_notes", "reviewed_at")}),
    )

    actions = ["mark_as_reviewed", "mark_as_resolved", "mark_as_rejected"]

    @admin.display(
        description="Отправитель"
    )
    def reporter_display(self, obj):
        if obj.reporter:
            return obj.reporter.username
        return format_html('<span style="color: #9ca3af;">Анонимный</span>')


    @admin.action(
        description="Отметить как рассмотренные"
    )
    def mark_as_reviewed(self, request, queryset):
        updated = queryset.update(status="reviewed", reviewed_at=timezone.now())
        self.message_user(request, f"{updated} жалоб отмечено как рассмотренные.")


    @admin.action(
        description="Отметить как решённые"
    )
    def mark_as_resolved(self, request, queryset):
        updated = queryset.update(status="resolved", reviewed_at=timezone.now())
        self.message_user(request, f"{updated} жалоб отмечено как решённые.")


    @admin.action(
        description="Отметить как отклонённые"
    )
    def mark_as_rejected(self, request, queryset):
        updated = queryset.update(status="rejected", reviewed_at=timezone.now())
        self.message_user(request, f"{updated} жалоб отмечено как отклонённые.")

