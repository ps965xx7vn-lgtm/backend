"""
Celery tasks для блога.
"""

import logging

from celery import shared_task
from django.core.cache import cache

from blog.cache_utils import get_cache_key, warm_cache
from blog.models import Article

logger = logging.getLogger(__name__)


@shared_task(name="blog.warm_cache")
def warm_cache_task():
    """
    Периодическая задача для прогрева кеша.
    Запускается каждые 5 минут.
    """
    try:
        warm_cache()
        logger.info("Cache warmed successfully")
        return "Cache warmed"
    except Exception as e:
        logger.error(f"Error warming cache: {e}")
        return f"Error: {str(e)}"


@shared_task(name="blog.update_article_views")
def update_article_views(article_id, increment=1):
    """
    Асинхронное обновление счетчика просмотров статьи.

    Args:
        article_id: ID статьи
        increment: На сколько увеличить счетчик (по умолчанию 1)
    """
    try:
        article = Article.objects.get(id=article_id)
        article.views_count += increment
        article.save(update_fields=["views_count"])

        # Инвалидируем кеш статьи
        cache.delete_pattern(f"blog:article_detail:*{article.slug}*")
        cache.delete_pattern("blog:popular_articles:*")

        logger.info(f"Updated views for article {article.slug}: +{increment}")
        return f"Views updated: {article.views_count}"
    except Article.DoesNotExist:
        logger.warning(f"Article {article_id} not found")
        return "Article not found"
    except Exception as e:
        logger.error(f"Error updating article views: {e}")
        return f"Error: {str(e)}"


@shared_task(name="blog.cleanup_old_cache")
def cleanup_old_cache():
    """
    Очистка старого кеша.
    Запускается раз в день.
    """
    try:
        # Очищаем устаревшие данные
        cache.delete_pattern("blog:article_list:*")
        cache.delete_pattern("blog:stats:*")

        logger.info("Old cache cleaned up")
        return "Cache cleaned"
    except Exception as e:
        logger.error(f"Error cleaning cache: {e}")
        return f"Error: {str(e)}"


@shared_task(name="blog.generate_sitemap")
def generate_sitemap_task():
    """
    Генерация sitemap.xml.
    Запускается раз в день.
    """
    try:
        from django.core.management import call_command

        call_command("generate_sitemap")

        logger.info("Sitemap generated successfully")
        return "Sitemap generated"
    except Exception as e:
        logger.error(f"Error generating sitemap: {e}")
        return f"Error: {str(e)}"


@shared_task(name="blog.update_popular_articles")
def update_popular_articles():
    """
    Обновление списка популярных статей в кеше.
    Запускается каждый час.
    """
    try:
        popular = (
            Article.objects.filter(status="published")
            .select_related("author", "category")
            .order_by("-views_count")[:20]
        )

        cache_key = get_cache_key("popular_articles", "top20")
        try:
            cache.set(cache_key, list(popular), 3600)  # 1 час
        except Exception as e:
            logger.warning(f"Error writing to cache {cache_key}: {e}")

        logger.info(f"Updated popular articles cache: {popular.count()} articles")
        return f"Popular articles updated: {popular.count()}"
    except Exception as e:
        logger.error(f"Error updating popular articles: {e}")
        return f"Error: {str(e)}"
