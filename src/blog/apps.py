"""
Blog Application Configuration

Конфигурация приложения blog для Django.
Управляет настройками блога в рамках платформы Pyland School.
"""

from django.apps import AppConfig


class BlogConfig(AppConfig):
    """
    Конфигурация приложения Blog.

    Attributes:
        default_auto_field: Тип первичного ключа для моделей
        name: Имя приложения в Django проекте
        verbose_name: Человекочитаемое название для админки
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "blog"
    verbose_name = "Блог"
