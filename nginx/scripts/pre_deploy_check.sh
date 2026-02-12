#!/bin/bash

# Скрипт проверки готовности к деплою Pyland
# Использование: ./pre_deploy_check.sh

set -e

DOMAIN="pylandschool.com"
SERVER_IP="78.40.219.145"

# Цвета
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

echo "🔍 Проверка готовности к деплою Pyland..."
echo ""

# 1. Проверка DNS
echo "1. Проверка DNS записей..."
DNS_RESULT=$(dig +short $DOMAIN)
if [ "$DNS_RESULT" == "$SERVER_IP" ]; then
    log_info "DNS запись для $DOMAIN корректна: $DNS_RESULT"
else
    log_error "DNS запись для $DOMAIN некорректна!"
    echo "   Ожидается: $SERVER_IP"
    echo "   Получено: $DNS_RESULT"
    echo "   Настройте DNS записи в панели регистратора и подождите 15 минут."
fi

DNS_WWW=$(dig +short www.$DOMAIN)
if [ "$DNS_WWW" == "$SERVER_IP" ]; then
    log_info "DNS запись для www.$DOMAIN корректна: $DNS_WWW"
else
    log_error "DNS запись для www.$DOMAIN некорректна!"
    echo "   Ожидается: $SERVER_IP"
    echo "   Получено: $DNS_WWW"
fi

echo ""

# 2. Проверка доступности сервера
echo "2. Проверка доступности сервера..."
if ping -c 1 $SERVER_IP &> /dev/null; then
    log_info "Сервер $SERVER_IP доступен"
else
    log_error "Сервер $SERVER_IP недоступен"
fi

echo ""

# 3. Проверка портов (если есть доступ к серверу)
if [ "$EUID" -eq 0 ] && [ -f "/etc/nginx/nginx.conf" ]; then
    echo "3. Проверка сервисов на сервере..."

    # Проверка Nginx
    if systemctl is-active --quiet nginx; then
        log_info "Nginx запущен"
    else
        log_warning "Nginx не запущен"
    fi

    # Проверка PostgreSQL
    if systemctl is-active --quiet postgresql; then
        log_info "PostgreSQL запущен"
    else
        log_error "PostgreSQL не запущен"
    fi

    # Проверка Redis
    if systemctl is-active --quiet redis-server || systemctl is-active --quiet redis; then
        log_info "Redis запущен"
    else
        log_error "Redis не запущен"
    fi

    # Проверка Gunicorn
    if systemctl is-active --quiet pyland-gunicorn; then
        log_info "Gunicorn запущен"
    else
        log_warning "Gunicorn не запущен (нормально для первого запуска)"
    fi

    echo ""

    # 4. Проверка firewall
    echo "4. Проверка firewall..."
    if ufw status | grep -q "Status: active"; then
        log_info "Firewall активен"
        if ufw status | grep -q "Nginx Full"; then
            log_info "Nginx Full разрешен"
        else
            log_warning "Nginx Full не разрешен в firewall"
            echo "   Выполните: sudo ufw allow 'Nginx Full'"
        fi
    else
        log_warning "Firewall неактивен"
    fi

    echo ""

    # 5. Проверка файлов проекта
    echo "5. Проверка файлов проекта..."
    if [ -d "/opt/pyland/backend" ]; then
        log_info "Директория проекта существует"
    else
        log_error "Директория проекта не найдена: /opt/pyland/backend"
    fi

    if [ -f "/opt/pyland/backend/.env" ]; then
        log_info ".env файл существует"
    else
        log_warning ".env файл не найден (будет создан при установке)"
    fi

    echo ""

    # 6. Проверка SSL сертификата
    echo "6. Проверка SSL сертификата..."
    if [ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
        log_info "SSL сертификат найден"
        # Проверка срока действия
        EXPIRY=$(openssl x509 -enddate -noout -in /etc/letsencrypt/live/$DOMAIN/fullchain.pem | cut -d= -f2)
        log_info "Срок действия сертификата: $EXPIRY"
    else
        log_warning "SSL сертификат не найден"
        echo "   Получите сертификат: sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN"
    fi
else
    echo "3. Проверка на сервере недоступна (запустите с правами root на сервере)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Итоговая проверка
if [ "$DNS_RESULT" == "$SERVER_IP" ] && [ "$DNS_WWW" == "$SERVER_IP" ]; then
    echo ""
    log_info "✅ DNS настроен корректно! Можно продолжать установку."
    echo ""
    echo "Следующие шаги:"
    echo "1. Подключитесь к серверу: ssh root@$SERVER_IP"
    echo "2. Создайте директорию: mkdir -p /opt/pyland && cd /opt/pyland"
    echo "3. Клонируйте репозиторий: git clone https://github.com/ps965xx7vn-lgtm/backend.git"
    echo "4. Запустите установку: cd backend/nginx/scripts && sudo ./install.sh"
else
    echo ""
    log_error "❌ DNS не настроен! Перед установкой:"
    echo ""
    echo "1. Добавьте DNS A-записи:"
    echo "   @ → $SERVER_IP"
    echo "   www → $SERVER_IP"
    echo ""
    echo "2. Подождите 5-15 минут"
    echo ""
    echo "3. Проверьте снова: ./pre_deploy_check.sh"
    echo ""
    echo "Подробнее: см. nginx/DNS_SETUP.md"
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
