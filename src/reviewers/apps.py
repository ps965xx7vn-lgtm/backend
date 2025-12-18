"""
Reviewers App Config - Конфигурация приложения reviewers.

Автор: Pyland Team
Дата: 2025
"""

from django.apps import AppConfig


class ReviewersConfig(AppConfig):
    """
    Конфигурация приложения reviewers.

    Отвечает за проверку работ студентов ревьюерами и менторами.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "reviewers"
    verbose_name = "Проверка работ"

    def ready(self):
        """
        Выполняется при запуске приложения.

        Подключает сигналы для автоматизации и уведомлений.
        """
        import reviewers.signals  # noqa: F401
