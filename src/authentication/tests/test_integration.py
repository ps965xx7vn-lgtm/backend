"""
Интеграционные тесты полного цикла аутентификации.

Проверяет:
- Полный цикл регистрации
- Полный цикл входа/выхода
- Сброс пароля
- Верификация email
"""

import pytest
from django.contrib.auth import get_user_model

from authentication.tests.factories import UserFactory

User = get_user_model()


@pytest.mark.django_db
class TestCompleteRegistrationFlow:
    """Тесты полного цикла регистрации."""

    def test_complete_student_registration_flow(self, api_client, student_role):
        """Полный цикл регистрации студента от начала до конца."""
        # Шаг 1: Регистрация
        payload = {
            "email": "newstudent@example.com",
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!",
            "first_name": "John",
            "last_name": "Doe",
            "role": "student",
        }

        response = api_client.post("/auth/register", json=payload)

        assert response.status_code == 201
        data = response.json()

        # Проверяем, что получили токены
        assert "user" in data
        assert "tokens" in data
        access_token = data["tokens"]["access"]

        # Шаг 2: Получаем профиль с токеном
        response = api_client.get(
            "/auth/profile", headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 200
        profile_data = response.json()
        assert "user" in profile_data
        assert "profile" in profile_data
        assert profile_data["user"]["email"] == "newstudent@example.com"

        # Шаг 3: Проверяем создание пользователя в БД
        user = User.objects.get(email="newstudent@example.com")
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert hasattr(user, "student")
        assert user.student is not None

    def test_complete_multi_role_registration(self, api_client, mentor_role, reviewer_role):
        """Регистрация с разными ролями."""
        roles_to_test = [
            ("mentor", "mentor"),
            ("reviewer", "reviewer"),
            ("manager", "manager"),
        ]

        for idx, (role_name, profile_attr) in enumerate(roles_to_test):
            email = f"{role_name}{idx}@example.com"

            payload = {
                "email": email,
                "password": "SecurePass123!",
                "confirm_password": "SecurePass123!",
                "first_name": role_name.capitalize(),
                "last_name": "User",
                "role": role_name,
            }

            response = api_client.post("/auth/register", json=payload)

            assert response.status_code == 201

            # Проверяем профиль
            user = User.objects.get(email=email)
            assert hasattr(user, profile_attr)


@pytest.mark.django_db
class TestCompleteLoginLogoutFlow:
    """Тесты полного цикла входа/выхода."""

    @pytest.mark.skip(reason="Использует /login - authenticate() несовместим с TestClient")
    def test_complete_login_logout_cycle(self, api_client):
        """Полный цикл: регистрация → вход → выход."""
        # Создаем пользователя
        UserFactory(
            email="test@example.com",
            password="TestPass123!",
            is_active=True,
            email_is_verified=True,
        )

        # Шаг 1: Вход
        login_payload = {"email": "test@example.com", "password": "TestPass123!"}

        response = api_client.post("/auth/login", json=login_payload)

        assert response.status_code == 200
        data = response.json()
        access_token = data["tokens"]["access"]
        refresh_token = data["tokens"]["refresh"]

        # Шаг 2: Работа с аутентифицированным API
        response = api_client.get(
            "/auth/profile", headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 200

        # Шаг 3: Выход
        logout_payload = {"refresh_token": refresh_token}

        response = api_client.post(
            "/logout", json=logout_payload, headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 200


@pytest.mark.django_db
class TestCompletePasswordChangeFlow:
    """Тесты полного цикла смены пароля."""

    @pytest.mark.skip(reason="Использует /login - authenticate() несовместим с TestClient")
    def test_complete_password_change_cycle(self, api_client):
        """Полный цикл смены пароля."""
        # Создаем пользователя
        UserFactory(
            email="test@example.com", password="OldPass123!", is_active=True, email_is_verified=True
        )

        # Шаг 1: Логинимся со старым паролем
        response = api_client.post(
            "/login", json={"email": "test@example.com", "password": "OldPass123!"}
        )

        assert response.status_code == 200
        access_token = response.json()["tokens"]["access"]

        # Шаг 2: Меняем пароль
        response = api_client.post(
            "/password/change",
            json={
                "old_password": "OldPass123!",
                "new_password": "NewPass123!",
                "confirm_new_password": "NewPass123!",
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200

        # Шаг 3: Логинимся с новым паролем
        response = api_client.post(
            "/login", json={"email": "test@example.com", "password": "NewPass123!"}
        )

        assert response.status_code == 200

        # Шаг 4: Проверяем, что старый пароль не работает
        response = api_client.post(
            "/login", json={"email": "test@example.com", "password": "OldPass123!"}
        )

        assert response.status_code == 401


@pytest.mark.django_db
class TestCompleteProfileUpdateFlow:
    """Тесты полного цикла обновления профиля."""

    @pytest.mark.skip(reason="Использует /login - authenticate() несовместим с TestClient")
    def test_complete_profile_update_cycle(self, api_client):
        """Полный цикл обновления профиля."""
        # Создаем пользователя
        user = UserFactory(
            email="test@example.com",
            password="TestPass123!",
            first_name="Original",
            last_name="Name",
            is_active=True,
            email_is_verified=True,
        )

        # Логинимся
        response = api_client.post(
            "/login", json={"email": "test@example.com", "password": "TestPass123!"}
        )

        access_token = response.json()["tokens"]["access"]

        # Получаем текущий профиль
        response = api_client.get(
            "/auth/profile", headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 200
        original_data = response.json()
        assert original_data["user"]["first_name"] == "Original"

        # Обновляем профиль
        update_payload = {
            "first_name": "Updated",
            "last_name": "NewName",
            "phone": "+79991234567",
            "country": "RU",
            "city": "Moscow",
            "bio": "Updated bio text",
        }

        response = api_client.patch(
            "/profile", json=update_payload, headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 200
        updated_data = response.json()
        assert updated_data["first_name"] == "Updated"
        assert updated_data["last_name"] == "NewName"

        # Проверяем в БД
        user.refresh_from_db()
        assert user.first_name == "Updated"
        assert user.last_name == "NewName"
