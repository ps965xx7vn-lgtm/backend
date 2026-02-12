"""
Management команда для создания базовых ролей в системе.

Использование:
    python manage.py create_roles

Создает все роли из Role.RoleChoices если они еще не существуют.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from authentication.models import Role


class Command(BaseCommand):
    """Команда для создания базовых ролей в системе."""

    help = "Создает базовые роли пользователей в системе"

    def handle(self, *args, **options):
        """
        Создает роли из Role.get_default_roles().

        Raises:
            CommandError: При ошибках создания ролей
        """
        self.stdout.write(self.style.MIGRATE_HEADING("🔐 Создание базовых ролей..."))

        default_roles = Role.get_default_roles()
        created_count = 0
        existing_count = 0

        try:
            with transaction.atomic():
                for role_name, description in default_roles.items():
                    role, created = Role.objects.get_or_create(
                        name=role_name,
                        defaults={"description": description},
                    )

                    if created:
                        created_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f"✓ Создана роль: {role.get_name_display()}")
                        )
                    else:
                        existing_count += 1
                        self.stdout.write(
                            self.style.WARNING(f"⚠ Роль уже существует: {role.get_name_display()}")
                        )

            # Итоговая статистика
            self.stdout.write("")
            self.stdout.write(self.style.MIGRATE_HEADING("📊 Статистика:"))
            self.stdout.write(f"   Создано новых ролей: {created_count}")
            self.stdout.write(f"   Уже существовало: {existing_count}")
            self.stdout.write(f"   Всего ролей: {Role.objects.count()}")
            self.stdout.write("")

            if created_count > 0:
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Успешно создано {created_count} роле(й)!")
                )
            else:
                self.stdout.write(self.style.SUCCESS("✅ Все роли уже существуют в системе!"))

        except Exception as e:
            raise CommandError(f"❌ Ошибка при создании ролей: {e}") from e
