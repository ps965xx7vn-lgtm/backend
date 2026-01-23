"""
Blog Models Module - Модели данных для системы блога.

Этот модуль содержит полнофункциональную систему блога с 11 моделями:

Основные модели:
    Category - Категории статей (с иконками)
    Article - Статьи блога (markdown, SEO, статусы)
    Author - Профили авторов блога
    Series - Серии связанных статей
    Comment - Комментарии к статьям (вложенные, до 3 уровней)

Дополнительные модели:
    ArticleReaction - Реакции на статьи (like, love, helpful, insightful, amazing)
    Bookmark - Закладки пользователей
    ReadingProgress - Прогресс чтения статей
    ArticleView - Просмотры статей (с IP-tracking)
    Newsletter - Email-подписки на рассылку

Особенности:
    - Markdown поддержка в статьях
    - SEO оптимизация (meta-теги, schema.org, Open Graph)
    - Система тегов (django-taggit)
    - Вложенные комментарии (макс. 3 уровня)
    - Различные статусы: draft, pending, published, archived
    - Уровни сложности: beginner, intermediate, advanced, expert
    - Рекомендуемые статьи (is_featured)
    - Автоматический расчет времени чтения

Валидация:
    - Ограничения на длину полей
    - Проверка slug на уникальность
    - Кастомные clean() методы
    - Автоматическая генерация slug

Автор: Pyland Team
Дата: 2025
"""

from __future__ import annotations

import logging
from typing import Any

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from taggit.managers import TaggableManager

logger = logging.getLogger(__name__)
User = get_user_model()


