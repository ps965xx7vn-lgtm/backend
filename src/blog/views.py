from __future__ import annotations

import logging
from typing import Any

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.core.mail import mail_admins, send_mail
from django.core.paginator import Paginator
from django.db.models import Count, F, Max, Q, Sum, Value
from django.http import Http404, JsonResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.views.generic import DetailView, ListView, TemplateView, View
from taggit.models import Tag

from .cache_utils import cache_article_list, cache_category_list, cache_page_data, cache_stats
from .forms import CommentForm
from .models import Article, ArticleReaction, Author, Category, Comment, Newsletter, Series

logger = logging.getLogger(__name__)

# Вспомогательные функции с кешированием


@cache_article_list(timeout=300)
def get_featured_articles():
    """Получает рекомендуемые статьи с кешированием (5 минут)."""
    try:
        return list(
            Article.objects.filter(
                status="published",
                is_featured=True,
                published_at__lte=timezone.now(),
            )
            .select_related("category", "blog_author", "author")
            .prefetch_related("tags")[:6]
        )
    except Exception as e:
        logger.error(f"Ошибка получения рекомендуемых статей: {e}")
        return []


@cache_article_list(timeout=300)
def get_latest_articles(exclude_featured=False):
    """Получает последние статьи с кешированием (5 минут)."""
    try:
        queryset = (
            Article.objects.filter(status="published", published_at__lte=timezone.now())
            .select_related("category", "blog_author", "author")
            .prefetch_related("tags")
        )

        if exclude_featured:
            queryset = queryset.exclude(is_featured=True)

        return list(queryset[:12])
    except Exception as e:
        logger.error(f"Ошибка получения последних статей: {e}")
        return []


@cache_category_list(timeout=1800)
def get_popular_categories():
    """Получает популярные категории с кешированием (30 минут)."""
    try:
        return list(
            Category.objects.annotate(
                published_count=Count("articles", filter=Q(articles__status="published"))
            )
            .filter(published_count__gt=0)
            .order_by("-published_count")[:8]
        )
    except Exception as e:
        logger.error(f"Ошибка получения категорий: {e}")
        return []


@cache_page_data(timeout=1800, key_prefix="popular_tags")
def get_popular_tags():
    """Получает популярные теги с кешированием (30 минут)."""
    try:
        return list(
            Tag.objects.annotate(
                num_articles=Count(
                    "taggit_taggeditem_items",
                    filter=Q(taggit_taggeditem_items__content_type__model="article"),
                )
            )
            .filter(num_articles__gt=0)
            .order_by("-num_articles")[:20]
        )
    except Exception as e:
        logger.error(f"Ошибка получения тегов: {e}")
        return []


@cache_stats(timeout=600)
def get_blog_stats():
    """Получает статистику блога с кешированием (10 минут)."""
    try:
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
        logger.error(f"Ошибка получения статистики: {e}")
        return {
            "total_articles": 0,
            "total_categories": 0,
            "total_comments": 0,
            "total_authors": 0,
        }


class BlogHomeView(TemplateView):
    """
    Главная страница блога с рекомендуемыми статьями.

    Отображает:
    - Рекомендуемые статьи (is_featured=True)
    - Последние опубликованные статьи
    - Популярные категории с количеством статей
    - Популярные теги
    - Общую статистику блога
    """

    template_name = "blog/home.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """
        Формирование контекста для главной страницы блога.

        Оптимизирует запросы к БД используя select_related и prefetch_related
        для минимизации количества SQL запросов.

        Args:
            **kwargs: Дополнительные параметры контекста

        Returns:
            dict[str, Any]: Контекст с данными для шаблона:
                - featured_articles: Рекомендуемые статьи (до 6)
                - latest_articles: Последние статьи (до 12)
                - popular_categories: Популярные категории (до 8)
                - popular_tags: Популярные теги (до 20)
                - stats: Статистика блога
                - page_title: Заголовок страницы
                - meta_description: Мета-описание для SEO
        """
        try:
            context = super().get_context_data(**kwargs)

            # Рекомендуемые статьи с кешированием (5 минут)
            featured_articles = get_featured_articles()

            # Последние статьи с кешированием (5 минут)
            latest_articles = get_latest_articles(exclude_featured=True)

            # Популярные категории с кешированием (30 минут)
            popular_categories = get_popular_categories()

            # Популярные теги с кешированием (30 минут)
            popular_tags = get_popular_tags()

            # Статистика блога с кешированием (10 минут)
            stats = get_blog_stats()

            # Добавляем подписчиков (не кешируется - часто меняется)
            try:
                stats["total_subscribers"] = Newsletter.objects.filter(is_active=True).count()
            except Exception as e:
                logger.error(f"Ошибка подсчета подписчиков: {e}")
                stats["total_subscribers"] = 0

            context.update(
                {
                    "featured_articles": featured_articles,
                    "latest_articles": latest_articles,
                    "popular_categories": popular_categories,
                    "popular_tags": popular_tags,
                    "stats": stats,
                    "page_title": "Блог PyLand - Изучай программирование",
                    "meta_description": "Образовательный блог PyLand: статьи о программировании, уроки Python, Django, JavaScript, React и многое другое.",
                }
            )

            logger.info("Главная страница блога успешно загружена")
            return context

        except Exception as e:
            logger.error(f"Ошибка при загрузке главной страницы блога: {e}", exc_info=True)
            # Возвращаем базовый контекст с пустыми данными
            return super().get_context_data(**kwargs)


class ToggleBookmarkView(View):
    """
    AJAX view для добавления/удаления статьи из закладок.

    Требует аутентификации пользователя.
    Переключает состояние закладки для указанной статьи.
    """

    def post(self, request: Any, *args: Any, **kwargs: Any) -> JsonResponse:
        """
        Обработка POST запроса для переключения закладки.

        Args:
            request: HTTP запрос с article_id в POST данных
            *args: Дополнительные позиционные аргументы
            **kwargs: Дополнительные именованные аргументы

        Returns:
            JsonResponse: JSON с результатом операции
            - {'bookmarked': True} если закладка добавлена
            - {'bookmarked': False} если закладка удалена
            - {'error': 'message'} при ошибке
        """
        try:
            # Проверка аутентификации
            if not request.user.is_authenticated:
                logger.warning("Попытка добавления закладки неаутентифицированным пользователем")
                return JsonResponse(
                    {"error": "Необходима авторизация для добавления в закладки"},
                    status=403,
                )

            # Получение ID статьи
            article_id = request.POST.get("article_id") or request.POST.get("id")
            if not article_id:
                logger.warning("Запрос на добавление закладки без article_id")
                return JsonResponse({"error": "Не указан ID статьи"}, status=400)

            # Поиск статьи
            try:
                article = Article.objects.get(pk=article_id, status="published")
            except Article.DoesNotExist:
                logger.warning(
                    f"Попытка добавить в закладки несуществующую статью ID: {article_id}"
                )
                return JsonResponse({"error": "Статья не найдена"}, status=404)

            # Переключение закладки
            from .models import Bookmark

            bookmark, created = Bookmark.objects.get_or_create(user=request.user, article=article)

            if not created:
                # Закладка уже существует - удаляем
                bookmark.delete()
                logger.info(
                    f"Пользователь {request.user.username} удалил из закладок статью '{article.title}'"
                )
                return JsonResponse({"bookmarked": False})

            logger.info(
                f"Пользователь {request.user.username} добавил в закладки статью '{article.title}'"
            )
            return JsonResponse({"bookmarked": True})

        except Exception as e:
            logger.error(f"Ошибка при переключении закладки: {e}", exc_info=True)
            return JsonResponse({"error": "Произошла ошибка при обработке запроса"}, status=500)


class ReportArticleView(View):
    """
    AJAX endpoint для отправки жалобы на статью.

    Сохраняет жалобу в базу данных и отправляет уведомление администраторам.
    Поддерживает как аутентифицированных, так и анонимных пользователей.
    """

    def post(self, request: Any, *args: Any, **kwargs: Any) -> JsonResponse:
        """
        Обработка POST запроса для отправки жалобы на статью.

        Args:
            request: HTTP запрос с article_id и reason в POST данных
            *args: Дополнительные позиционные аргументы
            **kwargs: Дополнительные именованные аргументы

        Returns:
            JsonResponse: JSON с результатом операции
            - {'reported': True, 'report_id': id} при успехе
            - {'error': 'message'} при ошибке
        """
        try:
            # Получение и валидация данных
            article_id = request.POST.get("article_id") or request.POST.get("id")
            reason = request.POST.get("reason", "").strip()

            if not article_id:
                logger.warning("Попытка отправить жалобу без article_id")
                return JsonResponse({"error": "Не указан ID статьи"}, status=400)

            if not reason:
                logger.warning(
                    f"Попытка отправить жалобу на статью {article_id} без указания причины"
                )
                return JsonResponse({"error": "Необходимо указать причину жалобы"}, status=400)

            # Поиск статьи
            try:
                article = Article.objects.select_related("author", "blog_author").get(pk=article_id)
            except Article.DoesNotExist:
                logger.warning(
                    f"Попытка отправить жалобу на несуществующую статью ID: {article_id}"
                )
                return JsonResponse({"error": "Статья не найдена"}, status=404)

            # Сохранение жалобы в базу данных
            from .models import ArticleReport

            report = ArticleReport.objects.create(
                article=article,
                reporter=request.user if request.user.is_authenticated else None,
                reason=reason,
                reason_type="other",
            )

            reporter_name = (
                request.user.username if request.user.is_authenticated else "Анонимный пользователь"
            )
            logger.info(
                f"Получена жалоба на статью '{article.title}' от {reporter_name}. Причина: {reason[:50]}..."
            )

            # Отправка email администраторам
            try:
                subject = f"🚨 Новая жалоба на статью: {article.title}"
                site_url = request.build_absolute_uri("/")
                article_url = request.build_absolute_uri(article.get_absolute_url())

                body = f"""
Получена новая жалоба на статью в блоге.

Отправитель: {reporter_name}
ID статьи: {article.id}
Название статьи: {article.title}
Ссылка на статью: {article_url}

Причина жалобы:
{reason}

---
Статус статьи: {article.get_status_display()}
Автор статьи: {article.get_author_display_name()}
Дата публикации: {article.published_at.strftime("%d.%m.%Y %H:%M") if article.published_at else "Не опубликовано"}

