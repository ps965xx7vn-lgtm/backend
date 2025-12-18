"""
Management command для создания ролей пользователей.

Usage:
    python manage.py create_roles

Создает 6 базовых ролей:
    - student: Студент (по умолчанию для новых пользователей)
    - mentor: Ментор (помогает студентам)
    - reviewer: Ревьюер (проверяет работы)
    - manager: Менеджер (управление платформой)
    - admin: Администратор (полный доступ)
    - support: Поддержка (помощь пользователям)
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from authentication.models import Role


class Command(BaseCommand):
    """Создает базовые роли пользователей в системе."""

    help = "Создает базовые роли пользователей: student, mentor, reviewer, manager, admin, support"

    def handle(self, *args, **options):
        """
        Основной метод команды.

        Создает все 6 ролей если их еще нет.
        Использует транзакцию для атомарности операции.
        """
        roles_data = [
            ("student", "Студент", "Обучается на платформе, проходит курсы и выполняет задания"),
            ("mentor", "Ментор", "Помогает студентам, отвечает на вопросы, проводит консультации"),
            ("reviewer", "Ревьюер", "Проверяет работы студентов, оставляет комментарии и оценки"),
            ("manager", "Менеджер", "Управляет платформой, курсами и пользователями"),
            ("admin", "Администратор", "Полный доступ ко всем функциям платформы"),
            ("support", "Поддержка", "Помогает пользователям решать проблемы"),
        ]

        created_count = 0
        existing_count = 0

        with transaction.atomic():
            for name, description, _ in roles_data:
                role, created = Role.objects.get_or_create(
                    name=name,
                    defaults={
                        "description": description,
                    },
                )

                if created:
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f"✓ Создана роль: {name} ({description})"))
                else:
                    existing_count += 1
                    self.stdout.write(self.style.WARNING(f"○ Роль уже существует: {name}"))

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("━" * 60))
        self.stdout.write(self.style.SUCCESS("✓ Команда выполнена успешно!"))
        self.stdout.write(self.style.SUCCESS(f"  Создано ролей: {created_count}"))
        self.stdout.write(self.style.SUCCESS(f"  Уже существовало: {existing_count}"))
        self.stdout.write(self.style.SUCCESS(f"  Всего ролей: {created_count + existing_count}"))
        self.stdout.write(self.style.SUCCESS("━" * 60))
