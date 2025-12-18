"""
Core Application Configuration

Конфигурация приложения core для Django.
Содержит основные страницы, формы обратной связи и подписки.
"""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """
    Конфигурация приложения Core.

    Attributes:
        default_auto_field: Тип автоматического поля для первичных ключей
        name: Имя приложения для регистрации в Django
        verbose_name: Человеко-читаемое название приложения
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
    verbose_name = "Основные функции"
