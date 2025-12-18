"""
Тесты для Django forms authentication.

Проверяет валидацию форм.
"""

import pytest
from django.contrib.auth import get_user_model

from authentication.forms import PasswordResetForm, SetPasswordForm, UserLoginForm, UserRegisterForm
from authentication.tests.factories import UserFactory

User = get_user_model()


@pytest.mark.django_db
class TestUserRegisterForm:
    """Тесты формы регистрации."""

    def test_valid_registration_form(self):
        """Валидная форма регистрации."""
        form_data = {
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!",
            "first_name": "John",
            "phone_number": "+79991234567",
            "agree_to_terms": True,
        }

        form = UserRegisterForm(data=form_data)

        assert form.is_valid()

    def test_password_mismatch(self):
        """Ошибка при несовпадении паролей."""
        form_data = {
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "confirm_password": "DifferentPass123!",
            "first_name": "John",
            "phone_number": "+79991234567",
            "agree_to_terms": True,
        }

        form = UserRegisterForm(data=form_data)

        assert not form.is_valid()
        assert "confirm_password" in form.errors or "__all__" in form.errors

    def test_duplicate_email(self):
        """Ошибка при существующем email."""
        UserFactory(email="existing@example.com")

        form_data = {
            "email": "existing@example.com",
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!",
            "first_name": "John",
            "phone_number": "+79991234567",
            "agree_to_terms": True,
        }

        form = UserRegisterForm(data=form_data)

        assert not form.is_valid()
        assert "email" in form.errors

    def test_invalid_email_format(self):
        """Ошибка при невалидном формате email."""
        form_data = {
            "email": "invalid-email",
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!",
            "first_name": "John",
            "phone_number": "+79991234567",
            "agree_to_terms": True,
        }

        form = UserRegisterForm(data=form_data)

        assert not form.is_valid()
        assert "email" in form.errors

    def test_weak_password(self):
        """Ошибка при слабом пароле."""
        form_data = {
            "email": "newuser@example.com",
            "password": "123",
            "confirm_password": "123",
            "first_name": "John",
            "phone_number": "+79991234567",
            "agree_to_terms": True,
        }

        form = UserRegisterForm(data=form_data)

        assert not form.is_valid()
        # Django password validators будут жаловаться
        assert (
            "password" in form.errors
            or "confirm_password" in form.errors
            or "__all__" in form.errors
        )


@pytest.mark.django_db
class TestUserLoginForm:
    """Тесты формы входа."""

    def test_missing_email(self):
        """Ошибка при отсутствии email."""
        form_data = {"password": "TestPass123!"}

        form = UserLoginForm(data=form_data)

        assert not form.is_valid()
        assert "email" in form.errors

    def test_missing_password(self):
        """Ошибка при отсутствии пароля."""
        form_data = {"email": "test@example.com"}

        form = UserLoginForm(data=form_data)

        assert not form.is_valid()
        assert "password" in form.errors


@pytest.mark.django_db
class TestPasswordResetForm:
    """Тесты формы сброса пароля."""

    def test_valid_password_reset_form(self):
        """Валидная форма сброса пароля."""
        UserFactory(email="test@example.com")

        form_data = {"email": "test@example.com"}

        form = PasswordResetForm(data=form_data)

        assert form.is_valid()

    def test_invalid_email(self):
        """Ошибка при невалидном email."""
        form_data = {"email": "invalid-email"}

        form = PasswordResetForm(data=form_data)

        assert not form.is_valid()
        assert "email" in form.errors


@pytest.mark.django_db
class TestSetPasswordForm:
    """Тесты формы установки нового пароля."""

    def test_valid_set_password_form(self):
        """Валидная форма установки пароля."""
        user = UserFactory()

        form_data = {"new_password1": "NewSecurePass123!", "new_password2": "NewSecurePass123!"}

        form = SetPasswordForm(user=user, data=form_data)

        assert form.is_valid()

    def test_password_mismatch(self):
        """Ошибка при несовпадении паролей."""
        user = UserFactory()

        form_data = {"new_password1": "NewSecurePass123!", "new_password2": "DifferentPass123!"}

        form = SetPasswordForm(user=user, data=form_data)

        assert not form.is_valid()
        assert "new_password2" in form.errors

    def test_weak_password(self):
        """Ошибка при слабом пароле."""
        user = UserFactory()

        form_data = {"new_password1": "123", "new_password2": "123"}

        form = SetPasswordForm(user=user, data=form_data)

        assert not form.is_valid()
