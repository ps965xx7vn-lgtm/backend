"""
Management command для создания тестовых пользователей.

Usage:
    python manage.py create_test_users
    python manage.py create_test_users --count 10

Создает тестовых пользователей для разработки и тестирования:
    - Один пользователь каждой роли с предсказуемыми данными
    - Опционально: дополнительные студенты

Credentials:
    - student@test.com / password123
    - mentor@test.com / password123
    - reviewer@test.com / password123
    - manager@test.com / password123
    - admin@test.com / password123
    - support@test.com / password123
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from authentication.models import Role

User = get_user_model()


class Command(BaseCommand):
    """Создает тестовых пользователей для разработки."""

    help = "Создает тестовых пользователей с разными ролями для разработки и тестирования"

    def add_arguments(self, parser):
        """Добавляет аргументы команды."""
        parser.add_argument(
            "--count",
            type=int,
            default=0,
            help="Количество дополнительных студентов для создания (по умолчанию: 0)",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Удалить существующих тестовых пользователей перед созданием",
        )

    def handle(self, *args, **options):
        """
        Основной метод команды.

        Args:
            count: Количество дополнительных студентов
            clear: Флаг удаления существующих тестовых пользователей
        """
        count = options["count"]
        clear = options["clear"]

        # Проверяем что роли существуют
        if Role.objects.count() < 6:
            raise CommandError("Сначала создайте роли командой: python manage.py create_roles")

        # Удаляем существующих если нужно
        if clear:
            deleted_count = User.objects.filter(email__endswith="@test.com").delete()[0]
            self.stdout.write(
                self.style.WARNING(f"Удалено тестовых пользователей: {deleted_count}")
            )

        created_count = 0
        skipped_count = 0

        # Данные для базовых тестовых пользователей
        test_users = [
            {
                "email": "student@test.com",
                "first_name": "Test",
                "last_name": "Student",
                "role": "student",
            },
            {
                "email": "mentor@test.com",
                "first_name": "Test",
                "last_name": "Mentor",
                "role": "mentor",
            },
            {
                "email": "reviewer@test.com",
                "first_name": "Test",
                "last_name": "Reviewer",
                "role": "reviewer",
            },
            {
                "email": "manager@test.com",
                "first_name": "Test",
                "last_name": "Manager",
                "role": "manager",
                "is_staff": True,
            },
            {
                "email": "admin@test.com",
                "first_name": "Test",
                "last_name": "Admin",
                "role": "admin",
                "is_staff": True,
                "is_superuser": True,
            },
            {
                "email": "support@test.com",
                "first_name": "Test",
                "last_name": "Support",
                "role": "support",
            },
        ]

        with transaction.atomic():
            # Создаем базовых пользователей
            for user_data in test_users:
                role_name = user_data.pop("role")

                if User.objects.filter(email=user_data["email"]).exists():
                    skipped_count += 1
                    self.stdout.write(
                        self.style.WARNING(f"○ Пользователь уже существует: {user_data['email']}")
                    )
                    continue

                # Получаем роль
                role = Role.objects.get(name=role_name)

                user = User.objects.create_user(
                    password="password123",
                    is_active=True,
                    email_is_verified=True,
                    role=role,
                    **user_data,
                )

                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Создан пользователь: {user.email} (роль: {role_name})")
                )

            # Создаем дополнительных студентов если нужно
            if count > 0:
                student_role = Role.objects.get(name="student")

                for i in range(1, count + 1):
                    email = f"student{i}@test.com"

                    if User.objects.filter(email=email).exists():
                        skipped_count += 1
                        continue

                    user = User.objects.create_user(
                        email=email,
                        password="password123",
                        first_name="Student",
                        last_name=f"#{i}",
                        is_active=True,
                        email_is_verified=True,
                        role=student_role,
                    )

                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f"✓ Создан студент: {email}"))

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("━" * 60))
        self.stdout.write(self.style.SUCCESS("✓ Команда выполнена успешно!"))
        self.stdout.write(self.style.SUCCESS(f"  Создано пользователей: {created_count}"))
        if skipped_count > 0:
            self.stdout.write(self.style.WARNING(f"  Пропущено (уже существуют): {skipped_count}"))
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Credentials для входа:"))
        self.stdout.write(self.style.SUCCESS("  Email: [role]@test.com"))
        self.stdout.write(self.style.SUCCESS("  Password: password123"))
        self.stdout.write(self.style.SUCCESS("━" * 60))
