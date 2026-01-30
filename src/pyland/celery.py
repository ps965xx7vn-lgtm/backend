import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyland.settings")

app = Celery("pyland")

# Загружаем конфигурацию из Django settings
app.config_from_object("django.conf:settings", namespace="CELERY")

# Убедитесь, что Celery будет отслеживать события задач
app.conf.worker_send_task_events = True
app.conf.task_track_started = True
app.conf.eventer = "celery.events.Eventer"

# Автоматическое обнаружение задач
app.autodiscover_tasks()

# Периодические задачи (Celery Beat)
app.conf.beat_schedule = {
    "warm-cache-every-5-minutes": {
        "task": "blog.warm_cache",
        "schedule": 300.0,  # 5 минут
    },
    "update-popular-articles-hourly": {
        "task": "blog.update_popular_articles",
        "schedule": 3600.0,  # 1 час
    },
    "cleanup-old-cache-daily": {
        "task": "blog.cleanup_old_cache",
        "schedule": 86400.0,  # 24 часа
    },
    "generate-sitemap-daily": {
        "task": "blog.generate_sitemap",
        "schedule": 86400.0,  # 24 часа
    },
}
