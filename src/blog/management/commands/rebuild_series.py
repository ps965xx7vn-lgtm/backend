from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db.models import Count, Q
from django.utils import timezone

from blog.models import Article, Category, Series

User = get_user_model()


class Command(BaseCommand):
    help = "Delete old/empty series and create logical series by category and popular tags."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run", action="store_true", help="Only show actions without applying changes"
        )
        parser.add_argument(
            "--min-per-category",
            type=int,
            default=3,
            help="Minimum published articles in a category to create a series",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        min_per_category = options["min_per_category"]

        self.stdout.write("Rebuild series started")

        # 1) Delete empty series (no published articles)
        empty_series_qs = Series.objects.annotate(
            pub_count=Count("articles", filter=Q(articles__status="published"))
        ).filter(pub_count=0)

        empty_count = empty_series_qs.count()
        self.stdout.write(f"Found {empty_count} empty series to delete")
        if not dry_run and empty_count:
            empty_series_qs.delete()
            self.stdout.write(f"Deleted {empty_count} empty series")

        # 2) Create series for popular categories
        categories = Category.objects.annotate(
            pub_count=Count("articles", filter=Q(articles__status="published"))
        ).filter(pub_count__gte=min_per_category)

        default_author = User.objects.filter(is_superuser=True).first() or User.objects.first()
        if not default_author:
            self.stdout.write(
                self.style.ERROR("No user found to assign as series author. Aborting.")
            )
            return

        created_series = 0
        updated_series = 0

        for cat in categories:
            title = f"Лучшее в {cat.name}"
            description = f"Подборка статей по теме {cat.name} — актуальные материалы и практические руководства."
            series, created = Series.objects.get_or_create(
                title=title,
                defaults={
                    "description": description,
                    "slug": title.lower().replace(" ", "-"),
                    "author": default_author,
                },
            )

            # привязываем статьи к серии (топ по дате, до 10 штук)
            articles_qs = Article.objects.filter(
                status="published", category=cat, published_at__lte=timezone.now()
            ).order_by("-published_at")[:10]

            if articles_qs.exists():
                for idx, art in enumerate(articles_qs, start=1):
                    if not dry_run:
                        art.series = series
                        art.series_order = idx
                        art.save(update_fields=["series", "series_order"])
                if created:
                    created_series += 1
                else:
                    updated_series += 1

        self.stdout.write(
            f"Categories processed. Created series: {created_series}, updated: {updated_series}"
        )

        # 3) Create some curated series by matching article titles (example)
        curated = [
            {
                "title": "DevOps на практике",
                "description": "Контейнеризация, Docker, CI/CD и практические кейсы",
                "match_titles": ["Docker для разработчиков: Контейнеризация приложений"],
            },
            {
                "title": "Python: основы и больше",
                "description": "Серия для углублённого изучения Python",
                "match_titles": ["Основы Python: Начало пути в программирование"],
            },
        ]

        for s in curated:
            series, created = Series.objects.get_or_create(
                title=s["title"],
                defaults={
                    "description": s["description"],
                    "slug": s["title"].lower().replace(" ", "-"),
                    "author": default_author,
                },
            )
            # attach matching articles
            for idx, t in enumerate(s.get("match_titles", []), start=1):
                try:
                    art = Article.objects.get(title=t)
                    if not dry_run:
                        art.series = series
                        art.series_order = idx
                        art.save(update_fields=["series", "series_order"])
                except Article.DoesNotExist:
                    self.stdout.write(f"  Article not found: {t}")

    self.stdout.write(self.style.SUCCESS("Rebuild series finished"))
