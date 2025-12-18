"""
Authentication App - Система аутентификации и управления пользователями Pyland.

Это приложение предоставляет полную систему аутентификации с поддержкой:
    - Регистрации и входа (email/password + social auth)
    - JWT токенов для API
    - Ролевой системы (6 ролей)
    - Email верификации
    - Сброса пароля
    - Управления профилями

Components:
    models - User, Role, Profile модели
    views - Django views для web-интерфейса
    api - REST API endpoints (Django Ninja)
    forms - Формы регистрации/входа
    schemas - Pydantic schemas для API
    signals - Auto-создание профилей
    tasks - Celery tasks для email
    decorators - Security decorators

Management Commands:
    create_roles - Создать базовые роли
    create_test_users - Создать тестовых пользователей

См. README.md для подробной документации.

Автор: Pyland Team
Версия: 2.0
Дата: 2025
"""

from .decorators import (
    get_user_role,
    has_permission,
    has_role,
    require_any_permission,
    require_any_role,
    require_permission,
    require_role,
    require_role_and_permission,
)

default_app_config = "authentication.apps.AuthenticationConfig"

__version__ = "2.0"
__author__ = "Pyland Team"

__all__ = [
    "require_role",
    "require_any_role",
    "require_permission",
    "require_any_permission",
    "require_role_and_permission",
    "has_role",
    "has_permission",
    "get_user_role",
]