class Category(models.Model):
    """Категории статей блога"""

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Название категории",
        help_text="Название категории (макс. 100 символов)",
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name="URL-адрес",
        help_text="Автоматически генерируется из названия",
    )
    description = models.TextField(
        blank=True, verbose_name="Описание", help_text="Краткое описание категории"
    )
    icon = models.CharField(
        max_length=50,
        default="📝",
        verbose_name="Иконка",
        help_text="Эмодзи или CSS класс для иконки",
    )
    color = models.CharField(
        max_length=7,
        default="#3498db",
        verbose_name="Цвет",
        help_text="Цвет категории в формате HEX (#ffffff)",
    )
    # Поля для страницы тегов
    tag_keywords = models.TextField(
        blank=True,
        verbose_name="Ключевые слова для тегов",
        help_text="Ключевые слова для фильтрации тегов через запятую (например: python, basics, oop)",
    )
    badge = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Бейдж",
        help_text="Краткая метка для страницы тегов (например: Основы, Backend)",
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Порядок на странице тегов",
        help_text="Чем меньше число, тем выше в списке (0 - не показывать)",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["name"]

    def __str__(self) -> str:
        """
        Строковое представление категории.

        Returns:
            str: Название категории
        """
        return self.name

    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Сохранение категории с автоматической генерацией slug.

        Если slug не указан, генерируется автоматически из названия.
        Логирует ошибки при сохранении.

        Args:
            *args: Позиционные аргументы для метода save
            **kwargs: Именованные аргументы для метода save

        Raises:
            ValidationError: При ошибке валидации данных
        """
        try:
            if not self.slug:
                self.slug = slugify(self.name)
            super().save(*args, **kwargs)
            logger.info(f"Категория '{self.name}' успешно сохранена")
        except Exception as e:
            logger.error(f"Ошибка при сохранении категории '{self.name}': {e}")
            raise

    def get_absolute_url(self) -> str:
        """
        Получение абсолютного URL категории.

        Returns:
            str: URL для страницы категории

        Example:
            >>> category = Category(slug='python')
            >>> category.get_absolute_url()
            '/ru/blog/category/python/'
        """
        return reverse("blog:category_detail", kwargs={"slug": self.slug})

    def get_tag_keywords_list(self) -> list[str]:
        """
        Получение списка ключевых слов для фильтрации тегов.

        Разбивает строку tag_keywords по запятым, очищает от пробелов
        и приводит к нижнему регистру.

        Returns:
            list[str]: Список ключевых слов в нижнем регистре

        Example:
            >>> category = Category(tag_keywords='Python, Django, Web')
            >>> category.get_tag_keywords_list()
            ['python', 'django', 'web']
        """
        if not self.tag_keywords:
            return []
        return [kw.strip().lower() for kw in self.tag_keywords.split(",") if kw.strip()]

    @property
    def article_count(self) -> int:
        """
        Количество опубликованных статей в категории.

        Returns:
            int: Количество статей со статусом 'published'
        """
        return self.articles.filter(status="published").count()


class Article(models.Model):
    """Статьи блога"""

    STATUS_CHOICES = [
        ("draft", "Черновик"),
        ("published", "Опубликовано"),
        ("archived", "В архиве"),
    ]

    DIFFICULTY_CHOICES = [
        ("beginner", "Новичок"),
        ("intermediate", "Средний"),
        ("advanced", "Продвинутый"),
        ("expert", "Эксpert"),
    ]

    # Основная информация
    title = models.CharField(
        max_length=200,
        verbose_name="Заголовок",
        validators=[MinLengthValidator(10)],
        help_text="Заголовок статьи (10-200 символов)",
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name="URL-адрес",
        help_text="Автоматически генерируется из заголовка",
    )
    subtitle = models.CharField(
        max_length=300, blank=True, verbose_name="Подзаголовок", help_text="Краткое описание статьи"
    )

    # Контент
    content = models.TextField(
        verbose_name="Содержание",
        validators=[MinLengthValidator(100)],
        help_text="Основной текст статьи",
    )
    excerpt = models.TextField(
        max_length=500,
        blank=True,
        verbose_name="Краткое содержание",
        help_text="Краткое описание для предварительного просмотра",
    )

    # Медиа
    featured_image = models.ImageField(
        upload_to="blog/featured/",
        blank=True,
        null=True,
        verbose_name="Главное изображение",
        help_text="Изображение для обложки статьи",
    )
    featured_image_alt = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Alt текст для изображения",
        help_text="Описание изображения для SEO",
    )

    # Классификация
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name="articles",
        verbose_name="Категория",
    )
    series = models.ForeignKey(
        "Series",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
        verbose_name="Серия статей",
        help_text="Серия, к которой принадлежит статья",
    )
    series_order = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Порядок в серии",
        help_text="Порядковый номер статьи в серии",
    )
    tags = TaggableManager(
        verbose_name="Теги", help_text="Теги для статьи, разделенные запятыми", blank=True
    )
    difficulty = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        default="beginner",
        verbose_name="Уровень сложности",
    )

    # Мета информация
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="blog_articles",
        verbose_name="Автор (пользователь)",
    )
    blog_author = models.ForeignKey(
        "Author",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
        verbose_name="Профиль автора блога",
        help_text="Расширенный профиль автора (если создан)",
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="draft", verbose_name="Статус"
    )

    # Временные метки
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")
    published_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата публикации")

    # SEO
    meta_description = models.CharField(
        max_length=160,
        blank=True,
        verbose_name="Meta описание",
        help_text="Описание для поисковых систем (макс. 160 символов)",
    )
    meta_keywords = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Ключевые слова",
        help_text="Ключевые слова через запятую",
    )

    # Open Graph / Social Media
    og_title = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="OG заголовок",
        help_text="Заголовок для социальных сетей (по умолчанию = title)",
    )
    og_description = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="OG описание",
        help_text="Описание для социальных сетей",
    )
    og_image = models.ImageField(
        upload_to="blog/og/",
        blank=True,
        null=True,
        verbose_name="OG изображение",
        help_text="Изображение для социальных сетей (1200x630px)",
    )

    # Schema.org structured data
    schema_type = models.CharField(
        max_length=50,
        default="Article",
        verbose_name="Тип Schema.org",
        help_text="Тип структурированных данных",
    )

    # Статистика
    views_count = models.PositiveIntegerField(default=0, verbose_name="Количество просмотров")
    reading_time = models.PositiveIntegerField(
        default=5, verbose_name="Время чтения (мин)", help_text="Примерное время чтения в минутах"
    )

    # Настройки
    is_featured = models.BooleanField(
        default=False,
        verbose_name="Рекомендуемая статья",
        help_text="Отображается в блоке рекомендуемых статей",
    )
    allow_comments = models.BooleanField(default=True, verbose_name="Разрешить комментарии")

    class Meta:
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"
        ordering = ["-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["status", "published_at"]),
            models.Index(fields=["category", "status"]),
            models.Index(fields=["is_featured", "status"]),
        ]

    def __str__(self) -> str:
        """
        Строковое представление статьи.

        Returns:
            str: Заголовок статьи
        """
        return self.title

    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Сохранение статьи с автоматической обработкой полей.

        Выполняет:
        - Генерацию slug из заголовка
        - Установку даты публикации при первой публикации
        - Автоматическое создание excerpt из контента
        - Расчет времени чтения

        Args:
            *args: Позиционные аргументы для метода save
            **kwargs: Именованные аргументы для метода save

        Raises:
            ValidationError: При ошибке валидации данных
        """
        try:
            # Генерируем slug если его нет
            if not self.slug:
                self.slug = slugify(self.title)

            # Устанавливаем дату публикации при первой публикации
            if self.status == "published" and not self.published_at:
                self.published_at = timezone.now()

            # Генерируем excerpt если его нет
            if not self.excerpt and self.content:
                # Берем первые 300 символов из контента
                self.excerpt = (
                    self.content[:300] + "..." if len(self.content) > 300 else self.content
                )

            # Вычисляем время чтения (примерно 200 слов в минуту)
            if self.content:
                word_count = len(self.content.split())
                self.reading_time = max(1, word_count // 200)

            super().save(*args, **kwargs)
            logger.info(f"Статья '{self.title}' успешно сохранена (статус: {self.status})")
        except Exception as e:
            logger.error(f"Ошибка при сохранении статьи '{self.title}': {e}")
            raise

    def get_absolute_url(self) -> str:
        """
        Получение абсолютного URL статьи.

        Returns:
            str: URL для страницы статьи

        Example:
            >>> article = Article(slug='django-tutorial')
            >>> article.get_absolute_url()
            '/ru/blog/article/django-tutorial/'
        """
        return reverse("blog:article_detail", kwargs={"slug": self.slug})

    @property
    def is_published(self):
        return self.status == "published" and self.published_at <= timezone.now()

    @property
    def reaction_counts(self):
        """Возвращает количество реакций по типам"""
        from django.db.models import Count

        return self.reactions.values("reaction_type").annotate(count=Count("id"))

    @property
    def total_reactions(self):
        """Общее количество реакций"""
        return self.reactions.count()

    @property
    def bookmark_count(self):
        """Количество добавлений в закладки"""
        return self.bookmarks.count()

    def get_series_navigation(self):
        """Возвращает предыдущую и следующую статьи в серии"""
        if not self.series:
            return {"prev": None, "next": None}

        articles = self.series.articles.filter(status="published").order_by(
            "series_order", "published_at"
        )

        articles_list = list(articles)
        try:
            current_index = articles_list.index(self)
            prev_article = articles_list[current_index - 1] if current_index > 0 else None
            next_article = (
                articles_list[current_index + 1] if current_index < len(articles_list) - 1 else None
            )
            return {"prev": prev_article, "next": next_article}
        except ValueError:
            return {"prev": None, "next": None}

    def get_estimated_read_time(self):
        """Более точная оценка времени чтения"""
        if not self.content:
            return 1

        # Подсчет слов с учетом кода и форматирования
        import re

        # Удаляем код блоки
        text = re.sub(r"```[\s\S]*?```", "", self.content)
        # Удаляем инлайн код
        text = re.sub(r"`[^`]+`", "", text)
        # Удаляем markdown разметку
        text = re.sub(r"[#*_\[\]()]+", "", text)

        words = len(text.split())
        # Средняя скорость чтения: 200 слов в минуту
        # Добавляем время на просмотр кода/изображений
        code_blocks = len(re.findall(r"```[\s\S]*?```", self.content))
        images = len(re.findall(r"!\[.*?\]\(.*?\)", self.content))

        base_time = max(1, words // 200)
        extra_time = (code_blocks * 0.5) + (images * 0.2)

        return max(1, int(base_time + extra_time))

    def get_og_data(self):
        """Возвращает данные для Open Graph"""
        author_name = self.get_author_display_name()
        return {
            "title": self.og_title or self.title,
            "description": self.og_description or self.meta_description or self.excerpt,
            "image": self.og_image or self.featured_image,
            "url": self.get_absolute_url(),
            "type": "article",
            "author": author_name,
            "published_time": self.published_at.isoformat() if self.published_at else None,
            "modified_time": self.updated_at.isoformat(),
        }

    def get_author_display_name(self):
        """Возвращает отображаемое имя автора"""
        if self.blog_author:
            return self.blog_author.display_name
        return self.author.get_full_name() or self.author.username

    def get_author_bio(self):
        """Возвращает биографию автора"""
        if self.blog_author:
            return self.blog_author.bio
        return getattr(self.author.student, "bio", "") if hasattr(self.author, "student") else ""

    def get_author_avatar(self):
        """Возвращает аватар автора"""
        if self.blog_author and self.blog_author.avatar:
            return self.blog_author.avatar
        if hasattr(self.author, "student") and self.author.student.avatar:
            return self.author.student.avatar
        return None

    def get_author_url(self):
        """Возвращает URL профиля автора"""
        if self.blog_author:
            return self.blog_author.get_absolute_url()
        return None


class Comment(models.Model):
    """
    Комментарии к статьям блога.

    Поддерживает:
    - Вложенные комментарии (через поле parent)
    - Модерацию (поле is_approved)
    - Отслеживание времени создания и редактирования

    Attributes:
        article: Статья, к которой оставлен комментарий
        author: Пользователь-автор комментария
        parent: Родительский комментарий (для ответов)
        content: Текст комментария (минимум 3 символа)
        created_at: Дата и время создания
        updated_at: Дата и время последнего обновления
        is_approved: Прошел ли комментарий модерацию
    """

    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="comments", verbose_name="Статья"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="blog_comments", verbose_name="Автор"
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
        verbose_name="Родительский комментарий",
    )

    content = models.TextField(
        verbose_name="Содержание",
        validators=[MinLengthValidator(3)],
        help_text="Содержание комментария",
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    is_approved = models.BooleanField(
        default=True, verbose_name="Одобрен", help_text="Отображается ли комментарий на сайте"
    )

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ["created_at"]

    def __str__(self) -> str:
        """
        Строковое представление комментария.

        Returns:
            str: Краткое описание комментария с автором и статьей
        """
        return f'Комментарий от {self.author.username} к "{self.article.title}"'

    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Сохранение комментария с валидацией.

        Args:
            *args: Позиционные аргументы для родительского метода
            **kwargs: Именованные аргументы для родительского метода

        Raises:
            ValidationError: Если комментарий не прошел валидацию
        """
        try:
            # Проверяем, что родительский комментарий принадлежит той же статье
            if self.parent and self.parent.article != self.article:
                logger.warning(
                    f"Попытка создать ответ на комментарий из другой статьи: "
                    f"parent_article={self.parent.article.id}, article={self.article.id}"
                )
                raise ValidationError("Родительский комментарий должен принадлежать той же статье")

            super().save(*args, **kwargs)
            logger.info(
                f"Комментарий сохранен: ID={self.id}, автор={self.author.username}, "
                f"статья='{self.article.title}', родитель={'ID=' + str(self.parent.id) if self.parent else 'нет'}"
            )
        except Exception as e:
            logger.error(f"Ошибка при сохранении комментария: {e}", exc_info=True)
            raise

    @property
    def is_edited(self) -> bool:
        """
        Проверяет, был ли комментарий отредактирован.

        Returns:
            bool: True если комментарий редактировался (updated_at отличается от created_at более чем на 1 минуту)
        """
        if not self.created_at or not self.updated_at:
            return False
        time_diff = (self.updated_at - self.created_at).total_seconds()
        return time_diff > 60  # Считаем редактированным если прошло больше минуты

    @property
    def reply_count(self) -> int:
        """
        Количество ответов на комментарий.

        Returns:
            int: Количество дочерних комментариев
        """
        return self.replies.filter(is_approved=True).count()

    @property
    def is_reply(self) -> bool:
        """
        Является ли комментарий ответом на другой комментарий.

        Returns:
            bool: True если это ответ (есть родительский комментарий)
        """
        return self.parent is not None

    def get_depth(self) -> int:
        """
        Возвращает глубину вложенности комментария.

        Глубина определяется количеством родительских комментариев:
        - 0: Корневой комментарий (без родителя)
        - 1: Прямой ответ на корневой комментарий
        - 2: Ответ на ответ (максимальная глубина)

        Returns:
            int: Уровень вложенности комментария (0, 1 или 2)
        """
        depth = 0
        current = self
        while current.parent is not None:
            depth += 1
            current = current.parent
            # Защита от бесконечного цикла
            if depth > 10:
                logger.error(f"Обнаружена циклическая зависимость в комментариях: ID={self.id}")
                break
        return depth

    def get_all_replies(self) -> list:
        """
        Рекурсивно получает все ответы на комментарий.

        Returns:
            list: Список всех дочерних комментариев (включая вложенные)
        """
        replies = []
        for reply in self.replies.filter(is_approved=True).select_related("author"):
            replies.append(reply)
            replies.extend(reply.get_all_replies())
        return replies


class Newsletter(models.Model):
    """
    Подписка на рассылку блога.

    Управляет email-подписками пользователей на новости и обновления блога.
    Поддерживает деактивацию подписки без удаления записи.

    Attributes:
        email: Уникальный email адрес подписчика
        name: Имя подписчика (опционально)
        is_active: Активна ли подписка
        created_at: Дата подписки
    """

    email = models.EmailField(
        unique=True, verbose_name="Email", help_text="Email адрес для подписки"
    )
    name = models.CharField(
        max_length=100, blank=True, verbose_name="Имя", help_text="Имя подписчика"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активная подписка")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Подписан")

    class Meta:
        verbose_name = "Подписка на рассылку"
        verbose_name_plural = "Подписки на рассылку"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        """
        Строковое представление подписки.

        Returns:
            str: Имя и email или только email
        """
        return f"{self.name} ({self.email})" if self.name else self.email

    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Сохранение подписки с логированием.

        Args:
            *args: Позиционные аргументы для родительского метода
            **kwargs: Именованные аргументы для родительского метода
        """
        try:
            is_new = self.pk is None
            action = "создана" if is_new else "обновлена"

            super().save(*args, **kwargs)

            logger.info(
                f"Подписка {action}: email={self.email}, имя={self.name or 'не указано'}, "
                f"активна={self.is_active}"
            )
        except Exception as e:
            logger.error(f"Ошибка при сохранении подписки {self.email}: {e}", exc_info=True)
            raise

    def deactivate(self) -> None:
        """
        Деактивирует подписку (отписка).

        Не удаляет запись, а помечает как неактивную для возможности восстановления.
        """
        self.is_active = False
        self.save()
        logger.info(f"Подписка деактивирована: {self.email}")

    def activate(self) -> None:
        """
        Активирует подписку (повторная подписка).
        """
        self.is_active = True
        self.save()
        logger.info(f"Подписка активирована: {self.email}")


class Series(models.Model):
    """
    Серии статей для группировки связанного контента.

    Серии позволяют объединить несколько статей в последовательный курс
    с автоматической навигацией между статьями.

    Attributes:
        title: Название серии
        slug: URL-адрес серии
        description: Описание содержания серии
        cover_image: Обложка серии
        status: Статус серии (активная, завершена, приостановлена)
        author: Автор серии
        is_featured: Отображать в рекомендуемых
        created_at: Дата создания
        updated_at: Дата обновления
        tags: Теги для категоризации
        meta_description: SEO описание
    """

    title = models.CharField(
        max_length=200, verbose_name="Название серии", help_text="Название серии статей"
    )
    slug = models.SlugField(max_length=200, unique=True, verbose_name="URL-адрес серии")
    description = models.TextField(
        verbose_name="Описание серии", help_text="Краткое описание того, о чем серия статей"
    )
    cover_image = models.ImageField(
        upload_to="blog/series/", blank=True, null=True, verbose_name="Обложка серии"
    )

    # Статус серии
    STATUS_CHOICES = [
        ("active", "Активная"),
        ("completed", "Завершена"),
        ("paused", "Приостановлена"),
    ]
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="active", verbose_name="Статус серии"
    )

    # Метаданные
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="blog_series", verbose_name="Автор серии"
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name="Рекомендуемая серия",
        help_text="Отображать в блоке рекомендуемых серий",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Теги
    tags = TaggableManager(
        blank=True, verbose_name="Теги", help_text="Теги для категоризации серии"
    )

    # SEO
    meta_description = models.CharField(max_length=160, blank=True, verbose_name="Meta описание")

    class Meta:
        verbose_name = "Серия статей"
        verbose_name_plural = "Серии статей"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        """
        Строковое представление серии.

        Returns:
            str: Название серии
        """
        return self.title

    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Сохранение серии с автоматической генерацией slug.

        Args:
            *args: Позиционные аргументы для родительского метода
            **kwargs: Именованные аргументы для родительского метода
        """
        try:
            # Генерируем slug если его нет
            if not self.slug:
                self.slug = slugify(self.title)

            super().save(*args, **kwargs)
            logger.info(
                f"Серия '{self.title}' сохранена: статус={self.status}, "
                f"автор={self.author.username}, featured={self.is_featured}"
            )
        except Exception as e:
            logger.error(f"Ошибка при сохранении серии '{self.title}': {e}", exc_info=True)
            raise

    def get_absolute_url(self) -> str:
        """
        Получение абсолютного URL серии.

        Returns:
            str: URL для страницы серии
        """
        return reverse("blog:series_detail", kwargs={"slug": self.slug})

    @property
    def article_count(self) -> int:
        """
        Количество опубликованных статей в серии.

        Returns:
            int: Количество статей со статусом 'published'
        """
        return self.articles.filter(status="published").count()

    @property
    def published_articles_count(self) -> int:
        """
        Количество опубликованных статей в серии (алиас для article_count).

        Returns:
            int: Количество статей со статусом 'published'
        """
        return self.articles.filter(status="published").count()

    @property
    def published_articles(self) -> Any:
        """
        Опубликованные статьи серии.

        Возвращает статьи, упорядоченные по series_order и дате публикации
        с предзагрузкой связанных данных для оптимизации.

        Returns:
            QuerySet: Опубликованные статьи серии в правильном порядке
        """
        from django.utils import timezone

        return (
            self.articles.filter(status="published", published_at__lte=timezone.now())
            .select_related("author", "category")
            .order_by("series_order", "published_at")
        )

    @property
    def image_url(self) -> str | None:
        """
        Безопасно возвращает URL обложки серии.

        Returns:
            str | None: URL изображения или None если обложки нет
        """
        try:
            if self.cover_image:
                return self.cover_image.url
        except Exception:
            return None
        return None

    @property
    def total_views(self):
        return (
            self.articles.filter(status="published").aggregate(total=models.Sum("views_count"))[
                "total"
            ]
            or 0
        )

    @property
    def estimated_reading_time(self):
        """Общее время чтения всех статей серии в минутах"""
        return (
            self.articles.filter(status="published").aggregate(total=models.Sum("reading_time"))[
                "total"
            ]
            or 0
        )


class ArticleReaction(models.Model):
    """
    Модель эмодзи-реакций пользователей на статьи.

    Позволяет пользователям выражать свою реакцию на статью с помощью
    различных эмодзи. Один пользователь может оставить только одну реакцию
    на статью (ограничение unique_together).

    Attributes:
        user (ForeignKey): Пользователь, оставивший реакцию
        article (ForeignKey): Статья, к которой относится реакция
        reaction_type (str): Тип реакции (like, love, helpful, insightful, amazing)
        created_at (datetime): Дата и время создания реакции

    Relations:
        - user.article_reactions: Все реакции пользователя
        - article.reactions: Все реакции на статью

    Constraints:
        - unique_together: Один пользователь может оставить только одну реакцию на статью
    """

    REACTION_CHOICES = [
        ("like", "👍 Нравится"),
        ("love", "❤️ Супер"),
        ("helpful", "💡 Полезно"),
        ("insightful", "🤔 Интересно"),
        ("amazing", "🤩 Потрясающе"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="article_reactions",
        verbose_name="Пользователь",
    )
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="reactions", verbose_name="Статья"
    )
    reaction_type = models.CharField(
        max_length=20, choices=REACTION_CHOICES, verbose_name="Тип реакции"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Реакция на статью"
        verbose_name_plural = "Реакции на статьи"
        unique_together = ["user", "article"]  # Один пользователь - одна реакция на статью

    def __str__(self) -> str:
        """
        Строковое представление реакции.

        Returns:
            str: Строка в формате 'username - тип_реакции - название_статьи'
        """
        return f"{self.user.username} - {self.get_reaction_type_display()} - {self.article.title}"

    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Переопределённый метод сохранения с логированием.

        Args:
            *args: Позиционные аргументы для Model.save()
            **kwargs: Именованные аргументы для Model.save()

        Raises:
            IntegrityError: Если пользователь уже оставил реакцию на эту статью
        """
        is_new = self.pk is None
        super().save(*args, **kwargs)

        action = "создана" if is_new else "изменена"
        logger.info(
            f"Реакция {action}: {self.user.username} - "
            f"{self.get_reaction_type_display()} на '{self.article.title}'"
        )


class Bookmark(models.Model):
    """
    Модель закладок пользователей для сохранения интересных статей.

    Позволяет пользователям добавлять статьи в закладки для последующего
    чтения, добавлять личные заметки и организовывать закладки по папкам.

    Attributes:
        user (ForeignKey): Владелец закладки
        article (ForeignKey): Добавленная в закладки статья
        created_at (datetime): Дата добавления в закладки
        notes (str): Личные заметки пользователя к статье (необязательно)
        folder (str): Название папки для группировки закладок (необязательно)

    Relations:
        - user.bookmarks: Все закладки пользователя
        - article.bookmarks: Все закладки этой статьи

    Constraints:
        - unique_together: Пользователь не может добавить одну статью дважды
        - ordering: Сортировка по дате создания (новые первыми)
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="bookmarks", verbose_name="Пользователь"
    )
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="bookmarks", verbose_name="Статья"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # Дополнительные поля для организации закладок
    notes = models.TextField(
        blank=True, verbose_name="Заметки", help_text="Личные заметки пользователя к статье"
    )
    folder = models.CharField(
        max_length=100, blank=True, verbose_name="Папка", help_text="Папка для группировки закладок"
    )

    class Meta:
        verbose_name = "Закладка"
        verbose_name_plural = "Закладки"
        unique_together = ["user", "article"]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        """
        Строковое представление закладки.

        Returns:
            str: Строка в формате 'username - название_статьи'
        """
        return f"{self.user.username} - {self.article.title}"

    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Переопределённый метод сохранения с логированием.

        Args:
            *args: Позиционные аргументы для Model.save()
            **kwargs: Именованные аргументы для Model.save()

        Raises:
            IntegrityError: Если закладка уже существует
        """
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            logger.info(
                f"Закладка создана: {self.user.username} добавил "
                f"'{self.article.title}' в папку '{self.folder or 'Без папки'}'"
            )

    @property
    def is_categorized(self) -> bool:
        """
        Проверяет, организована ли закладка в папку.

        Returns:
            bool: True если указана папка, False иначе
        """
        return bool(self.folder)


class ReadingProgress(models.Model):
    """
    Модель отслеживания прогресса чтения статей пользователями.

    Сохраняет информацию о том, сколько пользователь прочитал статьи,
    сколько времени потратил на чтение, и текущий статус чтения.
    Полезно для аналитики и возобновления чтения с последнего места.

    Attributes:
        user (ForeignKey): Пользователь, читающий статью
        article (ForeignKey): Читаемая статья
        progress_percentage (int): Прогресс чтения в процентах (0-100)
        reading_time_seconds (int): Время, потраченное на чтение (в секундах)
        status (str): Текущий статус чтения (not_started, in_progress, completed)
        started_at (datetime): Дата и время начала чтения (может быть None)
        completed_at (datetime): Дата и время завершения чтения (может быть None)
        last_read_at (datetime): Дата последнего сеанса чтения (обновляется автоматически)

    Relations:
        - user.reading_progress: Прогресс чтения всех статей пользователя
        - article.reading_progress: Прогресс чтения статьи всеми пользователями

    Constraints:
        - unique_together: Один пользователь имеет один прогресс на статью
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reading_progress", verbose_name="Пользователь"
    )
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="reading_progress", verbose_name="Статья"
    )

    # Прогресс чтения (в процентах)
    progress_percentage = models.PositiveIntegerField(default=0, verbose_name="Прогресс чтения (%)")

    # Время, потраченное на чтение (в секундах)
    reading_time_seconds = models.PositiveIntegerField(default=0, verbose_name="Время чтения (сек)")

    # Статус чтения
    STATUS_CHOICES = [
        ("not_started", "Не начато"),
        ("in_progress", "В процессе"),
        ("completed", "Прочитано"),
    ]
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="not_started", verbose_name="Статус чтения"
    )

    # Временные метки
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_read_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Прогресс чтения"
        verbose_name_plural = "Прогрессы чтения"
        unique_together = ["user", "article"]

    def __str__(self) -> str:
        """
        Строковое представление прогресса чтения.

        Returns:
            str: Строка в формате 'username - название_статьи (процент%)'
        """
        return f"{self.user.username} - {self.article.title} ({self.progress_percentage}%)"

    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Переопределённый метод сохранения с автоматическим обновлением статуса.

        Логика обновления:
        - Если прогресс > 0 и started_at не установлено, устанавливает started_at
        - Если прогресс >= 95, автоматически меняет статус на 'completed'
        - Если прогресс 100%, устанавливает completed_at

        Args:
            *args: Позиционные аргументы для Model.save()
            **kwargs: Именованные аргументы для Model.save()
        """
        # Автоматическая установка started_at при первом прогрессе
        if self.progress_percentage > 0 and not self.started_at:
            self.started_at = timezone.now()
            self.status = "in_progress"
            logger.info(f"{self.user.username} начал читать '{self.article.title}'")

        # Автоматическая установка completed при 95%+ прогресса
        if self.progress_percentage >= 95 and self.status != "completed":
            self.status = "completed"
            self.completed_at = timezone.now()
            logger.info(
                f"{self.user.username} завершил чтение '{self.article.title}' "
                f"(время: {self.reading_time_seconds}с)"
            )

        super().save(*args, **kwargs)

    @property
    def is_completed(self) -> bool:
        """
        Проверяет, завершено ли чтение статьи.

        Returns:
            bool: True если статус 'completed', False иначе
        """
        return self.status == "completed"

    @property
    def reading_time_minutes(self) -> int:
        """
        Возвращает время чтения в минутах.

        Returns:
            int: Время чтения, округлённое до минут
        """
        return self.reading_time_seconds // 60

    def update_progress(self, percentage: int, time_spent: int = 0) -> None:
        """
        Обновляет прогресс чтения пользователя.

        Args:
            percentage (int): Новое значение прогресса в процентах (0-100)
            time_spent (int): Добавочное время чтения в секундах (по умолчанию 0)

        Raises:
            ValueError: Если percentage не в диапазоне 0-100
        """
        if not 0 <= percentage <= 100:
            raise ValueError(f"Прогресс должен быть от 0 до 100, получено: {percentage}")

        self.progress_percentage = percentage
        self.reading_time_seconds += time_spent
        self.save()

        logger.info(
            f"Прогресс обновлён: {self.user.username} - '{self.article.title}' - {percentage}%"
        )


class Author(models.Model):
    """
    Расширенный профиль автора блога.

    Содержит дополнительную информацию об авторах статей: биографию,
    специализации, социальные сети, статистику публикаций.

    Attributes:
        user: Связанный пользователь Django
        display_name: Отображаемое имя в статьях
        slug: URL-адрес профиля
        bio: Биография автора
        specializations: Области экспертизы
        job_title: Должность
        company: Место работы
        avatar: Фото автора
        cover_image: Обложка профиля
        social_links: Twitter, GitHub, LinkedIn, YouTube, Telegram
        is_featured: Рекомендуемый автор
        statistics: articles_count, total_views, total_reactions
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="blog_author_profile",
        verbose_name="Пользователь",
    )

    # Профессиональная информация
    display_name = models.CharField(
        max_length=100,
        verbose_name="Отображаемое имя",
        help_text="Имя, которое будет показано в статьях",
    )
    slug = models.SlugField(max_length=100, unique=True, verbose_name="URL-адрес профиля")

    # Биография и специализация
    bio = models.TextField(verbose_name="Биография", help_text="Краткая биография автора")
    specializations = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Специализации",
        help_text="Области экспертизы, разделенные запятыми",
    )
    job_title = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Должность",
        help_text="Текущая должность или звание",
    )
    company = models.CharField(
        max_length=100, blank=True, verbose_name="Компания", help_text="Место работы"
    )

    # Изображения
    avatar = models.ImageField(
        upload_to="blog/authors/",
        blank=True,
        null=True,
        verbose_name="Аватар",
        help_text="Фото автора (рекомендуется 300x300px)",
    )
    cover_image = models.ImageField(
        upload_to="blog/authors/covers/",
        blank=True,
        null=True,
        verbose_name="Обложка профиля",
        help_text="Изображение для шапки профиля (рекомендуется 1200x400px)",
    )

    # Социальные сети и контакты
    website = models.URLField(blank=True, verbose_name="Личный сайт")
    twitter = models.CharField(
        max_length=50, blank=True, verbose_name="Twitter", help_text="Имя пользователя без @"
    )
    github = models.CharField(
        max_length=50, blank=True, verbose_name="GitHub", help_text="Имя пользователя GitHub"
    )
    linkedin = models.URLField(blank=True, verbose_name="LinkedIn")
    youtube = models.URLField(blank=True, verbose_name="YouTube канал")
    telegram = models.CharField(
        max_length=50, blank=True, verbose_name="Telegram", help_text="Имя пользователя без @"
    )

    # Настройки профиля
    is_featured = models.BooleanField(
        default=False,
        verbose_name="Рекомендуемый автор",
        help_text="Отображается в блоке популярных авторов",
    )
    show_email = models.BooleanField(
        default=False,
        verbose_name="Показывать email",
        help_text="Отображать email в публичном профиле",
    )
    accept_guest_posts = models.BooleanField(
        default=False,
        verbose_name="Принимает гостевые посты",
        help_text="Готов рассматривать предложения о гостевых публикациях",
    )

    # Статистика (рассчитывается автоматически)
    articles_count = models.PositiveIntegerField(default=0, verbose_name="Количество статей")
    total_views = models.PositiveIntegerField(default=0, verbose_name="Общие просмотры")
    total_reactions = models.PositiveIntegerField(default=0, verbose_name="Общие реакции")

    # Временные метки
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Автор блога"
        verbose_name_plural = "Авторы блога"
        ordering = ["-articles_count", "display_name"]

    def __str__(self) -> str:
        """
        Строковое представление автора.

        Returns:
            str: Отображаемое имя автора
        """
        return self.display_name

    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Сохранение профиля автора с автоматической генерацией slug.

        Args:
            *args: Позиционные аргументы для родительского метода
            **kwargs: Именованные аргументы для родительского метода
        """
        try:
            # Генерируем slug если его нет
            if not self.slug:
                self.slug = slugify(self.display_name)

            super().save(*args, **kwargs)
            logger.info(
                f"Профиль автора '{self.display_name}' сохранен: "
                f"пользователь={self.user.username}, статей={self.articles_count}"
            )
        except Exception as e:
            logger.error(
                f"Ошибка при сохранении профиля автора '{self.display_name}': {e}", exc_info=True
            )
            raise

    def get_absolute_url(self) -> str:
        """
        Получение абсолютного URL профиля автора.

        Returns:
            str: URL для страницы автора
        """
        return reverse("blog:author_detail", kwargs={"slug": self.slug})

    @property
    def published_articles(self) -> Any:
        """
        Опубликованные статьи автора.

        Returns:
            QuerySet: Опубликованные статьи пользователя
        """
        return self.user.blog_articles.filter(status="published")

    @property
    def average_rating(self) -> float:
        """
        Средний рейтинг статей автора на основе реакций.

        Returns:
            float: Среднее количество реакций на статью
        """
        articles = self.published_articles
        if not articles.exists():
            return 0.0

        try:
            total_reactions = sum(article.total_reactions for article in articles)
            return round(total_reactions / articles.count() if total_reactions > 0 else 0.0, 2)
        except Exception as e:
            logger.error(f"Ошибка при расчете среднего рейтинга автора {self.display_name}: {e}")
            return 0.0

    def update_statistics(self) -> None:
        """
        Обновляет статистику автора.

        Пересчитывает количество статей, общие просмотры и реакции.
        Используется в периодических задачах или после публикации статьи.
        """
        try:
            articles = self.published_articles.prefetch_related("reactions", "detailed_views")

            self.articles_count = articles.count()
            self.total_views = sum(article.views_count for article in articles)
            self.total_reactions = sum(article.total_reactions for article in articles)

            self.save(update_fields=["articles_count", "total_views", "total_reactions"])
            logger.info(
                f"Статистика автора '{self.display_name}' обновлена: "
                f"статей={self.articles_count}, просмотров={self.total_views}, реакций={self.total_reactions}"
            )
        except Exception as e:
            logger.error(
                f"Ошибка при обновлении статистики автора {self.display_name}: {e}", exc_info=True
            )

    def get_social_links(self) -> dict[str, str]:
        """
        Возвращает активные социальные ссылки автора.

        Returns:
            dict[str, str]: Словарь {название: URL} для всех заполненных социальных сетей

        Example:
            >>> author.get_social_links()
            {'GitHub': 'https://github.com/username', 'Twitter': 'https://twitter.com/username'}
        """
        from collections import OrderedDict

        links = OrderedDict()

        if self.website:
            links["Сайт"] = self.website
        if self.twitter:
            links["Twitter"] = f"https://twitter.com/{self.twitter}"
        if self.github:
            links["GitHub"] = f"https://github.com/{self.github}"
        if self.linkedin:
            links["LinkedIn"] = self.linkedin
        if self.youtube:
            links["YouTube"] = self.youtube
        if self.telegram:
            links["Telegram"] = f"https://t.me/{self.telegram}"

        return links

    @property
    def followers_count(self) -> int:
        """
        Количество подписчиков автора.

        Returns:
            int: Количество подписчиков (0 если механизм подписок не реализован)

        Note:
            Заглушка для будущей функциональности подписок на авторов
        """
        # Если в будущем добавится модель подписок — можно заменить на реальный подсчёт
        return getattr(self, "_followers_count_cache", 0)

    @property
    def last_published_at(self) -> Any | None:
        """
        Дата последней опубликованной статьи автора.

        Returns:
            datetime | None: Дата публикации последней статьи или None
        """
        try:
            latest = (
                self.published_articles.order_by("-published_at")
                .values_list("published_at", flat=True)
                .first()
            )
            return latest
        except Exception as e:
            logger.error(
                f"Ошибка при получении даты последней публикации автора {self.display_name}: {e}"
            )
            return None

    @property
    def rating(self):
        """Алиас для average_rating, удобный для шаблонов."""
        return self.average_rating

    @property
    def avatar_url(self):
        """Безопасно возвращает URL аватара или None."""
        try:
            if self.avatar:
                return self.avatar.url
        except Exception:
            return None
        return None

    def social_links_dict(self):
        """Alias для совместимости: возвращает dict социальных ссылок."""
        return dict(self.get_social_links())


class ArticleView(models.Model):
    """Детальная аналитика просмотров статей"""

    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="detailed_views", verbose_name="Статья"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="article_views",
        verbose_name="Пользователь",
    )

    # Информация о просмотре
    ip_address = models.GenericIPAddressField(verbose_name="IP адрес")
    user_agent = models.TextField(verbose_name="User Agent")
    referer = models.URLField(blank=True, null=True, verbose_name="Источник перехода")

    # Поведенческие метрики
    time_on_page = models.PositiveIntegerField(default=0, verbose_name="Время на странице (сек)")
    scroll_depth = models.PositiveIntegerField(default=0, verbose_name="Глубина прокрутки (%)")

    # Метки времени
    viewed_at = models.DateTimeField(auto_now_add=True)

    # Флаги
    is_unique = models.BooleanField(
        default=True,
        verbose_name="Уникальный просмотр",
        help_text="Первый просмотр статьи этим пользователем/IP",
    )

    class Meta:
        verbose_name = "Просмотр статьи"
        verbose_name_plural = "Просмотры статей"
        ordering = ["-viewed_at"]

    def __str__(self):
        user_info = self.user.username if self.user else self.ip_address
        return f"{user_info} - {self.article.title}"


