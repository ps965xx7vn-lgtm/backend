#!/bin/bash

# Скрипт первоначальной установки Pyland на VDS
# Использование: sudo ./install.sh

set -e

echo "🔧 Установка Pyland на сервер..."

# Переменные
PROJECT_NAME="pyland"
PROJECT_DIR="/opt/pyland"
BACKEND_DIR="$PROJECT_DIR/backend"
USER="pyland"
DOMAIN="pylandschool.com"
SERVER_IP="78.40.219.145"
GIT_REPO="https://github.com/ps965xx7vn-lgtm/backend.git"
GIT_BRANCH="${GIT_BRANCH:-main}"  # По умолчанию main, можно переопределить

# Цвета
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

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
    log_error "Запустите скрипт с правами root: sudo ./install.sh"
    exit 1
fi

# 1. Обновление системы
log_info "Обновление системы..."
apt update && apt upgrade -y

# 2. Определение доступной версии Python
log_info "Определение доступной версии Python..."
if command -v python3.13 &> /dev/null; then
    PYTHON_VERSION="python3.13"
    PYTHON_VENV="python3.13-venv"
elif command -v python3.12 &> /dev/null; then
    PYTHON_VERSION="python3.12"
    PYTHON_VENV="python3.12-venv"
elif command -v python3.11 &> /dev/null; then
    PYTHON_VERSION="python3.11"
    PYTHON_VENV="python3.11-venv"
else
    PYTHON_VERSION="python3"
    PYTHON_VENV="python3-venv"
fi
log_info "Используется: $PYTHON_VERSION"

# 3. Установка необходимых пакетов
log_info "Установка системных пакетов..."
apt install -y \
    $PYTHON_VERSION \
    $PYTHON_VENV \
    python3-pip \
    postgresql \
    postgresql-contrib \
    nginx \
    redis-server \
    git \
    curl \
    build-essential \
    libpq-dev \
    python3-dev \
    gettext

# 4. Установка Poetry
log_info "Установка Poetry..."
curl -sSL https://install.python-poetry.org | $PYTHON_VERSION -
export PATH="/root/.local/bin:$PATH"

# 5. Создание пользователя
log_info "Создание пользователя $USER..."
if id "$USER" &>/dev/null; then
    log_warning "Пользователь $USER уже существует"
else
    useradd -m -s /bin/bash $USER
    usermod -aG www-data $USER
fi

# 5. Создание директорий проекта
log_info "Создание директорий..."
mkdir -p $PROJECT_DIR
mkdir -p $BACKEND_DIR/logs
mkdir -p $BACKEND_DIR/src/media
mkdir -p $BACKEND_DIR/src/staticfiles

# 6. Клонирование репозитория
log_info "Клонирование репозитория из GitHub (ветка: $GIT_BRANCH)..."
if [ ! -d "$BACKEND_DIR" ]; then
    git clone -b $GIT_BRANCH $GIT_REPO $BACKEND_DIR
    log_info "Репозиторий клонирован из ветки $GIT_BRANCH"
else
    log_warning "Директория $BACKEND_DIR уже существует"
    cd $BACKEND_DIR
    sudo -u $USER git fetch origin
    sudo -u $USER git checkout $GIT_BRANCH
    sudo -u $USER git pull origin $GIT_BRANCH || log_warning "Не удалось обновить репозиторий"
fi

# 7. Настройка PostgreSQL
log_info "Настройка PostgreSQL..."
sudo -u postgres psql -c "CREATE DATABASE pyland_db;" || log_warning "База данных уже существует"
sudo -u postgres psql -c "CREATE USER pyland_user WITH PASSWORD 'your_password';" || log_warning "Пользователь уже существует"
sudo -u postgres psql -c "ALTER ROLE pyland_user SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE pyland_user SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE pyland_user SET timezone TO 'UTC';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE pyland_db TO pyland_user;"
sudo -u postgres psql -c "ALTER DATABASE pyland_db OWNER TO pyland_user;"

# 8. Настройка Redis
log_info "Настройка Redis..."
systemctl enable redis-server
systemctl start redis-server

# 9. Установка Python зависимостей
log_info "Установка Python зависимостей..."
cd $BACKEND_DIR
sudo -u $USER $PYTHON_VERSION -m venv $PROJECT_DIR/.venv
sudo -u $USER $PROJECT_DIR/.venv/bin/pip install --upgrade pip
sudo -u $USER $PROJECT_DIR/.venv/bin/pip install poetry
sudo -u $USER $PROJECT_DIR/.venv/bin/poetry config virtualenvs.create false
sudo -u $USER $PROJECT_DIR/.venv/bin/poetry install --no-dev

