"""
Management команда для наполнения всех данных сайта одной командой.

Использование:
    python manage.py populate_all_data
    python manage.py populate_all_data --clear  # Очистить старые данные
"""

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Наполняет все данные сайта: роли, курсы, блог"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Очистить существующие данные перед созданием",
        )

    def handle(self, *args, **options):
        """Запускает все команды наполнения данных"""

        self.stdout.write(self.style.HTTP_INFO("=" * 70))
        self.stdout.write(self.style.HTTP_INFO("  НАПОЛНЕНИЕ БАЗЫ ДАННЫХ PYLAND"))
        self.stdout.write(self.style.HTTP_INFO("=" * 70))
        self.stdout.write("")

        # 1. Создаем роли
        self.stdout.write(self.style.HTTP_INFO("📋 ШАГ 1/4: Создание ролей пользователей"))
        self.stdout.write(self.style.HTTP_INFO("-" * 70))
        call_command("create_roles")

        self.stdout.write("")
        self.stdout.write("")

        # 2. Создаем курсы
        self.stdout.write(self.style.HTTP_INFO("📚 ШАГ 2/4: Создание курсов"))
        self.stdout.write(self.style.HTTP_INFO("-" * 70))
        if options["clear"]:
            call_command("populate_courses_data", "--clear")
        else:
            call_command("populate_courses_data")

        self.stdout.write("")
        self.stdout.write("")

        # 3. Создаем уроки и шаги
        self.stdout.write(self.style.HTTP_INFO("📖 ШАГ 3/4: Создание уроков и шагов"))
        self.stdout.write(self.style.HTTP_INFO("-" * 70))
        if options["clear"]:
            call_command("populate_lessons_data", "--clear")
        else:
            call_command("populate_lessons_data")

        self.stdout.write("")
        self.stdout.write("")

        # 4. Создаем статьи блога
        self.stdout.write(self.style.HTTP_INFO("📝 ШАГ 4/4: Создание статей блога"))
        self.stdout.write(self.style.HTTP_INFO("-" * 70))
        if options["clear"]:
            call_command("populate_blog_data", "--clear")
        else:
            call_command("populate_blog_data")

        self.stdout.write("")
        self.stdout.write("")
        self.stdout.write(self.style.HTTP_INFO("=" * 70))
        self.stdout.write(self.style.SUCCESS("✅ ВСЕ ДАННЫЕ УСПЕШНО СОЗДАНЫ!"))
        self.stdout.write(self.style.HTTP_INFO("=" * 70))
        self.stdout.write("")
        self.stdout.write(self.style.NOTICE("Теперь вы можете:"))
        self.stdout.write("  • Просмотреть курсы с уроками и шагами на сайте")
        self.stdout.write("  • Прочитать статьи блога")
        self.stdout.write("  • Назначить роли пользователям в админке")
        self.stdout.write("")