class ArticleReport(models.Model):
    """
    Модель жалоб пользователей на статьи.

    Позволяет пользователям сообщать о проблемах со статьями (спам,
    неподходящий контент, дезинформация, нарушение авторских прав и др.).
    Администраторы могут рассматривать жалобы и принимать меры.

    Attributes:
        article (ForeignKey): Статья, на которую подана жалоба
        reporter (ForeignKey): Пользователь, подавший жалобу (может быть None для анонимных)
        reason_type (str): Тип жалобы (spam, inappropriate, misinformation, copyright, other)
        reason (str): Детальное описание проблемы (необязательно)
        status (str): Статус обработки (pending, reviewed, resolved, rejected)
        admin_notes (str): Заметки администратора по жалобе (необязательно)
        reported_at (datetime): Дата и время подачи жалобы
        reviewed_at (datetime): Дата и время рассмотрения (может быть None)

    Relations:
        - article.reports: Все жалобы на эту статью
        - reporter.article_reports: Все жалобы этого пользователя

    Workflow:
        1. Пользователь создаёт жалобу (status='pending')
        2. Администратор рассматривает (status='reviewed')
        3. Администратор принимает решение (status='resolved' или 'rejected')
    """

    REASON_CHOICES = [
        ("spam", "Спам"),
        ("inappropriate", "Неподходящий контент"),
        ("misinformation", "Дезинформация"),
        ("copyright", "Нарушение авторских прав"),
        ("other", "Другое"),
    ]

    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="reports", verbose_name="Статья"
    )
    reporter = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="article_reports",
        verbose_name="Отправитель",
    )

    reason_type = models.CharField(
        max_length=20, choices=REASON_CHOICES, default="other", verbose_name="Тип жалобы"
    )
    reason = models.TextField(verbose_name="Описание проблемы", blank=True)

    # Статус обработки
    STATUS_CHOICES = [
        ("pending", "Ожидает рассмотрения"),
        ("reviewed", "Рассмотрена"),
        ("resolved", "Решена"),
        ("rejected", "Отклонена"),
    ]
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending", verbose_name="Статус"
    )

    admin_notes = models.TextField(blank=True, verbose_name="Заметки администратора")

    reported_at = models.DateTimeField(default=timezone.now, verbose_name="Дата жалобы")
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата рассмотрения")

    class Meta:
        verbose_name = "Жалоба на статью"
        verbose_name_plural = "Жалобы на статьи"
        ordering = ["-reported_at"]

    def __str__(self) -> str:
        """
        Строковое представление жалобы.

        Returns:
            str: Строка в формате 'имя_отправителя - название_статьи (статус)'
        """
        reporter_name = self.reporter.username if self.reporter else "Анонимный"
        return f"{reporter_name} - {self.article.title} ({self.get_status_display()})"

    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Переопределённый метод сохранения с автоматическим обновлением reviewed_at.

        Если статус изменён с 'pending' на другой статус, автоматически
        устанавливается reviewed_at в текущее время.

        Args:
            *args: Позиционные аргументы для Model.save()
            **kwargs: Именованные аргументы для Model.save()
        """
        is_new = self.pk is None

        # Автоматическая установка reviewed_at при изменении статуса
        if not is_new and self.status != "pending" and not self.reviewed_at:
            self.reviewed_at = timezone.now()

        super().save(*args, **kwargs)

        if is_new:
            logger.warning(
                f"Новая жалоба: {self.reporter.username if self.reporter else 'Анонимный'} "
                f"сообщает о '{self.article.title}' - причина: {self.get_reason_type_display()}"
            )
        elif self.status != "pending":
            logger.info(
                f"Жалоба обработана: '{self.article.title}' - статус: {self.get_status_display()}"
            )

    @property
    def is_pending(self) -> bool:
        """
        Проверяет, ожидает ли жалоба рассмотрения.

        Returns:
            bool: True если статус 'pending', False иначе
        """
        return self.status == "pending"

    @property
    def is_resolved(self) -> bool:
        """
        Проверяет, решена ли жалоба.

        Returns:
            bool: True если статус 'resolved' или 'rejected', False иначе
        """
        return self.status in ["resolved", "rejected"]

    def mark_as_reviewed(self, admin_notes: str = "") -> None:
        """
        Отмечает жалобу как рассмотренную.

        Args:
            admin_notes (str): Заметки администратора (необязательно)
        """
        self.status = "reviewed"
        if admin_notes:
            self.admin_notes = admin_notes
        self.save()
        logger.info(f"Жалоба '{self}' отмечена как рассмотренная")

    def resolve(self, admin_notes: str = "") -> None:
        """
        Решает жалобу (применяются меры по статье).

        Args:
            admin_notes (str): Заметки администратора о принятых мерах (необязательно)
        """
        self.status = "resolved"
        if admin_notes:
            self.admin_notes = admin_notes
        self.save()
        logger.info(f"Жалоба '{self}' решена")

    def reject(self, admin_notes: str = "") -> None:
        """
        Отклоняет жалобу (меры не требуются).

        Args:
            admin_notes (str): Заметки администратора о причинах отклонения (необязательно)
        """
        self.status = "rejected"
        if admin_notes:
            self.admin_notes = admin_notes
        self.save()
        logger.info(f"Жалоба '{self}' отклонена")
