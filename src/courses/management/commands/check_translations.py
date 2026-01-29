"""
Management команда для проверки покрытия переводов.

Использование:
    python manage.py check_translations

Пример вывода:
    Course:
      ru: 15/15 (100.0%)
      en: 10/15 (66.7%)
      ka: 5/15 (33.3%)
"""

from django.core.management.base import BaseCommand
from django.db.models import Q

from courses.models import Course, Lesson, Step


class Command(BaseCommand):
    """
    Проверяет покрытие переводов для моделей курсов.
    """

    help = "Проверка покрытия переводов для курсов"

    def add_arguments(self, parser):
        parser.add_argument(
            "--detailed",
            action="store_true",
            help="Показать детальную информацию по каждому объекту",
        )

    def handle(self, *args, **options):
        detailed = options.get("detailed", False)
        languages = ["ru", "en", "ka"]
        language_names = {
            "ru": "Русский",
            "en": "English",
            "ka": "ქართული",
        }
        models = [
            (Course, "Курсы"),
            (Lesson, "Уроки"),
            (Step, "Шаги"),
        ]

        self.stdout.write(self.style.SUCCESS("\n=== Проверка переводов ===\n"))

        for model, model_name in models:
            self.stdout.write(self.style.HTTP_INFO(f"\n{model_name}:"))

            total = model.objects.count()

            if total == 0:
                self.stdout.write("  Нет объектов для проверки")
                continue

            for lang in languages:
                # Подсчет объектов с заполненным name для языка
                field_name = f"name_{lang}"
                translated = model.objects.exclude(
                    Q(**{field_name: ""}) | Q(**{field_name: None})
                ).count()

                percentage = (translated / total * 100) if total > 0 else 0

                # Цветной вывод в зависимости от процента
                if percentage == 100:
                    style = self.style.SUCCESS
                elif percentage >= 50:
                    style = self.style.WARNING
                else:
                    style = self.style.ERROR

                self.stdout.write(
                    f"  {language_names[lang]:10} [{lang}]: "
                    + style(f"{translated}/{total} ({percentage:.1f}%)")
                )

                # Детальный вывод
                if detailed and percentage < 100:
                    missing = model.objects.filter(Q(**{field_name: ""}) | Q(**{field_name: None}))

                    if missing.exists():
                        self.stdout.write("    Не переведены:")
                        for obj in missing[:5]:  # Показать первые 5
                            self.stdout.write(f"      - {obj}")
                        if missing.count() > 5:
                            self.stdout.write(f"      ... и ещё {missing.count() - 5}")

        self.stdout.write(self.style.SUCCESS("\n=== Проверка завершена ===\n"))
