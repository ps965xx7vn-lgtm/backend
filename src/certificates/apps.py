from django.apps import AppConfig


class CertificatesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "certificates"
    verbose_name = "Сертификаты"

    def ready(self):
        """Подключить signals при запуске приложения."""
        import certificates.signals  # noqa: F401
