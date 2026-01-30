"""
Management команда для создания суперадмина с предустановленными данными.

Создаёт суперпользователя с email a@mail.ru и паролем 'a'.
Используется для быстрого развёртывания и разработки.
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from loguru import logger

User = get_user_model()


class Command(BaseCommand):
    """
    Команда для создания суперадмина с фиксированными данными.

    Usage:
        python manage.py create_superadmin
    """

    help = "Создаёт суперадмина с email a@mail.ru и паролем 'a'"

    def add_arguments(self, parser):
        """Добавление аргументов командной строки."""
        parser.add_argument(
            "--delete-existing",
            action="store_true",
            help="Удалить существующего пользователя с таким email перед созданием",
        )

    def handle(self, *args, **options):
        """Основная логика команды."""
        email = "a@mail.ru"
        password = "a"
        delete_existing = options.get("delete_existing", False)

        try:
            # Проверяем существование пользователя
            if User.objects.filter(email=email).exists():
                if delete_existing:
                    User.objects.filter(email=email).delete()
                    self.stdout.write(
                        self.style.WARNING(f"⚠️  Существующий пользователь {email} удалён")
                    )
                    logger.info(f"Удалён существующий пользователь: {email}")
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f"❌ Пользователь с email {email} уже существует!\n"
                            f"   Используйте флаг --delete-existing для пересоздания"
                        )
                    )
                    logger.warning(f"Попытка создать существующего пользователя: {email}")
                    return

            # Создаём суперпользователя
            user = User.objects.create_superuser(
                email=email,
                password=password,
                first_name="Super",
                last_name="Admin",
                email_is_verified=True,
            )

            self.stdout.write(
                self.style.SUCCESS(
                    "\n" + "=" * 60 + "\n"
                    "✅ Суперадмин успешно создан!\n" + "=" * 60 + "\n"
                    f"📧 Email:    {email}\n"
                    f"🔑 Password: {password}\n"
                    f"👤 Name:     {user.first_name} {user.last_name}\n"
                    f"🔒 Status:   Superuser, Staff\n"
                    f"✉️  Verified: Yes\n" + "=" * 60 + "\n"
                )
            )

            logger.info(
                f"Создан суперадмин: {email} (ID: {user.id}, is_superuser: True, is_staff: True)"
            )

            self.stdout.write(
                self.style.WARNING(
                    "⚠️  ВНИМАНИЕ: Этот пароль очень простой!\n"
                    "   Используйте только для разработки/тестирования.\n"
                    "   В продакшене обязательно смените пароль!\n"
                )
            )

        except IntegrityError as e:
            self.stdout.write(
                self.style.ERROR(
                    f"❌ Ошибка целостности базы данных: {e}\n"
                    f"   Возможно пользователь уже существует"
                )
            )
            logger.error(f"IntegrityError при создании суперадмина: {e}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Неожиданная ошибка: {e}"))
            logger.error(f"Ошибка при создании суперадмина: {e}", exc_info=True)