Для модерации перейдите в админ-панель:
{site_url}admin/blog/articlereport/{report.id}/change/
                """.strip()

                mail_admins(subject, body, fail_silently=False)
                logger.info(
                    f"Email с жалобой на статью '{article.title}' отправлен администраторам"
                )
            except Exception as email_error:
                # Не прерываем выполнение, если не удалось отправить email
                logger.error(f"Ошибка при отправке email с жалобой: {email_error}", exc_info=True)

            return JsonResponse(
                {
                    "reported": True,
                    "report_id": report.id,
                    "message": "Ваша жалоба успешно отправлена. Спасибо за помощь в улучшении качества контента!",
                }
            )

        except Exception as e:
            logger.error(f"Ошибка при обработке жалобы на статью: {e}", exc_info=True)
            return JsonResponse(
                {"error": "Произошла ошибка при отправке жалобы. Пожалуйста, попробуйте позже."},
                status=500,
            )


class ArticleDetailView(DetailView):
    """
    Детальная страница статьи с полным функционалом.

    Самый сложный view в блоге, обрабатывающий:
    - Отображение статьи с метаданными и SEO
    - Автоматическое увеличение счётчика просмотров
    - Отслеживание прогресса чтения (для аутентифицированных)
    - Отображение и добавление комментариев (GET/POST)
    - Вложенные ответы на комментарии
    - Похожие статьи (по категории и тегам)
    - Навигацию по предыдущей/следующей статье
    - Навигацию по серии статей (если статья входит в серию)
    - Пагинацию комментариев (10 на страницу)

    Attributes:
        model (Model): Article
        template_name (str): 'blog/article_detail.html'
        context_object_name (str): 'article'
        slug_field (str): 'slug'
        slug_url_kwarg (str): 'slug'

    Methods:
        get_queryset(): Оптимизированный queryset с select_related/prefetch_related
        get_object(): Увеличение просмотров и отслеживание прогресса
        post(): Обработка добавления комментариев и ответов
        get_context_data(): Формирование полного контекста страницы

    Context Variables:
        - article: Текущая статья
        - similar_articles: До 6 похожих статей
        - comments: Пагинированный список одобренных комментариев
        - comment_form: Форма для добавления комментария
        - comments_count: Общее количество комментариев
        - prev_article/next_article: Навигация по хронологии
        - current_series: Серия, к которой принадлежит статья
        - series_prev_article/series_next_article: Навигация по серии
        - series_count: Количество статей в серии
        - page_title, meta_description, meta_keywords: SEO метаданные
    """

    model = Article
    template_name = "blog/article_detail.html"
    context_object_name = "article"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self) -> Any:
        """
        Возвращает оптимизированный queryset опубликованных статей.

        Использует select_related и prefetch_related для уменьшения
        количества SQL-запросов при загрузке связанных объектов.

        Returns:
            QuerySet: Опубликованные статьи с предзагруженными связями
        """
        return (
            Article.objects.filter(status="published", published_at__lte=timezone.now())
            .select_related("category", "blog_author", "author")
            .prefetch_related("tags", "comments")
        )

    def get_object(self, queryset: Any = None) -> Article:
        """
        Получает статью и выполняет дополнительные операции.

        Выполняет:
        1. Увеличение счётчика просмотров (атомарная операция)
        2. Отслеживание прогресса чтения для аутентифицированных пользователей
        3. Автоматическое обновление прогресса при каждом просмотре

        Args:
            queryset: Опциональный queryset для получения объекта

        Returns:
            Article: Запрошенная статья с обновлённым счётчиком просмотров

        Side Effects:
            - Увеличивает views_count на 1
            - Создаёт или обновляет ReadingProgress для авторизованных пользователей
            - Логирует просмотр статьи
        """
        try:
            article = super().get_object(queryset)

            # Атомарное увеличение счётчика просмотров
            Article.objects.filter(pk=article.pk).update(views_count=F("views_count") + 1)
            article.refresh_from_db()

            logger.info(
                f"Просмотр статьи: '{article.title}' (ID={article.id}), "
                f"пользователь: {self.request.user.username if self.request.user.is_authenticated else 'anonymous'}"
            )

            # Отслеживание прогресса чтения для аутентифицированных пользователей
            if self.request.user.is_authenticated:
                try:
                    from .models import ReadingProgress

                    progress, created = ReadingProgress.objects.get_or_create(
                        user=self.request.user,
                        article=article,
                        defaults={
                            "status": "in_progress",
                            "progress_percentage": 50,
                            "started_at": timezone.now(),
                        },
                    )

                    if created:
                        logger.info(f"Создан прогресс чтения для {self.request.user.username}")
                    else:
                        # Обновляем прогресс только если статья не завершена
                        if progress.status != "completed":
                            progress.last_read_at = timezone.now()

                            if progress.status == "not_started":
                                progress.status = "in_progress"
                                progress.started_at = timezone.now()

                            # Постепенное увеличение прогресса (до 90%, финал 100% - по кнопке)
                            if progress.progress_percentage < 90:
                                progress.progress_percentage = min(
                                    90, progress.progress_percentage + 10
                                )

                            progress.save()

                except Exception as e:
                    # Не прерываем отображение статьи из-за ошибки прогресса
                    logger.error(f"Ошибка обновления прогресса чтения: {e}", exc_info=True)

            return article

        except Article.DoesNotExist:
            logger.warning(f"Попытка доступа к несуществующей статье: {self.kwargs.get('slug')}")
            raise
        except Exception as e:
            logger.error(f"Ошибка в get_object ArticleDetailView: {e}", exc_info=True)
            raise

    def post(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        """
        Обрабатывает POST-запросы для добавления комментариев или ответов.

        Валидация:
        1. Проверка аутентификации пользователя
        2. Проверка разрешения комментариев на статье
        3. Валидация формы CommentForm
        4. Проверка существования родительского комментария (для ответов)

        Args:
            request: HTTP-запрос с POST данными:
                - content: Текст комментария (обязательно)
                - parent_id: ID родительского комментария (опционально)
            *args: Позиционные аргументы
            **kwargs: Именованные аргументы (содержит slug статьи)

        Returns:
            HttpResponse: Редирект на статью с якорем на новый комментарий
                         или обратно на статью с сообщением об ошибке

        Side Effects:
            - Создаёт новый Comment в базе данных
            - Добавляет success/error сообщение в messages
            - Логирует действия пользователя
        """
        try:
            self.object = self.get_object()
            article = self.object

            # Проверка аутентификации
            if not request.user.is_authenticated:
                logger.warning(
                    f"Попытка добавить комментарий без аутентификации к статье '{article.slug}'"
                )
                messages.error(request, "Для добавления комментария необходимо войти в систему.")
                return redirect(article.get_absolute_url())

            # Проверка разрешения комментариев
            if not article.allow_comments:
                logger.warning(
                    f"Попытка добавить комментарий к статье '{article.slug}' "
                    f"с отключенными комментариями пользователем {request.user.username}"
                )
                messages.error(request, "Комментарии к этой статье отключены.")
                return redirect(article.get_absolute_url())

            # Валидация формы
            form = CommentForm(request.POST)

            if form.is_valid():
                comment = form.save(commit=False)
                comment.article = article
                comment.author = request.user

                # Обработка родительского комментария для ответов
                parent_id = request.POST.get("parent_id") or form.cleaned_data.get("parent_id")

                if parent_id:
                    try:
                        parent_comment = Comment.objects.get(id=parent_id, article=article)
                        # Проверка глубины вложенности
                        if parent_comment.get_depth() >= 2:
                            logger.warning(
                                f"Попытка создать комментарий глубже 3 уровня: "
                                f"пользователем {request.user.username}"
                            )
                            messages.error(
                                request, "Достигнута максимальная глубина вложенности комментариев."
                            )
                            return redirect(article.get_absolute_url())

                        comment.parent = parent_comment
                        logger.info(
                            f"Ответ на комментарий: {request.user.username} → "
                            f"комментарий ID={parent_id} (глубина={parent_comment.get_depth()}) на '{article.slug}'"
                        )
                        messages.success(request, "Ответ успешно добавлен!")
                    except Comment.DoesNotExist:
                        logger.error(
                            f"Попытка ответить на несуществующий комментарий ID={parent_id} "
                            f"пользователем {request.user.username}"
                        )
                        messages.error(request, "Родительский комментарий не найден.")
                        return redirect(article.get_absolute_url())
                    except ValueError as e:
                        logger.error(f"Некорректное значение parent_id={parent_id}: {e}")
                        messages.error(request, "Некорректный ID родительского комментария.")
                        return redirect(article.get_absolute_url())
                else:
                    logger.info(f"Новый комментарий: {request.user.username} к '{article.slug}'")
                    messages.success(request, "Комментарий успешно добавлен!")

                comment.save()
                logger.info(f"Комментарий ID={comment.id} успешно сохранен")

                # Перенаправление с якорем на добавленный комментарий
                redirect_url = article.get_absolute_url() + f"#comment-{comment.id}"
                return redirect(redirect_url)
            else:
                # Логирование ошибок валидации
                logger.warning(
                    f"Ошибка валидации комментария от {request.user.username}: {form.errors}"
                )
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, error)
                # Редирект к секции комментариев с якорем
                return redirect(article.get_absolute_url() + "#comments")

        except Exception as e:
            logger.error(
                f"Ошибка при добавлении комментария пользователем "
                f"{request.user.username if request.user.is_authenticated else 'anonymous'}: {e}",
                exc_info=True,
            )
            messages.error(
                request,
                "Произошла ошибка при добавлении комментария. Попробуйте позже.",
            )
            # Возвращаемся на статью или на главную страницу блога
            try:
                article = self.get_object()
                return redirect(article.get_absolute_url())
            except Exception:
                return redirect("blog:home")

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """
        Формирует контекст шаблона со всеми необходимыми данными.

        Добавляет в контекст:
        - Похожие статьи (по категории и тегам)
        - Пагинированные комментарии (только одобренные, без родителей)
        - Форму для добавления комментария
        - Навигацию по предыдущей/следующей статье
        - Навигацию по серии (если статья входит в серию)
        - SEO метаданные

        Args:
            **kwargs: Аргументы контекста от родительского класса

        Returns:
            dict[str, Any]: Полный контекст для рендеринга шаблона со всеми данными

        Context Keys:
            similar_articles: QuerySet из до 6 похожих статей
            comments: Paginator.Page с одобренными комментариями
            comment_form: Экземпляр CommentForm
            comments_count: int общего количества комментариев
            prev_article/next_article: Article или None
            current_series: Series или None
            series_prev_article/series_next_article: Article или None
            series_count: int количества статей в серии
            page_title, meta_description, meta_keywords: str для SEO
        """
        try:
            context = super().get_context_data(**kwargs)
            article = self.object

            # === Похожие статьи ===
            try:
                # Сначала ищем по категории или тегам
                similar_articles = (
                    Article.objects.filter(status="published", published_at__lte=timezone.now())
                    .filter(Q(category=article.category) | Q(tags__in=article.tags.all()))
                    .exclude(pk=article.pk)
                    .distinct()
                    .select_related("category", "blog_author", "author")
                    .prefetch_related("tags")[:6]
                )

                # Если похожих нет, берём последние опубликованные
                if not similar_articles.exists():
                    similar_articles = (
                        Article.objects.filter(status="published", published_at__lte=timezone.now())
                        .exclude(pk=article.pk)
                        .select_related("category", "blog_author", "author")
                        .prefetch_related("tags")
                        .order_by("-published_at")[:6]
                    )

            except Exception as e:
                logger.error(f"Ошибка загрузки похожих статей: {e}")
                similar_articles = Article.objects.none()

            # === Комментарии ===
            try:
                # Только одобренные корневые комментарии (без родителя)
                all_comments = (
                    article.comments.filter(is_approved=True, parent__isnull=True)
                    .select_related("author")
                    .prefetch_related("replies")
                    .order_by("-created_at")
                )

                # Пагинация
                comments_per_page = 10
                page = self.request.GET.get("page", 1)
                paginator = Paginator(all_comments, comments_per_page)

                try:
                    comments = paginator.page(page)
                except Exception:
                    logger.warning(f"Некорректная страница комментариев: {page}")
                    comments = paginator.page(1)

                comments_count = all_comments.count()

            except Exception as e:
                logger.error(f"Ошибка загрузки комментариев: {e}")
                comments = []
                comments_count = 0

            # Форма для комментариев
            comment_form = CommentForm()

            # === Навигация: предыдущая/следующая статья ===
            try:
                prev_article = (
                    Article.objects.filter(
                        status="published", published_at__lt=article.published_at
                    )
                    .order_by("-published_at")
                    .first()
                )

                next_article = (
                    Article.objects.filter(
                        status="published", published_at__gt=article.published_at
                    )
                    .order_by("published_at")
                    .first()
                )

            except Exception as e:
                logger.error(f"Ошибка загрузки навигации статей: {e}")
                prev_article = None
                next_article = None

            # === Навигация по серии ===
            series_prev_article = None
            series_next_article = None
            current_series = None
            series_count = 0

            try:
                if hasattr(article, "series") and article.series:
                    current_series = article.series
                    series_articles = article.series.articles.filter(
                        status="published", published_at__lte=timezone.now()
                    ).order_by("series_order", "published_at")

                    # Находим позицию текущей статьи в серии
                    series_articles_list = list(series_articles)
                    series_count = len(series_articles_list)

                    try:
                        current_index = series_articles_list.index(article)

                        if current_index > 0:
                            series_prev_article = series_articles_list[current_index - 1]

                        if current_index < len(series_articles_list) - 1:
                            series_next_article = series_articles_list[current_index + 1]

                    except (ValueError, IndexError) as e:
                        logger.warning(f"Ошибка определения позиции в серии: {e}")

            except Exception as e:
                logger.error(f"Ошибка загрузки навигации по серии: {e}")

            # === Обновление контекста ===
            context.update(
                {
                    "similar_articles": similar_articles,
                    "comments": comments,
                    "comment_form": comment_form,
                    "comments_count": comments_count,
                    "prev_article": prev_article,
                    "next_article": next_article,
                    "current_series": current_series,
                    "series_prev_article": series_prev_article,
                    "series_next_article": series_next_article,
                    "series_count": series_count,
                    "page_title": article.title,
                    "meta_description": (
                        article.meta_description or article.excerpt[:160] if article.excerpt else ""
                    ),
                    "meta_keywords": article.meta_keywords,
                }
            )

            return context

        except Exception as e:
            logger.error(f"Критическая ошибка в get_context_data: {e}", exc_info=True)
            # Возвращаем минимальный контекст для избежания полного краха
            return super().get_context_data(**kwargs)


class ArticleListView(ListView):
    """
    Список всех опубликованных статей с фильтрацией и сортировкой.

    Поддерживает фильтрацию по:
    - Категории (GET параметр 'category')
    - Уровню сложности (GET параметр 'difficulty')
    - Тегу (GET параметр 'tag')

    Поддерживает сортировку по:
    - Дате публикации (по умолчанию)
    - Количеству просмотров
    - Алфавиту заголовка
    """

    model = Article
    template_name = "blog/article_list.html"
    context_object_name = "articles"
    paginate_by = 12

    def get_queryset(self) -> Any:
        """
        Получение отфильтрованного и отсортированного queryset статей.

        Применяет оптимизацию запросов через select_related и prefetch_related
        для минимизации количества SQL запросов.

        Returns:
            QuerySet: Отфильтрованный набор опубликованных статей
        """
        try:
            queryset = (
                Article.objects.filter(status="published", published_at__lte=timezone.now())
                .select_related("category", "blog_author", "author")
                .prefetch_related("tags")
            )

            # Фильтрация по категории
            category_slug = self.request.GET.get("category")
            if category_slug:
                queryset = queryset.filter(category__slug=category_slug)
                logger.info(f"Фильтрация статей по категории: {category_slug}")

            # Фильтрация по сложности
            difficulty = self.request.GET.get("difficulty")
            if difficulty and difficulty in dict(Article.DIFFICULTY_CHOICES):
                queryset = queryset.filter(difficulty=difficulty)
                logger.info(f"Фильтрация статей по сложности: {difficulty}")

            # Фильтрация по тегу (distinct для избежания дубликатов из M2M)
            tag_slug = self.request.GET.get("tag")
            if tag_slug:
                queryset = queryset.filter(tags__slug=tag_slug).distinct()
                logger.info(f"Фильтрация статей по тегу: {tag_slug}")

            # Сортировка с валидацией
            sort_by = self.request.GET.get("sort", "-published_at")
            valid_sorts = [
                "-published_at",
                "published_at",
                "-views_count",
                "views_count",
                "title",
                "-title",
            ]
            if sort_by in valid_sorts:
                queryset = queryset.order_by(sort_by)
            else:
                logger.warning(f"Недопустимый параметр сортировки: {sort_by}")
                queryset = queryset.order_by("-published_at")

            return queryset

        except Exception as e:
            logger.error(f"Ошибка при получении списка статей: {e}", exc_info=True)
            return Article.objects.none()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """
        Формирование контекста для страницы списка статей.

        Args:
            **kwargs: Дополнительные параметры контекста

        Returns:
            dict[str, Any]: Контекст с данными для шаблона:
                - categories: Категории с количеством статей
                - popular_tags: Популярные теги
                - current_*: Текущие фильтры
                - page_title, meta_description: SEO данные
        """
        try:
            context = super().get_context_data(**kwargs)

            # Категории для фильтрации с подсчётом статей
            categories = (
                Category.objects.annotate(
                    published_count=Count("articles", filter=Q(articles__status="published"))
                )
                .filter(published_count__gt=0)
                .order_by("name")
            )

            # Популярные теги для облака тегов
            popular_tags = Tag.objects.annotate(
                usage_count=Count("taggit_taggeditem_items")
            ).order_by("-usage_count")[:15]

            context.update(
                {
                    "categories": categories,
                    "popular_tags": popular_tags,
                    "current_category": self.request.GET.get("category"),
                    "current_difficulty": self.request.GET.get("difficulty"),
                    "current_tag": self.request.GET.get("tag"),
                    "current_sort": self.request.GET.get("sort", "-published_at"),
                    "page_title": "Все статьи блога",
                    "meta_description": "Все статьи блога PyLand о программировании, Python, Django, JavaScript и веб-разработке.",
                }
            )

            logger.info(
                f"Страница списка статей загружена. Найдено статей: {self.get_queryset().count()}"
            )
            return context

        except Exception as e:
            logger.error(f"Ошибка при формировании контекста списка статей: {e}", exc_info=True)
            return super().get_context_data(**kwargs)


class ArticleSearchView(ListView):
    """
    Страница с результатами полнотекстового поиска статей.

    Использует PostgreSQL полнотекстовый поиск (SearchVector, SearchQuery)
    для поиска по заголовку (вес A) и содержимому (вес B).
    Результаты отсортированы по релевантности.
    """

    model = Article
    template_name = "blog/search_results.html"
    context_object_name = "articles"
    paginate_by = 10

    def get_queryset(self) -> Any:
        """
        Возвращает queryset статей, соответствующих поисковому запросу.

        Returns:
            QuerySet: Опубликованные статьи, отсортированные по релевантности (rank).
                     Пустой queryset, если запрос пустой или слишком короткий.
        """
        try:
            query = self.request.GET.get("q", "").strip()

            # Валидация запроса
            if not query:
                logger.info("Поисковый запрос пустой")
                return Article.objects.none()

            if len(query) < 2:
                logger.info(f"Поисковый запрос слишком короткий: '{query}' (длина={len(query)})")
                return Article.objects.none()

            if len(query) > 200:
                logger.warning(f"Поисковый запрос слишком длинный: длина={len(query)}, обрезаем")
                query = query[:200]

            logger.info(f"Поиск статей по запросу: '{query}'")

            # Полнотекстовый поиск
            search_vector = SearchVector("title", weight="A") + SearchVector("content", weight="B")
            search_query = SearchQuery(query)

            queryset = (
                Article.objects.filter(status="published", published_at__lte=timezone.now())
                .annotate(rank=SearchRank(search_vector, search_query))
                .filter(rank__gt=0)
                .order_by("-rank", "-published_at")
                .select_related("category", "blog_author", "author")
                .prefetch_related("tags")
            )

            result_count = queryset.count()
            logger.info(f"Найдено статей: {result_count} для запроса '{query}'")

            return queryset

        except Exception as e:
            logger.error(f"Ошибка при поиске статей: {e}", exc_info=True)
            return Article.objects.none()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """
        Добавляет поисковый запрос и результаты в контекст.

        Args:
            **kwargs: Аргументы контекста от родительского класса.

        Returns:
            dict[str, Any]: Контекст с ключами:
                - articles (QuerySet): Результаты поиска
                - query (str): Поисковый запрос
                - page_title (str): Заголовок страницы
                - meta_description (str): SEO описание
        """
        try:
            context = super().get_context_data(**kwargs)
            query = self.request.GET.get("q", "").strip()

            context.update(
                {
                    "query": query,
                    "page_title": f"Поиск: {query}" if query else "Поиск",
                    "meta_description": (
                        f'Результаты поиска по запросу "{query}" в блоге PyLand.'
                        if query
                        else "Поиск статей в блоге PyLand."
                    ),
                }
            )

            logger.info(f"Страница поиска загружена для запроса: '{query}'")
            return context

        except Exception as e:
            logger.error(f"Ошибка при формировании контекста поиска: {e}", exc_info=True)
            return super().get_context_data(**kwargs)


class CategoryDetailView(DetailView):
    """
    Детальная страница категории со списком статей.

    Отображает все опубликованные статьи выбранной категории
    с пагинацией и рекомендациями других категорий.
    """

    model = Category
    template_name = "blog/category_detail.html"
    context_object_name = "category"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """
        Формирование контекста для страницы категории.

        Args:
            **kwargs: Дополнительные параметры контекста

        Returns:
            dict[str, Any]: Контекст с данными:
                - articles: Статьи категории (пагинированные)
                - page_obj: Объект пагинации
                - other_categories: Другие категории для рекомендаций
                - page_title, meta_description: SEO данные
        """
        try:
            context = super().get_context_data(**kwargs)
            category = self.object

            # Статьи категории с оптимизацией запросов
            articles = (
                Article.objects.filter(
                    category=category,
                    status="published",
                    published_at__lte=timezone.now(),
                )
                .select_related("category", "blog_author", "author")
                .prefetch_related("tags")
                .order_by("-published_at")
            )

            # Пагинация
            paginator = Paginator(articles, 12)
            page_number = self.request.GET.get("page", 1)

            try:
                page_obj = paginator.get_page(page_number)
            except Exception as e:
                logger.warning(f"Ошибка пагинации для категории {category.slug}: {e}")
                page_obj = paginator.get_page(1)

            # Другие категории для рекомендаций (исключая текущую)
            other_categories = (
                Category.objects.annotate(
                    published_count=Count("articles", filter=Q(articles__status="published"))
                )
                .exclude(id=category.id)
                .filter(published_count__gt=0)
                .order_by("-published_count")[:3]
            )

            context.update(
                {
                    "articles": page_obj,
                    "page_obj": page_obj,
                    "other_categories": other_categories,
                    "page_title": f"Категория: {category.name}",
                    "meta_description": category.description
                    or f'Статьи категории "{category.name}" в блоге PyLand.',
                }
            )

            logger.info(f"Категория '{category.name}' загружена. Статей: {articles.count()}")
            return context

        except Exception as e:
            logger.error(f"Ошибка при загрузке категории: {e}", exc_info=True)
            return super().get_context_data(**kwargs)


class TagDetailView(TemplateView):
    """
    Страница со списком статей для определенного тега.

    Поддерживает:
    - Поиск тега по slug (например, 'python') или имени (для кириллицы)
    - Сортировку статей: new (новые), old (старые), alpha (алфавит), popular (популярные)
    - Пагинацию (12 статей на страницу)
    - Отображение связанных тегов (другие теги из статей текущего тега)
    """

    template_name = "blog/tag_detail.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """
        Формирует контекст для страницы тега.

        Args:
            **kwargs: Аргументы URL, включая 'slug' - идентификатор тега.

        Returns:
            dict[str, Any]: Словарь контекста с ключами:
                - tag (Tag): Объект тега
                - articles (Page): Страница статей с пагинацией
                - page_obj (Page): Объект пагинации
                - related_tags (QuerySet): Связанные теги (до 6)
                - sort_by (str): Текущая сортировка
                - page_title (str): Заголовок страницы
                - meta_description (str): SEO описание

        Raises:
            Http404: Если тег не найден ни по slug, ни по имени.
        """
        import urllib.parse

        try:
            context = super().get_context_data(**kwargs)
            tag_slug = kwargs["slug"]

            # Декодируем URL для поддержки кириллицы
            tag_name = urllib.parse.unquote(tag_slug)
            logger.info(f"Загрузка тега: slug='{tag_slug}', декодировано имя='{tag_name}'")

            tag = None
            try:
                # Сначала пробуем найти по slug
                tag = Tag.objects.get(slug=tag_slug)
                logger.info(f"Тег найден по slug: '{tag.name}' (ID: {tag.id})")
            except Tag.DoesNotExist:
                try:
                    # Если не нашли по slug, ищем по имени
                    tag = Tag.objects.get(name=tag_name)
                    logger.info(f"Тег найден по имени: '{tag.name}' (ID: {tag.id})")
                except Tag.DoesNotExist:
                    logger.warning(f"Тег не найден: slug='{tag_slug}', имя='{tag_name}'")
                    raise Http404("Тег не найден")

            # Получаем и валидируем параметр сортировки
            sort_by = self.request.GET.get("sort", "new")
            valid_sorts = ["new", "old", "alpha", "popular"]
            if sort_by not in valid_sorts:
                logger.warning(f"Некорректный параметр сортировки: '{sort_by}', используем 'new'")
                sort_by = "new"

            # Базовый queryset со статьями с этим тегом
            articles = (
                Article.objects.filter(
                    tags=tag, status="published", published_at__lte=timezone.now()
                )
                .select_related("category", "blog_author", "author")
                .prefetch_related("tags")
            )

            # Применяем сортировку
            if sort_by == "new":
                articles = articles.order_by("-published_at")
            elif sort_by == "old":
                articles = articles.order_by("published_at")
            elif sort_by == "alpha":
                articles = articles.order_by("title")
            elif sort_by == "popular":
                articles = articles.order_by("-views_count", "-published_at")

            articles = articles.distinct()
            article_count = articles.count()
            logger.info(
                f"Найдено статей для тега '{tag.name}': {article_count}, сортировка: {sort_by}"
            )

            # Похожие теги (другие теги из статей с текущим тегом, исключая сам тег)
            related_tags = (
                Tag.objects.filter(article__in=articles)
                .exclude(id=tag.id)
                .annotate(article_count=Count("article", distinct=True))
                .order_by("-article_count")[:6]
            )

            # Пагинация
            paginator = Paginator(articles, 12)
            page_number = self.request.GET.get("page", 1)

            try:
                page_obj = paginator.get_page(page_number)
            except Exception as e:
                logger.error(f"Ошибка пагинации для тега '{tag.name}': {e}")
                page_obj = paginator.get_page(1)

            context.update(
                {
                    "tag": tag,
                    "articles": page_obj,
                    "page_obj": page_obj,
                    "related_tags": related_tags,
                    "sort_by": sort_by,
                    "page_title": f"Тег: {tag.name}",
                    "meta_description": f'Статьи с тегом "{tag.name}" в блоге PyLand.',
                }
            )

            logger.info(f"Тег '{tag.name}' загружен. Статей на странице: {len(page_obj)}")
            return context

        except Http404:
            raise
        except Exception as e:
            logger.error(
                f"Ошибка при загрузке тега '{kwargs.get('slug', 'unknown')}': {e}",
                exc_info=True,
            )
            return super().get_context_data(**kwargs)


class CategoryListView(ListView):
    """
    Страница со списком всех категорий блога.

    Отображает все категории с количеством опубликованных статей в каждой,
    а также 3 самые популярные статьи для дополнительного контекста.
    """

    model = Category
    template_name = "blog/category_list.html"
    context_object_name = "categories"

    def get_queryset(self) -> Any:
        """
        Возвращает queryset категорий с подсчетом опубликованных статей.

        Returns:
            QuerySet: Категории с аннотацией published_count, отсортированные по имени.

        Note:
            Используем published_count вместо article_count, так как у модели Category
            уже есть @property article_count (Django не может перезаписать property аннотацией).
        """
        try:
            queryset = Category.objects.annotate(
                published_count=Count("articles", filter=Q(articles__status="published"))
            ).order_by("name")

            logger.info(f"Загружено категорий: {queryset.count()}")
            return queryset

        except Exception as e:
            logger.error(f"Ошибка при загрузке списка категорий: {e}", exc_info=True)
            return Category.objects.none()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """
        Добавляет в контекст популярные статьи.

        Args:
            **kwargs: Аргументы контекста от родительского класса.

        Returns:
            dict[str, Any]: Расширенный контекст с ключами:
                - categories (QuerySet): Список категорий
                - popular_articles (QuerySet): 3 самые популярные статьи
        """
        try:
            context = super().get_context_data(**kwargs)

            # Популярные статьи для секции "Популярные статьи по категориям"
            popular_articles = (
                Article.objects.filter(status="published", published_at__lte=timezone.now())
                .select_related("category", "blog_author", "author")
                .order_by("-views_count", "-published_at")[:3]
            )

            context["popular_articles"] = popular_articles
            logger.info(f"Загружено популярных статей: {popular_articles.count()}")

            return context

        except Exception as e:
            logger.error(
                f"Ошибка при формировании контекста списка категорий: {e}",
                exc_info=True,
            )
            return super().get_context_data(**kwargs)


class TagListView(TemplateView):
    """
    Страница со списком всех тегов, сгруппированных по категориям.

    Отображает теги, сгруппированные по категориям блога на основе
    ключевых слов категории (tag_keywords). Каждая категория показывает
    до 15 наиболее используемых тегов.
    """

    template_name = "blog/tag_list.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """
        Формирует контекст со списком тегов по категориям.

        Args:
            **kwargs: Аргументы контекста от родительского класса.

        Returns:
            dict[str, Any]: Контекст с ключами:
                - tag_categories (list): Список категорий с их тегами
                - page_title (str): Заголовок страницы
                - meta_description (str): SEO описание
        """
        try:
            context = super().get_context_data(**kwargs)

            # Все теги с количеством использований
            all_tags = (
                Tag.objects.annotate(usage_count=Count("taggit_taggeditem_items"))
                .filter(usage_count__gt=0)
                .order_by("-usage_count")
            )

            total_tags = all_tags.count()
            logger.info(f"Загружено тегов: {total_tags}")

            # Получаем категории для страницы тегов (order > 0)
            categories = Category.objects.filter(order__gt=0).order_by("order")
            logger.info(f"Категорий для группировки тегов: {categories.count()}")

            # Формируем данные для категорий тегов
            tag_categories = []
            for category in categories:
                keywords = category.get_tag_keywords_list()

                # Находим теги, соответствующие ключевым словам
                category_tags = []
                if keywords:
                    for tag in all_tags:
                        tag_name_lower = tag.name.lower()
                        if any(keyword in tag_name_lower for keyword in keywords):
                            category_tags.append({"name": tag.name, "count": tag.usage_count})

                # Добавляем категорию в любом случае (даже без тегов)
                tag_categories.append(
                    {
                        "name": category.name,
                        "slug": category.slug,
                        "emoji": category.icon,
                        "badge": category.badge or category.name,
                        "description": category.description,
                        "tags": category_tags[:15],  # Максимум 15 тегов
                    }
                )

                logger.info(
                    f"Категория '{category.name}': найдено {len(category_tags)} тегов (показываем {len(category_tags[:15])})"
                )

            context.update(
                {
                    "tag_categories": tag_categories,
                    "page_title": "Все теги блога",
                    "meta_description": "Все теги блога PyLand для поиска статей по интересующим темам.",
                }
            )

            logger.info(f"Страница тегов загружена. Категорий: {len(tag_categories)}")
            return context

        except Exception as e:
            logger.error(f"Ошибка при загрузке списка тегов: {e}", exc_info=True)
            return super().get_context_data(**kwargs)


class DifficultyListView(ListView):
    """
    Страница со списком статей определенного уровня сложности.

    Фильтрует статьи по уровню сложности (beginner, intermediate, advanced),
    отображает 12 статей на страницу с пагинацией.
    """

    model = Article
    template_name = "blog/difficulty_list.html"
    context_object_name = "articles"
    paginate_by = 12

    def get_queryset(self) -> Any:
        """
        Возвращает queryset статей с указанным уровнем сложности.

        Returns:
            QuerySet: Опубликованные статьи с заданным уровнем сложности,
                     отсортированные по дате публикации (новые первыми).
        """
        try:
            difficulty = self.kwargs["difficulty"]

            # Валидация уровня сложности
            valid_difficulties = [choice[0] for choice in Article.DIFFICULTY_CHOICES]
            if difficulty not in valid_difficulties:
                logger.warning(f"Некорректный уровень сложности: '{difficulty}'")
                return Article.objects.none()

            queryset = (
                Article.objects.filter(
                    difficulty=difficulty,
                    status="published",
                    published_at__lte=timezone.now(),
                )
                .select_related("category", "blog_author", "author")
                .prefetch_related("tags")
                .order_by("-published_at")
            )

            logger.info(f"Загружено статей уровня '{difficulty}': {queryset.count()}")
            return queryset

        except Exception as e:
            logger.error(f"Ошибка при загрузке статей по уровню сложности: {e}", exc_info=True)
            return Article.objects.none()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """
        Добавляет в контекст информацию об уровне сложности.

        Args:
            **kwargs: Аргументы контекста от родительского класса.

        Returns:
            dict[str, Any]: Расширенный контекст с ключами:
                - articles (QuerySet): Список статей
                - difficulty (str): Код уровня сложности
                - difficulty_display (str): Отображаемое имя уровня
                - page_title (str): Заголовок страницы
                - meta_description (str): SEO описание
        """
        try:
            context = super().get_context_data(**kwargs)
            difficulty = self.kwargs["difficulty"]
            difficulty_display = dict(Article.DIFFICULTY_CHOICES).get(difficulty, difficulty)

            context.update(
                {
                    "difficulty": difficulty,
                    "difficulty_display": difficulty_display,
                    "page_title": f"Статьи уровня: {difficulty_display}",
                    "meta_description": f'Статьи уровня "{difficulty_display}" в блоге PyLand.',
                }
            )

            logger.info(f"Страница уровня '{difficulty_display}' загружена")
            return context

        except Exception as e:
            logger.error(
                f"Ошибка при формировании контекста уровня сложности: {e}",
                exc_info=True,
            )
            return super().get_context_data(**kwargs)


class FeaturedArticlesView(ListView):
    """
    Страница с рекомендуемыми (избранными) статьями.

    Отображает статьи, помеченные как is_featured=True,
    с пагинацией по 12 статей на страницу.
    """

    model = Article
    template_name = "blog/featured.html"
    context_object_name = "articles"
    paginate_by = 12

    def get_queryset(self) -> Any:
        """
        Возвращает queryset избранных статей.

        Returns:
            QuerySet: Опубликованные избранные статьи,
                     отсортированные по дате публикации (новые первыми).
        """
        try:
            queryset = (
                Article.objects.filter(
                    is_featured=True,
                    status="published",
                    published_at__lte=timezone.now(),
                )
                .select_related("category", "blog_author", "author")
                .prefetch_related("tags")
                .order_by("-published_at")
            )

            logger.info(f"Загружено избранных статей: {queryset.count()}")
            return queryset

        except Exception as e:
            logger.error(f"Ошибка при загрузке избранных статей: {e}", exc_info=True)
            return Article.objects.none()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """
        Добавляет метаданные для SEO.

        Args:
            **kwargs: Аргументы контекста от родительского класса.

        Returns:
            dict[str, Any]: Контекст с метаданными страницы.
        """
        try:
            context = super().get_context_data(**kwargs)
            context.update(
                {
                    "page_title": "Избранные статьи",
                    "meta_description": "Избранные и рекомендуемые статьи блога PyLand.",
                }
            )
            return context

        except Exception as e:
            logger.error(
                f"Ошибка при формировании контекста избранных статей: {e}",
                exc_info=True,
            )
            return super().get_context_data(**kwargs)


class NewsletterSubscribeView(View):
    """
    API endpoint для подписки на рассылку блога.

    Обрабатывает POST-запросы с email и опциональным именем,
    создает подписку или возобновляет неактивную, отправляет приветственное письмо.
    """

    def post(self, request: Any) -> JsonResponse:
        """
        Обрабатывает подписку на рассылку.

        Args:
            request: HTTP-запрос с полями:
                - email (str): Email подписчика (обязательно)
                - name (str): Имя подписчика (опционально)

        Returns:
            JsonResponse: JSON с ключами:
                - success (bool): Успешность операции
                - message (str): Сообщение для пользователя
        """
        try:
            email = request.POST.get("email", "").strip()
            name = request.POST.get("name", "").strip()

            # Валидация email
            if not email:
                logger.warning("Попытка подписки без email")
                return JsonResponse({"success": False, "message": "Email обязателен"})

            # Базовая валидация формата email
            if "@" not in email or "." not in email.split("@")[-1]:
                logger.warning(f"Некорректный формат email: {email}")
                return JsonResponse({"success": False, "message": "Некорректный формат email"})

            # Создание или получение подписки
            subscription, created = Newsletter.objects.get_or_create(
                email=email, defaults={"name": name, "is_active": True}
            )

            if created:
                logger.info(f"Новая подписка: {email} (имя: {name or 'не указано'})")

                # Отправка приветственного письма
                try:
                    send_mail(
                        subject="Добро пожаловать в PyLand!",
                        message=f"Привет, {name or 'друг'}!\n\nСпасибо за подписку на блог PyLand. Теперь ты будешь первым узнавать о новых статьях и уроках программирования.",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[email],
                        fail_silently=True,
                    )
                    logger.info(f"Приветственное письмо отправлено: {email}")
                except Exception as e:
                    logger.error(f"Ошибка отправки приветственного письма для {email}: {e}")

                return JsonResponse({"success": True, "message": "Спасибо за подписку!"})

            else:
                if subscription.is_active:
                    logger.info(f"Попытка повторной подписки (уже активна): {email}")
                    return JsonResponse({"success": False, "message": "Вы уже подписаны"})
                else:
                    subscription.is_active = True
                    subscription.save()
                    logger.info(f"Подписка возобновлена: {email}")
                    return JsonResponse({"success": True, "message": "Подписка возобновлена!"})

        except Exception as e:
            logger.error(f"Ошибка при подписке на рассылку: {e}", exc_info=True)
            return JsonResponse(
                {"success": False, "message": "Произошла ошибка. Попробуйте позже."},
                status=500,
            )


class NewsletterUnsubscribeView(View):
    """
    API endpoint для отписки от рассылки блога.

    Обрабатывает POST-запросы с email, деактивирует подписку.
    """

    def post(self, request: Any) -> JsonResponse:
        """
        Обрабатывает отписку от рассылки.

        Args:
            request: HTTP-запрос с полем:
                - email (str): Email для отписки

        Returns:
            JsonResponse: JSON с ключами:
                - success (bool): Успешность операции
                - message (str): Сообщение для пользователя
        """
        try:
            email = request.POST.get("email", "").strip()

            if not email:
                logger.warning("Попытка отписки без email")
                return JsonResponse({"success": False, "message": "Email обязателен"})

            try:
                subscription = Newsletter.objects.get(email=email)

                if not subscription.is_active:
                    logger.info(f"Попытка отписки неактивной подписки: {email}")
                    return JsonResponse({"success": False, "message": "Вы уже отписаны"})

                subscription.is_active = False
                subscription.save()
                logger.info(f"Отписка выполнена: {email}")
                return JsonResponse({"success": True, "message": "Вы отписались от рассылки"})

            except Newsletter.DoesNotExist:
                logger.warning(f"Попытка отписки несуществующего email: {email}")
                return JsonResponse({"success": False, "message": "Email не найден"})

        except Exception as e:
            logger.error(f"Ошибка при отписке от рассылки: {e}", exc_info=True)
            return JsonResponse(
                {"success": False, "message": "Произошла ошибка. Попробуйте позже."},
                status=500,
            )


class AddCommentView(View):
    """
    API endpoint для добавления комментария к статье.

    Поддерживает создание как обычных комментариев, так и ответов (replies)
    на существующие комментарии через parent_id.
    """

    def post(self, request: Any) -> JsonResponse:
        """
        Создает новый комментарий к статье.

        Args:
            request: HTTP-запрос с полями:
                - article_slug (str): Slug статьи
                - content (str): Текст комментария
                - parent_id (int, optional): ID родительского комментария для ответа

        Returns:
            JsonResponse: JSON с ключами:
                - success (bool): Успешность операции
                - message (str): Сообщение для пользователя
                - comment (dict): Данные созданного комментария (при success=True)
        """
        try:
            # Проверка аутентификации
            if not request.user.is_authenticated:
                logger.warning("Попытка добавления комментария без аутентификации")
                return JsonResponse({"success": False, "message": "Необходимо войти в систему"})

            # Получение и валидация данных
            article_slug = request.POST.get("article_slug")
            content = request.POST.get("content", "").strip()
            parent_id = request.POST.get("parent_id")

            if not article_slug:
                logger.warning("Попытка добавления комментария без article_slug")
                return JsonResponse({"success": False, "message": "Не указана статья"})

            if not content:
                logger.warning(
                    f"Попытка добавления пустого комментария пользователем {request.user.username}"
                )
                return JsonResponse(
                    {"success": False, "message": "Комментарий не может быть пустым"}
                )

            if len(content) > 5000:
                logger.warning(
                    f"Попытка добавления слишком длинного комментария ({len(content)} символов)"
                )
                return JsonResponse(
                    {
                        "success": False,
                        "message": "Комментарий слишком длинный (максимум 5000 символов)",
                    }
                )

            # Получение статьи
            try:
                article = Article.objects.get(slug=article_slug, status="published")
            except Article.DoesNotExist:
                logger.warning(
                    f"Попытка добавления комментария к несуществующей статье: {article_slug}"
                )
                return JsonResponse({"success": False, "message": "Статья не найдена"})

            # Проверка разрешения комментариев
            if not article.allow_comments:
                logger.info(
                    f"Попытка добавления комментария к статье с отключенными комментариями: {article_slug}"
                )
                return JsonResponse(
                    {"success": False, "message": "Комментарии к этой статье отключены"}
                )

            # Получение родительского комментария (если это ответ)
            parent = None
            if parent_id:
                try:
                    parent = Comment.objects.get(id=parent_id, article=article)
                    logger.info(f"Ответ на комментарий ID={parent_id}")
                except Comment.DoesNotExist:
                    logger.warning(f"Несуществующий родительский комментарий ID={parent_id}")

            # Создание комментария
            comment = Comment.objects.create(
                article=article, author=request.user, parent=parent, content=content
            )

            logger.info(
                f"Комментарий создан: ID={comment.id}, автор={request.user.username}, "
                f"статья={article_slug}, родитель={'ID=' + str(parent_id) if parent_id else 'нет'}"
            )

            return JsonResponse(
                {
                    "success": True,
                    "message": "Комментарий добавлен",
                    "comment": {
                        "id": comment.id,
                        "content": comment.content,
                        "author": comment.author.username,
                        "created_at": comment.created_at.strftime("%d.%m.%Y %H:%M"),
                    },
                }
            )

        except Exception as e:
            logger.error(f"Ошибка при добавлении комментария: {e}", exc_info=True)
            return JsonResponse(
                {"success": False, "message": "Произошла ошибка. Попробуйте позже."},
                status=500,
            )


class LoadMoreArticlesView(View):
    """
    API endpoint для динамической подгрузки статей (infinite scroll).

    Поддерживает фильтрацию по категории, тегу, уровню сложности.
    Возвращает JSON с данными статей и информацией о пагинации.
    """

    def get(self, request: Any) -> JsonResponse:
        """
        Возвращает страницу статей с опциональной фильтрацией.

        Args:
            request: HTTP-запрос с GET-параметрами:
                - page (int): Номер страницы (по умолчанию 1)
                - category (str): Slug категории для фильтрации
                - tag (str): Slug тега для фильтрации
                - difficulty (str): Уровень сложности для фильтрации

        Returns:
            JsonResponse: JSON с ключами:
                - articles (list): Список статей с полными данными
                - has_next (bool): Есть ли следующая страница
                - next_page (int|None): Номер следующей страницы
        """
        try:
            # Получение и валидация параметров
            try:
                page = int(request.GET.get("page", 1))
                if page < 1:
                    page = 1
            except (ValueError, TypeError):
                logger.warning(f"Некорректный номер страницы: {request.GET.get('page')}")
                page = 1

            category_slug = request.GET.get("category")
            tag_slug = request.GET.get("tag")
            difficulty = request.GET.get("difficulty")

            # Базовый queryset
            queryset = (
                Article.objects.filter(status="published", published_at__lte=timezone.now())
                .select_related("category", "blog_author", "author")
                .prefetch_related("tags")
                .order_by("-published_at")
            )

            # Применение фильтров
            filters_applied = []
            if category_slug:
                queryset = queryset.filter(category__slug=category_slug)
                filters_applied.append(f"category={category_slug}")
            if tag_slug:
                queryset = queryset.filter(tags__slug=tag_slug).distinct()
                filters_applied.append(f"tag={tag_slug}")
            if difficulty:
                # Валидация уровня сложности
                valid_difficulties = [choice[0] for choice in Article.DIFFICULTY_CHOICES]
                if difficulty in valid_difficulties:
                    queryset = queryset.filter(difficulty=difficulty)
                    filters_applied.append(f"difficulty={difficulty}")
                else:
                    logger.warning(f"Некорректный уровень сложности: {difficulty}")

            logger.info(
                f"LoadMoreArticles: страница={page}, фильтры=[{', '.join(filters_applied) or 'нет'}]"
            )

            # Пагинация
            paginator = Paginator(queryset, 6)

            try:
                page_obj = paginator.get_page(page)
            except Exception as e:
                logger.error(f"Ошибка пагинации: {e}")
                page_obj = paginator.get_page(1)

            # Формирование данных статей
            articles_data = []
            for article in page_obj:
                try:
                    # Используем дружелюбное отображаемое имя автора
                    author_name = article.get_author_display_name()

                    # Безопасное получение URL изображения
                    try:
                        featured_image_url = (
                            article.featured_image.url if article.featured_image else None
                        )
                    except Exception:
                        featured_image_url = None

                    articles_data.append(
                        {
                            "title": article.title,
                            "slug": article.slug,
                            "excerpt": article.excerpt,
                            "category": article.category.name if article.category else "",
                            "author": author_name,
                            "published_at": (
                                article.published_at.strftime("%d.%m.%Y")
                                if article.published_at
                                else ""
                            ),
                            "reading_time": article.reading_time,
                            "views_count": article.views_count,
                            "url": article.get_absolute_url(),
                            "featured_image": featured_image_url,
                        }
                    )
                except Exception as e:
                    logger.error(f"Ошибка формирования данных статьи ID={article.id}: {e}")
                    continue

            logger.info(
                f"LoadMoreArticles: возвращено статей={len(articles_data)}, has_next={page_obj.has_next()}"
            )

            return JsonResponse(
                {
                    "articles": articles_data,
                    "has_next": page_obj.has_next(),
                    "next_page": page_obj.next_page_number() if page_obj.has_next() else None,
                }
            )

        except Exception as e:
            logger.error(f"Ошибка в LoadMoreArticlesView: {e}", exc_info=True)
            return JsonResponse({"articles": [], "has_next": False, "next_page": None}, status=500)


class ArticleReactionView(View):
    """
    API endpoint для добавления/изменения реакции на статью.

    Поддерживает 5 типов эмодзи-реакций:
    - like: 👍 Нравится
    - love: ❤️ Супер
    - helpful: 💡 Полезно
    - insightful: 🤔 Интересно
    - amazing: 🤩 Потрясающе

    Особенности:
    - Один пользователь может оставить только одну реакцию на статью
    - При повторном клике на ту же реакцию - она удаляется
    - При выборе другой реакции - старая заменяется новой
    - Требуется аутентификация

    Methods:
        post(): Добавляет, изменяет или удаляет реакцию
        get(): Возвращает статистику реакций для статьи
    """

    def post(self, request: Any) -> JsonResponse:
        """
        Добавляет, изменяет или удаляет реакцию пользователя на статью.

        Args:
            request: HTTP-запрос с POST параметрами:
                - article_slug (str): Slug статьи (обязательно)
                - reaction_type (str): Тип реакции из REACTION_CHOICES (обязательно)

        Returns:
            JsonResponse: JSON с ключами:
                - success (bool): Успешность операции
                - message (str): Сообщение для пользователя
                - action (str): Выполненное действие ('added', 'changed', 'removed')
                - reactions (dict): Обновлённая статистика реакций {type: count}
                - user_reaction (str|None): Текущая реакция пользователя или None
        """
        try:
            # Проверка аутентификации
            if not request.user.is_authenticated:
                logger.warning("Попытка добавить реакцию без аутентификации")
                return JsonResponse(
                    {
                        "success": False,
                        "message": "Необходимо войти в систему для добавления реакции",
                    },
                    status=401,
                )

            # Получение и валидация параметров
            article_slug = request.POST.get("article_slug")
            reaction_type = request.POST.get("reaction_type")

            if not article_slug:
                logger.warning("Попытка добавить реакцию без article_slug")
                return JsonResponse({"success": False, "message": "Не указана статья"}, status=400)

            if not reaction_type:
                logger.warning("Попытка добавить реакцию без reaction_type")
                return JsonResponse(
                    {"success": False, "message": "Не указан тип реакции"}, status=400
                )

            # Валидация типа реакции
            from .models import ArticleReaction

            valid_reactions = [choice[0] for choice in ArticleReaction.REACTION_CHOICES]

            if reaction_type not in valid_reactions:
                logger.warning(f"Некорректный тип реакции: {reaction_type}")
                return JsonResponse(
                    {
                        "success": False,
                        "message": f"Некорректный тип реакции. Допустимые: {', '.join(valid_reactions)}",
                    },
                    status=400,
                )

            # Проверка существования статьи
            try:
                article = Article.objects.get(slug=article_slug, status="published")
            except Article.DoesNotExist:
                logger.warning(f"Попытка добавить реакцию к несуществующей статье: {article_slug}")
                return JsonResponse({"success": False, "message": "Статья не найдена"}, status=404)

            # Обработка реакции
            action = "added"
            message = "Спасибо за вашу реакцию!"

            try:
                # Проверяем существующую реакцию пользователя
                existing_reaction = ArticleReaction.objects.filter(
                    user=request.user, article=article
                ).first()

                if existing_reaction:
                    if existing_reaction.reaction_type == reaction_type:
                        # Удаляем реакцию при повторном клике
                        existing_reaction.delete()
                        action = "removed"
                        message = "Реакция удалена"
                        user_reaction = None
                        logger.info(
                            f"Реакция удалена: {request.user.username} убрал "
                            f"'{reaction_type}' с '{article.slug}'"
                        )
                    else:
                        # Изменяем тип реакции
                        old_type = existing_reaction.reaction_type
                        existing_reaction.reaction_type = reaction_type
                        existing_reaction.save()
                        action = "changed"
                        message = "Реакция изменена!"
                        user_reaction = reaction_type
                        logger.info(
                            f"Реакция изменена: {request.user.username} изменил "
                            f"'{old_type}' → '{reaction_type}' на '{article.slug}'"
                        )
                else:
                    # Создаём новую реакцию
                    ArticleReaction.objects.create(
                        user=request.user, article=article, reaction_type=reaction_type
                    )
                    user_reaction = reaction_type
                    logger.info(
                        f"Новая реакция: {request.user.username} оставил "
                        f"'{reaction_type}' на '{article.slug}'"
                    )

            except Exception as e:
                logger.error(f"Ошибка при обработке реакции: {e}", exc_info=True)
                return JsonResponse(
                    {"success": False, "message": "Ошибка при обработке реакции"},
                    status=500,
                )

            # Получаем обновлённую статистику реакций
            reactions_stats = self._get_reactions_stats(article)

            return JsonResponse(
                {
                    "success": True,
                    "message": message,
                    "action": action,
                    "reactions": reactions_stats,
                    "user_reaction": user_reaction,
                }
            )

        except Exception as e:
            logger.error(f"Ошибка в ArticleReactionView.post: {e}", exc_info=True)
            return JsonResponse(
                {"success": False, "message": "Произошла ошибка. Попробуйте позже."},
                status=500,
            )

    def get(self, request: Any) -> JsonResponse:
        """
        Возвращает статистику реакций для статьи.

        Args:
            request: HTTP-запрос с GET параметром:
                - article_slug (str): Slug статьи

        Returns:
            JsonResponse: JSON с ключами:
                - success (bool): Успешность операции
                - reactions (dict): Статистика реакций {type: count}
                - user_reaction (str|None): Реакция текущего пользователя
                - total (int): Общее количество реакций
        """
        try:
            article_slug = request.GET.get("article_slug")

            if not article_slug:
                return JsonResponse({"success": False, "message": "Не указана статья"}, status=400)

            try:
                article = Article.objects.get(slug=article_slug, status="published")
            except Article.DoesNotExist:
                return JsonResponse({"success": False, "message": "Статья не найдена"}, status=404)

            # Получаем статистику
            reactions_stats = self._get_reactions_stats(article)
            total = sum(reactions_stats.values())

            # Получаем реакцию пользователя если он авторизован
            user_reaction = None
            if request.user.is_authenticated:
                from .models import ArticleReaction

                user_reaction_obj = ArticleReaction.objects.filter(
                    user=request.user, article=article
                ).first()
                if user_reaction_obj:
                    user_reaction = user_reaction_obj.reaction_type

            return JsonResponse(
                {
                    "success": True,
                    "reactions": reactions_stats,
                    "user_reaction": user_reaction,
                    "total": total,
                }
            )

        except Exception as e:
            logger.error(f"Ошибка в ArticleReactionView.get: {e}", exc_info=True)
            return JsonResponse(
                {"success": False, "message": "Ошибка при получении статистики"},
                status=500,
            )

    def _get_reactions_stats(self, article: Article) -> dict[str, int]:
        """
        Подсчитывает количество реакций каждого типа для статьи.

        Args:
            article: Статья для подсчёта реакций

        Returns:
            dict[str, int]: Словарь {тип_реакции: количество}
        """
        from django.db.models import Count

        from .models import ArticleReaction

        reactions = (
            ArticleReaction.objects.filter(article=article)
            .values("reaction_type")
            .annotate(count=Count("id"))
        )

        # Инициализируем все типы реакций нулями
        stats = {choice[0]: 0 for choice in ArticleReaction.REACTION_CHOICES}

        # Заполняем реальными значениями
        for reaction in reactions:
            stats[reaction["reaction_type"]] = reaction["count"]

        return stats


# Алиас для обратной совместимости
class LikeArticleView(ArticleReactionView):
    """
    Алиас для обратной совместимости.
    Перенаправляет на ArticleReactionView.

    Deprecated: Используйте ArticleReactionView напрямую.
    """

    pass


class SeriesListView(ListView):
    """
    Страница со списком всех серий статей.

    Отображает серии с количеством статей, прогрессом чтения (для аутентифицированных),
    и общей статистикой. 12 серий на страницу.
    """

    model = Series
    template_name = "blog/series_list.html"
    context_object_name = "series_list"
    paginate_by = 12

    def get_queryset(self) -> Any:
        """
        Возвращает queryset серий с аннотацией количества статей.

        Returns:
            QuerySet: Серии с аннотацией articles_count,
                     отсортированные по избранности и дате создания.
        """
        try:
            queryset = (
                Series.objects.select_related("author")
                .annotate(articles_count=Count("articles", filter=Q(articles__status="published")))
                .order_by("-is_featured", "-created_at")
            )

            logger.info(f"Загружено серий: {queryset.count()}")
            return queryset

        except Exception as e:
            logger.error(f"Ошибка при загрузке списка серий: {e}", exc_info=True)
            return Series.objects.none()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """
        Добавляет прогресс чтения и статистику в контекст.

        Args:
            **kwargs: Аргументы контекста от родительского класса.

        Returns:
            dict[str, Any]: Расширенный контекст с ключами:
                - series_list (QuerySet): Список серий с динамически добавленным completion_percentage
                - total_articles (int): Общее количество статей в сериях
                - active_series (int): Количество активных серий
                - expert_authors (int): Количество авторов
                - page_title (str): Заголовок страницы
                - meta_description (str): SEO описание
        """
        try:
            context = super().get_context_data(**kwargs)

            # Добавляем completion_percentage для каждой серии (если пользователь аутентифицирован)
            series_list = context.get("series_list") or context.get("page_obj")
            if series_list and self.request.user.is_authenticated:
                from .models import ReadingProgress

                for series in series_list:
                    try:
                        # Получаем опубликованные статьи серии
                        published_articles = series.articles.filter(
                            status="published", published_at__lte=timezone.now()
                        )
                        total_articles = published_articles.count()

                        if total_articles > 0:
                            # Считаем прочитанные статьи
                            completed_count = ReadingProgress.objects.filter(
                                user=self.request.user,
                                article__in=published_articles,
                                status="completed",
                            ).count()

                            # Добавляем статьи в процессе (>50% прогресса)
                            in_progress_count = ReadingProgress.objects.filter(
                                user=self.request.user,
                                article__in=published_articles,
                                status="in_progress",
                                progress_percentage__gte=50,
                            ).count()

                            completed_count += in_progress_count
                            series.completion_percentage = int(
                                (completed_count / total_articles * 100)
                            )
                        else:
                            series.completion_percentage = 0
                    except Exception as e:
                        logger.error(f"Ошибка подсчета прогресса для серии ID={series.id}: {e}")
                        series.completion_percentage = 0

            # Статистика для хиро секции
            try:
                total_articles = Article.objects.filter(
                    status="published", series__isnull=False
                ).count()

                active_series = (
                    Series.objects.filter(status="active", articles__status="published")
                    .distinct()
                    .count()
                )

                # Проверяем наличие поля is_active у модели Author
                expert_authors = (
                    Author.objects.filter(is_active=True).count()
                    if hasattr(Author, "is_active")
                    else Author.objects.count()
                )

                logger.info(
                    f"Статистика серий: статей={total_articles}, серий={active_series}, авторов={expert_authors}"
                )

            except Exception as e:
                logger.error(f"Ошибка подсчета статистики серий: {e}")
                total_articles = active_series = expert_authors = 0

            context.update(
                {
                    "total_articles": total_articles,
                    "active_series": active_series,
                    "expert_authors": expert_authors,
                    "page_title": "Серии статей",
                    "meta_description": "Структурированные серии статей по программированию и разработке от наших экспертов",
                }
            )

            logger.info("Страница списка серий загружена")
            return context

        except Exception as e:
            logger.error(f"Ошибка при формировании контекста списка серий: {e}", exc_info=True)
            return super().get_context_data(**kwargs)


class SeriesDetailView(DetailView):
    """
    Детальная страница серии статей.

    Отображает информацию о серии, список статей в серии по порядку,
    прогресс чтения (для аутентифицированных), похожие серии, статистику.
    """

    model = Series
    template_name = "blog/series_detail.html"
    context_object_name = "series"

    def get_queryset(self) -> Any:
        """
        Возвращает queryset серий с оптимизированными связями.

        Returns:
            QuerySet: Серии с предзагруженными author, articles, categories.
        """
        return Series.objects.select_related("author").prefetch_related(
            "articles__author", "articles__category"
        )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """
        Формирует расширенный контекст для страницы серии.

        Args:
            **kwargs: Аргументы контекста от родительского класса.

        Returns:
            dict[str, Any]: Контекст с ключами:
                - series (Series): Объект серии
                - published_articles (QuerySet): Опубликованные статьи серии по порядку
                - related_series (QuerySet): Похожие серии (до 6)
                - total_views (int): Суммарные просмотры всех статей
                - total_articles (int): Количество статей в серии
                - completed_articles (int): Прочитанных статей (для auth)
                - completion_percentage (int): Процент завершения (для auth)
                - total_reading_time (int): Общее время чтения (минуты)
                - series_author_profile (Author|None): Профиль автора
                - series_author_display (str): Отображаемое имя автора
                - page_title (str): Заголовок страницы
                - meta_description (str): SEO описание
        """
        try:
            context = super().get_context_data(**kwargs)
            # Получаем объект серии из уже подготовленного контекста/self.object
            series = getattr(self, "object", None) or context.get("series") or self.get_object()

            logger.info(f"Загрузка серии: '{series.title}' (ID: {series.id})")

            # Статьи серии (опубликованные)
            published_articles = (
                series.articles.filter(status="published", published_at__lte=timezone.now())
                .select_related("author", "category")
                .order_by("series_order", "published_at")
            )

            # Добавляем в контекст и к объекту серии для совместимости с шаблонами
            context["published_articles"] = published_articles
            try:
                setattr(series, "published_articles", published_articles)
            except Exception as e:
                logger.warning(f"Не удалось добавить published_articles к объекту серии: {e}")

            # Похожие серии (от того же автора или с похожими тегами)
            try:
                related_series = (
                    Series.objects.filter(Q(author=series.author) | Q(tags__in=series.tags.all()))
                    .exclude(id=series.id)
                    .distinct()
                    .annotate(
                        articles_count=Count("articles", filter=Q(articles__status="published"))
                    )[:6]
                )
            except Exception as e:
                logger.error(f"Ошибка загрузки похожих серий: {e}")
                related_series = Series.objects.none()

            # Статистика серии — суммируем просмотры статей
            from django.db.models import Sum

            try:
                total_views = published_articles.aggregate(total=Sum("views_count"))["total"] or 0
            except Exception as e:
                logger.error(f"Ошибка подсчета просмотров: {e}")
                total_views = 0

            # Подсчет прогресса серии
            total_articles = published_articles.count()
            completed_articles = 0
            completion_percentage = 0

            # Если пользователь аутентифицирован, подсчитываем реальный прогресс
            if self.request.user.is_authenticated:
                try:
                    from .models import ReadingProgress

                    # Считаем количество прочитанных статей в серии
                    completed_articles = ReadingProgress.objects.filter(
                        user=self.request.user,
                        article__in=published_articles,
                        status="completed",
                    ).count()

                    # Также считаем статьи в процессе чтения (более 50% прогресса)
                    in_progress_completed = ReadingProgress.objects.filter(
                        user=self.request.user,
                        article__in=published_articles,
                        status="in_progress",
                        progress_percentage__gte=50,
                    ).count()

                    completed_articles += in_progress_completed
                    completion_percentage = (
                        int((completed_articles / total_articles * 100))
                        if total_articles > 0
                        else 0
                    )

                    logger.info(
                        f"Прогресс пользователя {self.request.user.username}: {completed_articles}/{total_articles} ({completion_percentage}%)"
                    )
                except Exception as e:
                    logger.error(f"Ошибка подсчета прогресса чтения: {e}")

            # Подсчет общего времени чтения
            try:
                total_reading_time = (
                    published_articles.aggregate(total=Sum("reading_time"))["total"] or 0
                )
            except Exception as e:
                logger.error(f"Ошибка подсчета времени чтения: {e}")
                total_reading_time = 0

            # Отображаемое имя автора: используем профиль Author, если он есть
            author_profile = None
            try:
                author_profile = getattr(series.author, "blog_author_profile", None)
            except Exception as e:
                logger.warning(f"Не удалось получить профиль автора: {e}")

            series_author_display = (
                author_profile.display_name
                if author_profile
                else (series.author.get_full_name() or series.author.username)
            )

            context.update(
                {
                    "related_series": related_series,
                    "total_views": total_views,
                    "total_articles": total_articles,
                    "completed_articles": completed_articles,
                    "completion_percentage": completion_percentage,
                    "total_reading_time": total_reading_time,
                    "series_author_profile": author_profile,
                    "series_author_display": series_author_display,
                    "page_title": series.title,
                    "meta_description": (
                        series.meta_description or series.description[:160]
                        if series.description
                        else f"Серия статей: {series.title}"
                    ),
                }
            )

            logger.info(
                f"Серия '{series.title}' загружена. Статей: {total_articles}, просмотров: {total_views}"
            )
            return context

        except Exception as e:
            logger.error(f"Ошибка при загрузке серии: {e}", exc_info=True)
            return super().get_context_data(**kwargs)


class AuthorListView(ListView):
    """
    Страница со списком всех авторов блога.

    Отображает авторов, у которых есть опубликованные статьи,
    с информацией о количестве статей и дате последней публикации.
    12 авторов на страницу.
    """

    model = Author
    template_name = "blog/author_list.html"
    context_object_name = "authors"
    paginate_by = 12

    def get_queryset(self) -> Any:
        """
        Возвращает queryset авторов с опубликованными статьями.

        Returns:
            QuerySet: Авторы с аннотациями last_published и followers_count_annotated,
                     отсортированные по избранности, количеству статей и имени.
        """
        try:
            # Аннотируем дату последней публикации, чтобы не делать отдельный запрос на каждого автора
            queryset = (
                Author.objects.filter(
                    articles_count__gt=0  # Только авторы с опубликованными статьями
                )
                .annotate(
                    last_published=Max(
                        "articles__published_at", filter=Q(articles__status="published")
                    ),
                    followers_count_annotated=Value(0),
                )
                .order_by("-is_featured", "-articles_count", "display_name")
            )

            logger.info(f"Загружено авторов: {queryset.count()}")
            return queryset

        except Exception as e:
            logger.error(f"Ошибка при загрузке списка авторов: {e}", exc_info=True)
            return Author.objects.none()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """
        Добавляет избранных авторов в контекст.

        Args:
            **kwargs: Аргументы контекста от родительского класса.

        Returns:
            dict[str, Any]: Расширенный контекст с ключами:
                - authors (QuerySet): Список авторов
                - featured_authors (QuerySet): Избранные авторы (до 6)
                - page_title (str): Заголовок страницы
                - meta_description (str): SEO описание
        """
        try:
            context = super().get_context_data(**kwargs)

            # Рекомендуемые авторы
            try:
                featured_authors = Author.objects.filter(
                    is_featured=True, articles_count__gt=0
                ).annotate(
                    last_published=Max(
                        "articles__published_at", filter=Q(articles__status="published")
                    ),
                    followers_count_annotated=Value(0),
                )[
                    :6
                ]

                logger.info(f"Загружено избранных авторов: {featured_authors.count()}")
            except Exception as e:
                logger.error(f"Ошибка загрузки избранных авторов: {e}")
                featured_authors = Author.objects.none()

            # Статистика для главной страницы авторов
            try:
                # Общее количество авторов с опубликованными статьями
                total_authors = Author.objects.filter(articles_count__gt=0).count()

                # Общее количество статей всех авторов
                total_articles = Article.objects.filter(status="published").count()

                # Общее количество просмотров всех статей
                total_views = (
                    Article.objects.filter(status="published").aggregate(total=Sum("views_count"))[
                        "total"
                    ]
                    or 0
                )

                # Общее количество реакций на все статьи
                total_reactions = ArticleReaction.objects.count()

                stats = {
                    "total_authors": total_authors,
                    "total_articles": total_articles,
                    "total_views": total_views,
                    "total_reactions": total_reactions,
                }

                logger.info(
                    f"Статистика авторов: авторов={total_authors}, статей={total_articles}, просмотров={total_views}, реакций={total_reactions}"
                )
            except Exception as e:
                logger.error(f"Ошибка расчета статистики авторов: {e}")
                stats = {
                    "total_authors": 0,
                    "total_articles": 0,
                    "total_views": 0,
                    "total_reactions": 0,
                }

            context.update(
                {
                    "featured_authors": featured_authors,
                    "stats": stats,
                    "page_title": "Авторы блога",
                    "meta_description": "Познакомьтесь с нашими экспертами и писателями",
                }
            )

            logger.info("Страница списка авторов загружена")
            return context

        except Exception as e:
            logger.error(f"Ошибка при формировании контекста списка авторов: {e}", exc_info=True)
            return super().get_context_data(**kwargs)


class AuthorDetailView(DetailView):
    """
    Детальная страница автора блога.

    Отображает профиль автора, его статьи с пагинацией (10 на страницу),
    серии статей, статистику по категориям, популярные теги, социальные ссылки.
    """

    model = Author
    template_name = "blog/author_detail.html"
    context_object_name = "author"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """
        Формирует расширенный контекст для страницы автора.

        Args:
            **kwargs: Аргументы контекста от родительского класса.

        Returns:
            dict[str, Any]: Контекст с ключами:
                - author (Author): Объект автора
                - articles (Page): Страница статей с пагинацией
                - author_series (QuerySet): Серии автора
                - categories_stats (QuerySet): Топ-5 категорий по количеству статей
                - popular_tags (QuerySet): Топ-10 популярных тегов
                - social_links (dict): Словарь социальных ссылок
                - page_title (str): Заголовок страницы
                - meta_description (str): SEO описание
        """
        try:
            context = super().get_context_data(**kwargs)
            author = self.get_object()

            logger.info(f"Загрузка страницы автора: {author.display_name} (ID: {author.id})")

            # Опубликованные статьи автора
            try:
                articles = (
                    author.articles.filter(status="published", published_at__lte=timezone.now())
                    .select_related("category")
                    .prefetch_related("tags")
                    .order_by("-published_at")
                )

                article_count = articles.count()
                logger.info(f"Статей автора: {article_count}")
            except Exception as e:
                logger.error(f"Ошибка загрузки статей автора: {e}")
                articles = Article.objects.none()

            # Пагинация статей
            paginator = Paginator(articles, 10)
            page_number = self.request.GET.get("page", 1)

            try:
                page_obj = paginator.get_page(page_number)
            except Exception as e:
                logger.error(f"Ошибка пагинации статей автора: {e}")
                page_obj = paginator.get_page(1)

            # Статистика по категориям
            try:
                categories_stats = (
                    articles.values("category__name", "category__icon")
                    .annotate(count=Count("id"))
                    .order_by("-count")[:5]
                )
            except Exception as e:
                logger.error(f"Ошибка подсчета статистики категорий: {e}")
                categories_stats = []

            # Популярные теги
            try:
                popular_tags = (
                    Tag.objects.filter(
                        taggit_taggeditem_items__object_id__in=articles.values("id"),
                        taggit_taggeditem_items__content_type__model="article",
                    )
                    .annotate(article_count=Count("taggit_taggeditem_items"))
                    .order_by("-article_count")[:10]
                )
            except Exception as e:
                logger.error(f"Ошибка загрузки популярных тегов: {e}")
                popular_tags = Tag.objects.none()

            # Серии автора
            try:
                from .models import Series

                author_series = (
                    Series.objects.filter(author=author.user)
                    .annotate(
                        articles_count=Count("articles", filter=Q(articles__status="published"))
                    )
                    .order_by("-created_at")
                )

                logger.info(f"Серий автора: {author_series.count()}")
            except Exception as e:
                logger.error(f"Ошибка загрузки серий автора: {e}")
                author_series = Series.objects.none()

            # Социальные ссылки
            try:
                social_links = author.get_social_links()
            except Exception as e:
                logger.error(f"Ошибка получения социальных ссылок: {e}")
                social_links = {}

            # Статистика автора
            try:
                # Считаем общее количество просмотров статей автора
                total_views = articles.aggregate(total=Sum("views_count"))["total"] or 0

                # Считаем общее количество реакций на статьи автора через Count
                article_ids = articles.values_list("id", flat=True)
                total_reactions = ArticleReaction.objects.filter(article_id__in=article_ids).count()

                logger.info(
                    f"Статистика автора: просмотры={total_views}, реакции={total_reactions}"
                )
            except Exception as e:
                logger.error(f"Ошибка расчета статистики автора: {e}")
                total_views = 0
                total_reactions = 0

            context.update(
                {
                    "articles": page_obj,
                    "author_series": author_series,
                    "categories_stats": categories_stats,
                    "popular_tags": popular_tags,
                    "social_links": social_links,
                    "total_views": total_views,
                    "total_reactions": total_reactions,
                    "page_title": f"{author.display_name} - Автор блога",
                    "meta_description": (
                        author.bio[:160] if author.bio else f"Статьи от {author.display_name}"
                    ),
                }
            )

            logger.info(f"Страница автора {author.display_name} загружена")
            return context

        except Exception as e:
            logger.error(f"Ошибка при загрузке страницы автора: {e}", exc_info=True)
            return super().get_context_data(**kwargs)


class CommentEditView(LoginRequiredMixin, View):
    """
    View для редактирования комментария пользователя.

    Требует аутентификации (LoginRequiredMixin).
    Проверяет права доступа - только автор может редактировать свой комментарий.
    """

    def post(self, request: Any, comment_id: int) -> Any:
        """
        Обрабатывает POST-запрос на редактирование комментария.

        Args:
            request: HTTP-запрос с полем content (новый текст комментария)
            comment_id: ID комментария для редактирования

        Returns:
            HttpResponseRedirect: Редирект на страницу статьи с якорем на комментарий
        """
        try:
            # Получение комментария
            try:
                comment = Comment.objects.select_related("article", "author").get(id=comment_id)
            except Comment.DoesNotExist:
                logger.warning(
                    f"Попытка редактирования несуществующего комментария ID={comment_id}"
                )
                messages.error(request, "Комментарий не найден.")
                return redirect("blog:home")

            # Проверка прав доступа
            if comment.author != request.user:
                logger.warning(
                    f"Попытка редактирования чужого комментария: "
                    f"пользователь={request.user.username}, автор={comment.author.username}, ID={comment_id}"
                )
                messages.error(request, "Вы не можете редактировать чужие комментарии.")
                return redirect(comment.article.get_absolute_url())

            # Валидация контента
            content = request.POST.get("content", "").strip()
            if not content:
                logger.warning(f"Попытка сохранения пустого комментария ID={comment_id}")
                messages.error(request, "Комментарий не может быть пустым.")
                return redirect(comment.article.get_absolute_url() + f"#comment-{comment.id}")

            if len(content) < 3:
                logger.warning(
                    f"Попытка сохранения слишком короткого комментария ID={comment_id} (длина={len(content)})"
                )
                messages.error(request, "Комментарий должен содержать минимум 3 символа.")
                return redirect(comment.article.get_absolute_url() + f"#comment-{comment.id}")

            if len(content) > 5000:
                logger.warning(
                    f"Попытка сохранения слишком длинного комментария ID={comment_id} (длина={len(content)})"
                )
                messages.error(request, "Комментарий слишком длинный (максимум 5000 символов).")
                return redirect(comment.article.get_absolute_url() + f"#comment-{comment.id}")

            # Сохранение изменений
            old_content = comment.content
            comment.content = content
            comment.save()

            logger.info(
                f"Комментарий отредактирован: ID={comment_id}, пользователь={request.user.username}, "
                f"статья={comment.article.slug}, старая длина={len(old_content)}, новая длина={len(content)}"
            )

            messages.success(request, "Комментарий успешно отредактирован!")
            return redirect(comment.article.get_absolute_url() + f"#comment-{comment.id}")

        except Exception as e:
            logger.error(
                f"Ошибка при редактировании комментария ID={comment_id}: {e}",
                exc_info=True,
            )
            messages.error(request, "Произошла ошибка при редактировании. Попробуйте позже.")
            return redirect("blog:home")


class CommentDeleteView(LoginRequiredMixin, View):
    """
    View для удаления комментария.

    Требует аутентификации (LoginRequiredMixin).
    Проверяет права доступа - автор или staff могут удалять комментарий.
    """

    def post(self, request: Any, comment_id: int) -> Any:
        """
        Обрабатывает POST-запрос на удаление комментария.

        Args:
            request: HTTP-запрос
            comment_id: ID комментария для удаления

        Returns:
            HttpResponseRedirect: Редирект на страницу статьи с якорем на секцию комментариев
        """
        try:
            # Получение комментария
            try:
                comment = Comment.objects.select_related("article", "author").get(id=comment_id)
            except Comment.DoesNotExist:
                logger.warning(f"Попытка удаления несуществующего комментария ID={comment_id}")
                messages.error(request, "Комментарий не найден.")
                return redirect("blog:home")

            # Проверка прав доступа
            if comment.author != request.user and not request.user.is_staff:
                logger.warning(
                    f"Попытка удаления чужого комментария: "
                    f"пользователь={request.user.username}, автор={comment.author.username}, "
                    f"ID={comment_id}, is_staff={request.user.is_staff}"
                )
                messages.error(request, "Вы не можете удалять чужие комментарии.")
                return redirect(comment.article.get_absolute_url())

            # Сохраняем данные для логирования до удаления
            article_url = comment.article.get_absolute_url()
            article_slug = comment.article.slug
            comment_author = comment.author.username
            has_replies = comment.replies.exists() if hasattr(comment, "replies") else False

            # Удаление комментария
            comment.delete()

            logger.info(
                f"Комментарий удалён: ID={comment_id}, удалил={request.user.username}, "
                f"автор был={comment_author}, статья={article_slug}, "
                f"был ответ={has_replies}"
            )

            messages.success(request, "Комментарий успешно удалён!")
            return redirect(article_url + "#comments")

        except Exception as e:
            logger.error(f"Ошибка при удалении комментария ID={comment_id}: {e}", exc_info=True)
            messages.error(request, "Произошла ошибка при удалении. Попробуйте позже.")
            return redirect("blog:home")
