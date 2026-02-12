#!/bin/bash

# Скрипт деплоя Pyland на VDS
# Использование: ./deploy.sh

set -e

echo "🚀 Начало деплоя Pyland..."

# Переменные
PROJECT_DIR="/opt/pyland/backend"
VENV_DIR="/opt/pyland/.venv"
USER="pyland"

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Функция для логирования
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка прав root
if [ "$EUID" -ne 0 ]; then
    log_error "Запустите скрипт с правами root: sudo ./deploy.sh"
    exit 1
fi

# 1. Обновление кода из Git
log_info "Обновление кода из репозитория..."
cd $PROJECT_DIR
sudo -u $USER git pull origin main

# 2. Обновление зависимостей через Poetry
log_info "Обновление зависимостей..."
cd $PROJECT_DIR
sudo -u $USER $VENV_DIR/bin/poetry install --no-dev

# 3. Применение миграций
log_info "Применение миграций базы данных..."
cd $PROJECT_DIR/src
sudo -u $USER $VENV_DIR/bin/python manage.py migrate --noinput

# 4. Сбор статических файлов
log_info "Сбор статических файлов..."
sudo -u $USER $VENV_DIR/bin/python manage.py collectstatic --noinput --clear

# 5. Компиляция переводов
log_info "Компиляция переводов..."
sudo -u $USER $VENV_DIR/bin/python manage.py compilemessages

# 6. Перезапуск сервисов
log_info "Перезапуск Gunicorn..."
systemctl restart pyland-gunicorn

log_info "Перезапуск Celery Worker..."
systemctl restart pyland-celery-worker

log_info "Перезапуск Celery Beat..."
systemctl restart pyland-celery-beat

# 7. Перезагрузка Nginx
log_info "Перезагрузка Nginx..."
nginx -t && systemctl reload nginx

# 8. Проверка статуса сервисов
log_info "Проверка статуса сервисов..."
sleep 2

if systemctl is-active --quiet pyland-gunicorn; then
    log_info "✓ Gunicorn запущен"
else
    log_error "✗ Gunicorn не запущен"
    systemctl status pyland-gunicorn
    exit 1
fi

if systemctl is-active --quiet pyland-celery-worker; then
    log_info "✓ Celery Worker запущен"
else
    log_warning "✗ Celery Worker не запущен"
fi

if systemctl is-active --quiet pyland-celery-beat; then
    log_info "✓ Celery Beat запущен"
else
    log_warning "✗ Celery Beat не запущен"
fi

if systemctl is-active --quiet nginx; then
    log_info "✓ Nginx запущен"
else
    log_error "✗ Nginx не запущен"
    exit 1
fi

# 9. Очистка старых логов (опционально)
log_info "Очистка старых логов..."
find $PROJECT_DIR/logs -type f -name "*.log" -mtime +30 -delete

log_info "✅ Деплой завершен успешно!"
log_info "Проверьте приложение: http://your-domain.com"
