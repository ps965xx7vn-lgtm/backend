"""
Тесты для management команд authentication приложения.
"""

from io import StringIO

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command

User = get_user_model()


@pytest.mark.django_db
class TestCreateSuperadminCommand:
    """Тесты команды create_superadmin."""

    def test_create_superadmin_success(self):
        """Успешное создание суперадмина."""
        out = StringIO()
        call_command("create_superadmin", stdout=out)

        # Проверяем что пользователь создан
        user = User.objects.get(email="a@mail.ru")
        assert user.is_superuser is True
        assert user.is_staff is True
        assert user.is_active is True
        assert user.email_is_verified is True
        assert user.check_password("a") is True
        assert user.first_name == "Super"
        assert user.last_name == "Admin"

        # Проверяем вывод
        output = out.getvalue()
        assert "✅ Суперадмин успешно создан!" in output
        assert "a@mail.ru" in output

    def test_create_superadmin_already_exists(self):
        """Попытка создать существующего суперадмина."""
        # Создаём пользователя
        User.objects.create_user(email="a@mail.ru", password="test")

        out = StringIO()
        call_command("create_superadmin", stdout=out)

        output = out.getvalue()
        assert "❌ Пользователь с email a@mail.ru уже существует!" in output
        assert "--delete-existing" in output

    def test_create_superadmin_with_delete_existing(self):
        """Пересоздание суперадмина с флагом --delete-existing."""
        # Создаём обычного пользователя
        User.objects.create_user(email="a@mail.ru", password="old_password")

        out = StringIO()
        call_command("create_superadmin", "--delete-existing", stdout=out)

        # Проверяем что старый пользователь удалён и создан новый суперадмин
        user = User.objects.get(email="a@mail.ru")
        assert user.is_superuser is True
        assert user.check_password("a") is True  # Новый пароль
        assert not user.check_password("old_password")  # Старый пароль не работает

        output = out.getvalue()
        assert "⚠️  Существующий пользователь a@mail.ru удалён" in output
        assert "✅ Суперадмин успешно создан!" in output
