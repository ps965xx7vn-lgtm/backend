"""
Pytest fixtures для тестов authentication.

Содержит общие fixtures для всех тестов модуля.
"""

import pytest
from django.contrib.auth import get_user_model

from authentication.models import Role

User = get_user_model()


@pytest.fixture(autouse=True)
def create_roles(db):
    """Автоматически создает все роли для каждого теста."""
    roles_data = [
        ("student", "Студент"),
        ("mentor", "Ментор"),
        ("reviewer", "Ревьюер"),
        ("manager", "Менеджер"),
        ("admin", "Администратор"),
        ("support", "Поддержка"),
    ]
    for name, description in roles_data:
        Role.objects.get_or_create(name=name, defaults={"description": description})


# Используется api_client из root conftest (TestClient(api))
# Authentication tests должны использовать пути /api/auth/*


@pytest.fixture
def student_role(db):
    """Роль студента."""
    role, _ = Role.objects.get_or_create(name="student", defaults={"description": "Студент"})
    return role


@pytest.fixture
def mentor_role(db):
    """Роль ментора."""
    role, _ = Role.objects.get_or_create(name="mentor", defaults={"description": "Ментор"})
    return role


@pytest.fixture
def reviewer_role(db):
    """Роль ревьюера."""
    role, _ = Role.objects.get_or_create(name="reviewer", defaults={"description": "Ревьюер"})
    return role


@pytest.fixture
def manager_role(db):
    """Роль менеджера."""
    role, _ = Role.objects.get_or_create(name="manager", defaults={"description": "Менеджер"})
    return role


@pytest.fixture
def user(db, student_role):
    """Базовый пользователь со студентом ролью."""
    return User.objects.create_user(
        email="test@example.com",
        password="TestPass123!",
        first_name="Test",
        last_name="User",
        role=student_role,
        is_active=True,
        email_is_verified=True,
    )


@pytest.fixture
def authenticated_client(client, user):
    """Аутентифицированный Django test client."""
    client.force_login(user)
    return client


@pytest.fixture
def jwt_token(user):
    """JWT токен для аутентифицированного пользователя."""
    from ninja_jwt.tokens import RefreshToken

    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)
