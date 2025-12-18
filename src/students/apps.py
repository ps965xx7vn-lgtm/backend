from django.apps import AppConfig


class StudentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "students"
    verbose_name = "Студенты"

    def ready(self):
        """Настройка сигналов при инициализации приложения"""
        from .cache_utils import setup_cache_signals

        setup_cache_signals()
