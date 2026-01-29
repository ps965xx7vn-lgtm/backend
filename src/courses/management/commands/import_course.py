"""
Management-команда для импорта курса из JSON файла с переводами.

Использование:
    poetry run python manage.py import_course docs/examples/git_github_course.json
"""

import json
import logging
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.template.defaultfilters import slugify

from courses.models import Course, ExtraSource, Lesson, Step, Tip

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Импортирует курс из JSON файла с поддержкой переводов."""

    help = "Import course from JSON file with translations (ru, en, ka)"

    def add_arguments(self, parser):
        parser.add_argument("json_file", type=str, help="Path to JSON file with course data")
        parser.add_argument(
            "--update",
            action="store_true",
            help="Update existing course by slug instead of creating new one",
        )

    def handle(self, *args, **options):
        json_file = options["json_file"]
        update_mode = options.get("update", False)

        # Проверка существования файла
        json_path = Path(json_file)
        if not json_path.exists():
            raise CommandError(f"❌ File not found: {json_file}")

        try:
            # Загрузка JSON
            with open(json_path, encoding="utf-8") as f:
                data = json.load(f)

            self.stdout.write("📚 Starting course import...")

            # Валидация структуры
            if "ru" not in data:
                raise CommandError("❌ Missing 'ru' (Russian) data in JSON")

            ru_data = data["ru"]
            required_fields = ["name", "category", "status"]
            for field in required_fields:
                if field not in ru_data:
                    raise CommandError(f"❌ Missing required field: {field}")

            # Импорт курса в транзакции
            with transaction.atomic():
                course = self._import_course(data, update_mode)

            # Успешное завершение
            stats = self._get_stats(course)
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n✅ Course imported successfully!\n"
                    f"   ID: {course.id}\n"
                    f"   Name: {course.name}\n"
                    f"   Slug: {course.slug}\n"
                    f"   Lessons: {stats['lessons']}\n"
                    f"   Steps: {stats['steps']}\n"
                    f"   Tips: {stats['tips']}\n"
                    f"   Extra Sources: {stats['extra_sources']}\n"
                    f"\n🌍 Translations:\n"
                    f"   RU: ✅ Full\n"
                    f"   EN: {'✅' if data.get('en') else '❌'} {self._get_lang_completeness(course, 'en')}\n"
                    f"   KA: {'✅' if data.get('ka') else '❌'} {self._get_lang_completeness(course, 'ka')}\n"
                )
            )

        except json.JSONDecodeError as e:
            raise CommandError(f"❌ Invalid JSON format: {e}")
        except Exception as e:
            logger.exception("Course import failed")
            raise CommandError(f"❌ Import failed: {e}")

    def _import_course(self, data: dict, update_mode: bool) -> Course:
        """Импортирует курс и все связанные данные."""
        ru_data = data["ru"]

        # Создание курса с переводами сразу
        if update_mode:
            raise CommandError("Update mode not implemented yet")

        course = Course(
            name_ru=ru_data["name"],
            description_ru=ru_data.get("description", ""),
            short_description_ru=ru_data.get("short_description", ""),
            category=ru_data["category"],
            price=ru_data.get("price", 0),
            status=ru_data["status"],
        )

        # Добавляем переводы до сохранения
        if "en" in data:
            en_data = data["en"]
            course.name_en = en_data.get("name")
            course.description_en = en_data.get("description", "")
            course.short_description_en = en_data.get("short_description", "")

        if "ka" in data:
            ka_data = data["ka"]
            course.name_ka = ka_data.get("name")
            course.description_ka = ka_data.get("description", "")
            course.short_description_ka = ka_data.get("short_description", "")

        course.save()
        self.stdout.write(f"  📖 Created course: {course.name}")

        # Импорт уроков
        ru_lessons = ru_data.get("lessons", [])
        en_lessons = data.get("en", {}).get("lessons", [])
        ka_lessons = data.get("ka", {}).get("lessons", [])

        for idx, ru_lesson_data in enumerate(ru_lessons):
            # Создаём урок с русскими данными
            lesson = Lesson(
                course=course,
                name_ru=ru_lesson_data["name"],
                short_description_ru=ru_lesson_data.get("short_description", ""),
            )

            # Добавляем переводы до сохранения
            if idx < len(en_lessons):
                lesson.name_en = en_lessons[idx].get("name")
                lesson.short_description_en = en_lessons[idx].get("short_description", "")

            if idx < len(ka_lessons):
                lesson.name_ka = ka_lessons[idx].get("name")
                lesson.short_description_ka = ka_lessons[idx].get("short_description", "")

            # Manually set lesson_number to avoid auto-generation conflicts
            lesson.lesson_number = idx + 1
            # Generate unique slug with lesson number to avoid conflicts
            base_slug = slugify(ru_lesson_data["name"])
            lesson.slug = f"{base_slug}-{lesson.lesson_number}"
            super(Lesson, lesson).save()  # Bypass custom save() method
            self.stdout.write(f"    📝 Created lesson {lesson.lesson_number}: {lesson.name}")

            # Импортируем шаги для этого урока
            ru_steps = ru_lesson_data.get("steps", [])
            en_steps = en_lessons[idx].get("steps", []) if idx < len(en_lessons) else []
            ka_steps = ka_lessons[idx].get("steps", []) if idx < len(ka_lessons) else []

            for step_idx, ru_step_data in enumerate(ru_steps):
                # Создаём step БЕЗ вызова save() чтобы обойти автоматическую генерацию step_number
                step = Step(
                    lesson=lesson,
                    name_ru=ru_step_data["name"],
                    description_ru=ru_step_data.get("description", ""),
                    actions_ru=ru_step_data.get("actions", ""),
                    self_check_ru=ru_step_data.get("self_check", ""),
                    self_check_items=ru_step_data.get(
                        "self_check_items"
                    ),  # Чекбоксы (не переводится)
                    troubleshooting_help_ru=ru_step_data.get(
                        "troubleshooting_help", ""
                    ),  # Помощь студентам
                    repair_description_ru=ru_step_data.get("repair_description", ""),  # Админ-поле
                    step_number=step_idx + 1,  # Устанавливаем вручную
                )

                # Добавляем переводы
                if step_idx < len(en_steps):
                    step.name_en = en_steps[step_idx].get("name")
                    step.description_en = en_steps[step_idx].get("description", "")
                    step.actions_en = en_steps[step_idx].get("actions", "")
                    step.self_check_en = en_steps[step_idx].get("self_check", "")
                    step.troubleshooting_help_en = en_steps[step_idx].get(
                        "troubleshooting_help", ""
                    )
                    step.repair_description_en = en_steps[step_idx].get("repair_description", "")

                if step_idx < len(ka_steps):
                    step.name_ka = ka_steps[step_idx].get("name")
                    step.description_ka = ka_steps[step_idx].get("description", "")
                    step.actions_ka = ka_steps[step_idx].get("actions", "")
                    step.self_check_ka = ka_steps[step_idx].get("self_check", "")
                    step.troubleshooting_help_ka = ka_steps[step_idx].get(
                        "troubleshooting_help", ""
                    )
                    step.repair_description_ka = ka_steps[step_idx].get("repair_description", "")

                # Принудительно сохраняем без вызова кастомной логики save()
                super(Step, step).save()
                self.stdout.write(f"      🔹 Created step {step.step_number}: {step.name}")

        return course

    def _get_stats(self, course: Course) -> dict:
        """Возвращает статистику по курсу."""
        lessons = course.lessons.all()
        steps = Step.objects.filter(lesson__course=course)
        tips = Tip.objects.filter(step__lesson__course=course)
        extra_sources = ExtraSource.objects.filter(steps__lesson__course=course).distinct()

        return {
            "lessons": lessons.count(),
            "steps": steps.count(),
            "tips": tips.count(),
            "extra_sources": extra_sources.count(),
        }

    def _get_lang_completeness(self, course: Course, lang_code: str) -> str:
        """Проверяет полноту перевода для языка."""
        name_field = f"name_{lang_code}"
        if not getattr(course, name_field):
            return "No translation"

        lessons = course.lessons.all()
        translated_lessons = sum(1 for l in lessons if getattr(l, name_field))

        steps = Step.objects.filter(lesson__course=course)
        translated_steps = sum(1 for s in steps if getattr(s, name_field))

        if not lessons.count() or not steps.count():
            return "Partial"

        lesson_percent = (translated_lessons / lessons.count()) * 100
        step_percent = (translated_steps / steps.count()) * 100

        if lesson_percent == 100 and step_percent == 100:
            return "Complete"
        elif lesson_percent > 50 and step_percent > 50:
            return f"Partial ({int((lesson_percent + step_percent) / 2)}%)"
        else:
            return "Minimal"
