"""
Authentication Application Configuration

Конфигурация приложения authentication для Django.
Управляет системой аутентификации, профилями пользователей и ролями
в рамках платформы Pyland School.
"""

from __future__ import annotations

from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    """
    Конфигурация приложения Authentication.

    Attributes:
        default_auto_field: Тип первичного ключа для моделей
        name: Имя приложения в Django проекте
        verbose_name: Человекочитаемое название для админки
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "authentication"
    verbose_name = "Аутентификация"

    def ready(self) -> None:
        """
        Инициализация приложения при запуске Django.

        Подключает сигналы для автоматического создания профилей
        при регистрации новых пользователей.
        """
        import authentication.signals  # noqa: F401
