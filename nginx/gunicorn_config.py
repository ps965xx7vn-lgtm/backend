# Gunicorn конфигурация для Pyland
# Использование: gunicorn -c gunicorn_config.py pyland.wsgi:application

import multiprocessing
import os

# Пути
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logs")

# Сервер
bind = "unix:/opt/pyland/gunicorn.sock"
backlog = 2048

# Worker процессы
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 90
keepalive = 5

# Graceful timeout для корректного завершения при перезапуске
graceful_timeout = 30

# Логирование
accesslog = os.path.join(LOG_DIR, "gunicorn-access.log")
errorlog = os.path.join(LOG_DIR, "gunicorn-error.log")
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Процесс
pidfile = "/var/run/gunicorn/pyland.pid"
umask = 0o007
user = "pyland"
group = "www-data"

# Environment
raw_env = [
    "DJANGO_SETTINGS_MODULE=pyland.settings",
]

# Перезагрузка при изменении кода (только для разработки!)
reload = False

# Daemon mode (для systemd должно быть False)
daemon = False

# Preload приложения для экономии памяти
preload_app = True

# Временные файлы
tmp_upload_dir = None

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190


# Хуки
def on_starting(server):
    """Вызывается перед запуском master процесса"""
    print("Gunicorn master process starting...")


def on_reload(server):
    """Вызывается при перезагрузке"""
    print("Gunicorn reloading...")


def when_ready(server):
    """Вызывается когда сервер готов принимать запросы"""
    print("Gunicorn is ready. Spawning workers...")


def pre_fork(server, worker):
    """Вызывается перед созданием worker процесса"""
    pass


def post_fork(server, worker):
    """Вызывается после создания worker процесса"""
    print(f"Worker spawned (pid: {worker.pid})")


def pre_exec(server):
    """Вызывается перед новым master процессом при перезапуске"""
    print("Forked child, re-executing.")


def worker_int(worker):
    """Вызывается когда worker получает SIGINT или SIGQUIT"""
    print(f"Worker received INT or QUIT signal (pid: {worker.pid})")


def worker_abort(worker):
    """Вызывается когда worker получает SIGABRT"""
    print(f"Worker received SIGABRT signal (pid: {worker.pid})")
