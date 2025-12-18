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
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=1.8.2 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_VIRTUALENVS_CREATE=true

# Системные зависимости
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gettext \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Установка Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry

# Рабочая директория
WORKDIR /app

# Копирование файлов зависимостей
COPY pyproject.toml poetry.lock ./

# Установка зависимостей (без dev)
RUN poetry install --only main --no-root --no-interaction --no-ansi

# Stage 2: Production - минимальный образ
FROM python:3.13-slim AS production

# Переменные окружения
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH" \
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

# Копирование virtualenv из builder
COPY --from=builder /app/.venv /app/.venv

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
