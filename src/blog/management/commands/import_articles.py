"""
Management-команда для импорта статей из markdown файлов.

Использование:
    poetry run python src/manage.py import_articles src/blog/docs/articles/python-course/
"""

import logging
import re
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify

from authentication.models import User
from blog.models import Article, Author, Category

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Импортирует статьи из markdown файлов."""

    help = "Import articles from markdown files in a directory"

    def add_arguments(self, parser):
        parser.add_argument(
            "directory",
            type=str,
            help="Path to directory with markdown files",
        )
        parser.add_argument(
            "--update",
            action="store_true",
            help="Update existing articles by slug instead of creating new ones",
        )
        parser.add_argument(
            "--author-email",
            type=str,
            default="admin@pyschool.ru",
            help="Email of the article author (default: admin@pyschool.ru)",
        )
        parser.add_argument(
            "--category",
            type=str,
            default="python",
            help="Category slug for articles (default: python)",
        )
        parser.add_argument(
            "--status",
            type=str,
            default="published",
            choices=["draft", "published", "archived"],
            help="Article status (default: published)",
        )

    def handle(self, *args, **options):
        directory = options["directory"]
        update_mode = options.get("update", False)
        author_email = options["author_email"]
        category_slug = options["category"]
        status = options["status"]

        # Проверка существования директории
        dir_path = Path(directory)
        if not dir_path.exists() or not dir_path.is_dir():
            raise CommandError(f"❌ Directory not found: {directory}")

        # Получаем автора
        try:
            author_user = User.objects.get(email=author_email)
        except User.DoesNotExist as e:
            raise CommandError(
                f"❌ User with email {author_email} not found. "
                f"Create user first or use --author-email option."
            ) from e

        # Получаем или создаём профиль автора блога
        blog_author, created = Author.objects.get_or_create(
            user=author_user,
            defaults={
                "display_name": author_user.get_full_name() or author_user.username,
                "slug": author_user.username or f"author-{author_user.id}",
                "bio": "Автор статей на Pyland",
            },
        )

        # Если автор существовал, но у него не было slug - добавляем
        if not created and not blog_author.slug:
            blog_author.slug = author_user.username or f"author-{author_user.id}"
            blog_author.save()

        # Получаем категорию
        try:
            category = Category.objects.get(slug=category_slug)
        except Category.DoesNotExist:
            # Создаём категорию если не существует
            category = Category.objects.create(
                name=category_slug.title(),
                slug=category_slug,
                description=f"Статьи о {category_slug}",
            )
            self.stdout.write(self.style.WARNING(f"⚠ Created new category: {category.name}"))

        # Ищем все markdown файлы
        md_files = list(dir_path.glob("*.md"))
        if not md_files:
            raise CommandError(f"❌ No markdown files found in {directory}")

        self.stdout.write(f"\n📚 Found {len(md_files)} markdown files")
        self.stdout.write(f"👤 Author: {author_user.email}")
        self.stdout.write(f"📁 Category: {category.name}")
        self.stdout.write(f"📊 Status: {status}\n")

        imported_count = 0
        updated_count = 0
        skipped_count = 0

        for md_file in md_files:
            self.stdout.write(f"Processing: {md_file.name}...")

            try:
                with transaction.atomic():
                    result = self._import_article(
                        md_file,
                        author_user,
                        blog_author,
                        category,
                        status,
                        update_mode,
                    )

                    if result == "created":
                        imported_count += 1
                        self.stdout.write(self.style.SUCCESS("  ✅ Created"))
                    elif result == "updated":
                        updated_count += 1
                        self.stdout.write(self.style.SUCCESS("  ✅ Updated"))
                    elif result == "skipped":
                        skipped_count += 1
                        self.stdout.write(self.style.WARNING("  ⏭️  Skipped (already exists)"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ❌ Error: {e}"))
                logger.error(f"Error importing {md_file.name}: {e}", exc_info=True)

        # Итоговая статистика
        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ Import completed!\n"
                f"   Created: {imported_count}\n"
                f"   Updated: {updated_count}\n"
                f"   Skipped: {skipped_count}\n"
                f"   Total: {len(md_files)}"
            )
        )

    def _import_article(
        self,
        md_file: Path,
        author: User,
        blog_author: Author,
        category: Category,
        status: str,
        update_mode: bool,
    ) -> str:
        """Импортирует одну статью из markdown файла."""

        # Читаем содержимое файла
        with open(md_file, encoding="utf-8") as f:
            content = f.read()

        # Парсим frontmatter и контент
        title, excerpt, tags, difficulty, parsed_content = self._parse_markdown(
            content, md_file.stem
        )

        # Генерируем slug из названия файла или заголовка
        slug = slugify(md_file.stem)

        # Проверяем существование статьи
        existing_article = Article.objects.filter(slug=slug).first()

        if existing_article and not update_mode:
            return "skipped"

        # Данные для создания/обновления
        article_data = {
            "title": title,
            "content": parsed_content,
            "excerpt": excerpt,
            "author": author,
            "blog_author": blog_author,
            "category": category,
            "status": status,
            "difficulty": difficulty,
        }

        if existing_article:
            # Обновляем существующую статью
            for key, value in article_data.items():
                setattr(existing_article, key, value)
            existing_article.save()

            # Обновляем теги
            if tags:
                existing_article.tags.set(*tags)

            return "updated"
        else:
            # Создаём новую статью
            article = Article.objects.create(slug=slug, **article_data)

            # Добавляем теги
            if tags:
                article.tags.add(*tags)

            return "created"

    def _parse_markdown(self, content: str, filename: str) -> tuple:
        """
        Парсит markdown файл и извлекает метаданные.

        Returns:
            tuple: (title, excerpt, tags, difficulty, content)
        """

        # Пытаемся извлечь заголовок из первой строки вида # Title
        title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        if title_match:
            title = title_match.group(1).strip()
            # Удаляем заголовок из контента
            content = content[title_match.end() :].strip()
        else:
            # Если нет заголовка, используем имя файла
            title = filename.replace("-", " ").replace("_", " ").title()

        # Извлекаем первый параграф как excerpt
        paragraphs = [
            p.strip() for p in content.split("\n\n") if p.strip() and not p.startswith("#")
        ]
        # Очищаем от markdown разметки в excerpt
        excerpt = ""
        if paragraphs:
            excerpt = re.sub(r"[*_`#]", "", paragraphs[0])
            excerpt = excerpt[:500]  # Ограничиваем до 500 символов

        # Определяем теги из имени файла
        tags = []
        if "python" in filename.lower():
            tags.append("python")
        if "function" in filename.lower():
            tags.append("functions")
        if "loop" in filename.lower():
            tags.append("loops")
        if "if" in filename.lower() or "condition" in filename.lower():
            tags.append("conditions")
        if "list" in filename.lower() or "dict" in filename.lower():
            tags.append("data structures")
        if "codehs" in filename.lower():
            tags.append("codehs")
            tags.append("online ide")
        if "logical" in filename.lower() or "operator" in filename.lower():
            tags.append("operators")
        if "basics" in filename.lower():
            tags.append("basics")

        # Определяем сложность
        difficulty = "beginner"
        if "advanced" in filename.lower() or "expert" in filename.lower():
            difficulty = "advanced"
        elif "intermediate" in filename.lower():
            difficulty = "intermediate"

        return title, excerpt, tags, difficulty, content
