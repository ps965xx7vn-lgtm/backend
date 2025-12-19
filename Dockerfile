# Multi-stage Dockerfile for Pyland Backend
# Stage 1: Builder - установка зависимостей
FROM python:3.13-slim AS builder

# Метаданные
LABEL maintainer="Pyland Team"
LABEL description="Pyland Online School Backend"

# Переменные окружения для Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Системные зависимости для сборки
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gettext \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Копирование файлов зависимостей
COPY pyproject.toml ./

# Установка зависимостей (без dev-группы)
# Используем pip с поддержкой PEP 621
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir .

# Stage 2: Production - минимальный образ
FROM python:3.13-slim AS production

# Переменные окружения
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DJANGO_SETTINGS_MODULE=pyland.settings

# Системные зависимости (только runtime)
RUN apt-get update && apt-get install -y \
    libpq5 \
    gettext \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 pyland

# Рабочая директория
WORKDIR /app

# Копирование Python-пакетов из builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Копирование кода приложения
COPY --chown=pyland:pyland ./src /app/src

# Компиляция переводов
WORKDIR /app/src
RUN python manage.py compilemessages || true

# Сбор статики (будет использоваться WhiteNoise)
RUN python manage.py collectstatic --noinput || true

# Создание директорий для логов и медиа
RUN mkdir -p /app/logs /app/media /app/static && \
    chown -R pyland:pyland /app

# Переключение на непривилегированного пользователя
USER pyland

# Expose порт
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/health/ || exit 1

# Entrypoint script
COPY --chown=pyland:pyland docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

ENTRYPOINT ["/app/docker-entrypoint.sh"]

# Default command: запуск gunicorn
CMD ["gunicorn", "pyland.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "4", \
     "--worker-class", "sync", \
     "--worker-tmp-dir", "/dev/shm", \
     "--max-requests", "1000", \
     "--max-requests-jitter", "50", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info"]
