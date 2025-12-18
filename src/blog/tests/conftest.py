"""
Pytest Configuration and Fixtures.

Этот модуль содержит общие fixtures для всех тестов блога.
Fixtures используются для подготовки тестового окружения.
"""

from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from rest_framework.test import APIClient

User = get_user_model()

# ============================================================================
# USER FIXTURES
# ============================================================================


@pytest.fixture
def user(db):
    """
    Обычный пользователь для тестов.

    Returns:
        User: Обычный пользователь (не staff, не superuser)
    """
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
        first_name="Test",
        last_name="User",
    )


@pytest.fixture
def staff_user(db):
    """
    Пользователь со статусом staff.

    Returns:
        User: Staff пользователь
    """
    from authentication.models import Role

    # Создаем или получаем роль manager
    manager_role, _ = Role.objects.get_or_create(
        name="manager", defaults={"description": "Manager role"}
    )

    user = User.objects.create_user(
        username="staffuser",
        email="staff@example.com",
        password="staffpass123",
        first_name="Staff",
        last_name="User",
        is_staff=True,
        is_superuser=True,  # Superuser имеет все права
    )
    user.role = manager_role
    user.save()
    return user


@pytest.fixture
def superuser(db):
    """
    Суперпользователь (администратор).

    Returns:
        User: Superuser
    """
    return User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="adminpass123",
        first_name="Admin",
        last_name="User",
    )


@pytest.fixture
def author_user(db):
    """
    Пользователь-автор с опубликованными статьями.

    Returns:
        User: Автор статей
    """
    return User.objects.create_user(
        username="author",
        email="author@example.com",
        password="authorpass123",
        first_name="Author",
        last_name="Writer",
    )


# ============================================================================
# CLIENT FIXTURES
# ============================================================================


@pytest.fixture
def client():
    """
    Django test client.

    Returns:
        Client: Django test client
    """
    return Client()


# Удалена фикстура api_client - используется session-scope фикстура из root conftest.py
# которая возвращает TestClient(api) для всего проекта


@pytest.fixture
def authenticated_client(client, user):
    """
    Аутентифицированный Django client.

    Args:
        client: Django test client
        user: Тестовый пользователь

    Returns:
        Client: Аутентифицированный client
    """
    client.force_login(user)
    return client


@pytest.fixture
def authenticated_api_client(user):
    """
    Аутентифицированный API client с JWT токеном для Ninja API.

    Args:
        user: Тестовый пользователь

    Returns:
        Client: Django client с JWT токеном в заголовках
    """
    from ninja_jwt.tokens import RefreshToken

    # Создаем JWT токен
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)

    # Создаем новый client
    client = Client()
    # Используем HTTP_AUTHORIZATION напрямую в каждом запросе
    # через хелпер метод
    original_get = client.get
    original_post = client.post

    def get_with_auth(*args, **kwargs):
        kwargs.setdefault("HTTP_AUTHORIZATION", f"Bearer {access_token}")
        return original_get(*args, **kwargs)

    def post_with_auth(*args, **kwargs):
        kwargs.setdefault("HTTP_AUTHORIZATION", f"Bearer {access_token}")
        return original_post(*args, **kwargs)

    client.get = get_with_auth
    client.post = post_with_auth

    return client


@pytest.fixture
def staff_client(client, staff_user):
    """
    Client с авторизацией под staff пользователем.

    Args:
        client: Django test client
        staff_user: Staff пользователь

    Returns:
        Client: Staff client
    """
    client.force_login(staff_user)
    return client


@pytest.fixture
def admin_client(client, superuser):
    """
    Client с авторизацией под администратором.

    Args:
        client: Django test client
        superuser: Суперпользователь

    Returns:
        Client: Admin client
    """
    client.force_login(superuser)
    return client


# ============================================================================
# DATABASE FIXTURES
# ============================================================================


@pytest.fixture
def django_db_setup(django_db_setup, django_db_blocker):
    """
    Настройка тестовой базы данных.

    Этот fixture запускается один раз перед всеми тестами.
    """
    with django_db_blocker.unblock():
        # Здесь можно добавить начальные данные для всех тестов
        pass


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================


def pytest_configure(config):
    """
    Настройка pytest перед запуском тестов.

    Args:
        config: Pytest configuration object
    """
    # Можно добавить кастомные маркеры
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "api: marks tests as API tests")
