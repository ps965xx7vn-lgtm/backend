"""
Management command для генерации sitemap.xml для блога.
"""

from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.utils import timezone

from blog.models import Article, Author, Category, Series


class Command(BaseCommand):
    help = "Генерирует sitemap.xml для блога"

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            type=str,
            default="sitemap.xml",
            help="Путь к выходному файлу (по умолчанию: sitemap.xml)",
        )

    def handle(self, *args, **options):
        output_file = options["output"]

        try:
            site = Site.objects.get_current()
            domain = f"https://{site.domain}"
        except Exception:
            domain = "https://pyschool.ge"
            self.stdout.write(self.style.WARNING(f"Site not configured, using default: {domain}"))

        urls = []
        now = timezone.now().strftime("%Y-%m-%d")

        # Главная страница блога
        urls.append(
            {"loc": f"{domain}/blog/", "lastmod": now, "changefreq": "daily", "priority": "1.0"}
        )

        # Опубликованные статьи
        articles = (
            Article.objects.filter(status="published")
            .select_related("category")
            .order_by("-published_at")
        )

        for article in articles:
            lastmod = article.updated_at.strftime("%Y-%m-%d") if article.updated_at else now
            urls.append(
                {
                    "loc": f"{domain}/blog/article/{article.slug}/",
                    "lastmod": lastmod,
                    "changefreq": "weekly",
                    "priority": "0.8",
                }
            )

        # Категории
        categories = Category.objects.all()
        for category in categories:
            urls.append(
                {
                    "loc": f"{domain}/blog/category/{category.slug}/",
                    "lastmod": now,
                    "changefreq": "daily",
                    "priority": "0.7",
                }
            )

        # Серии
        series = Series.objects.filter(status="active")
        for s in series:
            urls.append(
                {
                    "loc": f"{domain}/blog/series/{s.slug}/",
                    "lastmod": now,
                    "changefreq": "weekly",
                    "priority": "0.7",
                }
            )

        # Авторы
        authors = Author.objects.all()
        for author in authors:
            urls.append(
                {
                    "loc": f"{domain}/blog/author/{author.slug}/",
                    "lastmod": now,
                    "changefreq": "weekly",
                    "priority": "0.6",
                }
            )

        # Генерируем XML
        xml_content = self._generate_xml(urls)

        # Сохраняем файл
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(xml_content)

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully generated sitemap with {len(urls)} URLs to {output_file}"
            )
        )

    def _generate_xml(self, urls):
        """Генерирует XML контент sitemap."""
        xml = ['<?xml version="1.0" encoding="UTF-8"?>']
        xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

        for url in urls:
            xml.append("  <url>")
            xml.append(f"    <loc>{url['loc']}</loc>")
            xml.append(f"    <lastmod>{url['lastmod']}</lastmod>")
            xml.append(f"    <changefreq>{url['changefreq']}</changefreq>")
            xml.append(f"    <priority>{url['priority']}</priority>")
            xml.append("  </url>")

        xml.append("</urlset>")
        return "\n".join(xml)