# 10. Настройка .env файла
log_info "Создание .env файла..."
if [ ! -f "$BACKEND_DIR/.env" ]; then
    cat > $BACKEND_DIR/.env << EOF
# Django settings
DEBUG=False
SECRET_KEY=$(openssl rand -base64 32)
ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN,localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://pyland_user:your_password@localhost:5432/pyland_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# HTTPS settings
SECURE_PROXY_SSL_HEADER=True
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
CSRF_TRUSTED_ORIGINS=https://pylandschool.com,https://www.pylandschool.com

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Static & Media
STATIC_ROOT=/opt/pyland/backend/src/staticfiles
MEDIA_ROOT=/opt/pyland/backend/src/media

EOF
    chown $USER:www-data $BACKEND_DIR/.env
    chmod 640 $BACKEND_DIR/.env
    log_info "✓ .env файл создан. Отредактируйте его: nano $BACKEND_DIR/.env"
else
    log_warning ".env файл уже существует"
fi

# 11. Применение миграций и сбор статики
log_info "Применение миграций..."
cd $BACKEND_DIR/src
sudo -u $USER $PROJECT_DIR/.venv/bin/python manage.py migrate

log_info "Создание ролей пользователей..."
sudo -u $USER $PROJECT_DIR/.venv/bin/python manage.py create_roles

log_info "Сбор статических файлов..."
sudo -u $USER $PROJECT_DIR/.venv/bin/python manage.py collectstatic --noinput

log_info "Компиляция переводов..."
sudo -u $USER $PROJECT_DIR/.venv/bin/python manage.py compilemessages

# 12. Создание суперпользователя
log_info "Создание суперпользователя..."
log_warning "Выполните вручную: sudo -u $USER $PROJECT_DIR/.venv/bin/python $BACKEND_DIR/src/manage.py createsuperuser"

# 13. Установка systemd сервисов
log_info "Установка systemd сервисов..."
cp $BACKEND_DIR/nginx/systemd/*.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable pyland-gunicorn
systemctl enable pyland-celery-worker
systemctl enable pyland-celery-beat
systemctl start pyland-gunicorn
systemctl start pyland-celery-worker
systemctl start pyland-celery-beat

# 14. Настройка Nginx
log_info "Настройка Nginx..."
cp $BACKEND_DIR/nginx/pyland.conf /etc/nginx/sites-available/pyland
sed -i "s/your-domain.com/$DOMAIN/g" /etc/nginx/sites-available/pyland
ln -sf /etc/nginx/sites-available/pyland /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx

# 15. Настройка прав доступа
log_info "Настройка прав доступа..."
chown -R $USER:www-data $PROJECT_DIR
chmod -R 755 $PROJECT_DIR
chmod -R 775 $BACKEND_DIR/logs
chmod -R 775 $BACKEND_DIR/src/media
chmod 660 $BACKEND_DIR/.env

# 16. Настройка firewall
log_info "Настройка firewall..."
ufw allow 'Nginx Full'
ufw allow OpenSSH
ufw --force enable

log_info "✅ Установка завершена!"
log_info ""
log_info "📝 ВАЖНО! Следующие шаги:"
log_info "1. Отредактируйте .env файл: nano $BACKEND_DIR/.env"
log_info "2. Создайте суперпользователя: sudo -u $USER $PROJECT_DIR/.venv/bin/python $BACKEND_DIR/src/manage.py createsuperuser"
log_info "3. 🔐 ОБЯЗАТЕЛЬНО установите SSL сертификат:"
log_info "   certbot --nginx -d $DOMAIN -d www.$DOMAIN"
log_info "4. После получения SSL перезапустите Nginx:"
log_info "   systemctl restart nginx"
log_info "5. Проверьте сайт: https://$DOMAIN"
log_info ""
log_info "⚠️  ВНИМАНИЕ: Сайт настроен для работы только через HTTPS!"
log_info "   До установки SSL сертификата сайт будет недоступен."
log_info "   Убедитесь, что DNS записи для $DOMAIN указывают на IP: $SERVER_IP"
log_info ""
log_info "Статус сервисов:"
systemctl status pyland-gunicorn --no-pager
systemctl status nginx --no-pager
