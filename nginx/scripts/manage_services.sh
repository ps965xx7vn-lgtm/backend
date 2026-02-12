#!/bin/bash

# Скрипт управления сервисами Pyland
# Использование: ./manage_services.sh [start|stop|restart|status]

set -e

# Цвета
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Функция для выполнения действия со всеми сервисами
manage_services() {
    local action=$1

    case $action in
        start)
            log_info "Запуск всех сервисов..."
            systemctl start pyland-gunicorn
            systemctl start pyland-celery-worker
            systemctl start pyland-celery-beat
            systemctl start nginx
            log_info "✓ Все сервисы запущены"
            ;;
        stop)
            log_info "Остановка всех сервисов..."
            systemctl stop pyland-gunicorn
            systemctl stop pyland-celery-worker
            systemctl stop pyland-celery-beat
            log_info "✓ Все сервисы остановлены"
            ;;
        restart)
            log_info "Перезапуск всех сервисов..."
            systemctl restart pyland-gunicorn
            systemctl restart pyland-celery-worker
            systemctl restart pyland-celery-beat
            systemctl reload nginx
            log_info "✓ Все сервисы перезапущены"
            ;;
        status)
            log_info "Статус сервисов:"
            echo ""
            echo "=== Gunicorn ==="
            systemctl status pyland-gunicorn --no-pager | head -n 10
            echo ""
            echo "=== Celery Worker ==="
            systemctl status pyland-celery-worker --no-pager | head -n 10
            echo ""
            echo "=== Celery Beat ==="
            systemctl status pyland-celery-beat --no-pager | head -n 10
            echo ""
            echo "=== Nginx ==="
            systemctl status nginx --no-pager | head -n 10
            ;;
        logs)
            log_info "Последние логи всех сервисов:"
            echo ""
            echo "=== Gunicorn ==="
            journalctl -u pyland-gunicorn -n 20 --no-pager
            echo ""
            echo "=== Celery Worker ==="
            journalctl -u pyland-celery-worker -n 20 --no-pager
            echo ""
            echo "=== Celery Beat ==="
            journalctl -u pyland-celery-beat -n 20 --no-pager
            ;;
        *)
            log_error "Неизвестное действие: $action"
            echo "Использование: $0 [start|stop|restart|status|logs]"
            exit 1
            ;;
    esac
}

# Проверка прав root
if [ "$EUID" -ne 0 ]; then
    log_error "Запустите скрипт с правами root: sudo $0"
    exit 1
fi

# Проверка аргументов
if [ $# -eq 0 ]; then
    log_error "Не указано действие"
    echo "Использование: $0 [start|stop|restart|status|logs]"
    exit 1
fi

# Выполнение действия
manage_services $1
