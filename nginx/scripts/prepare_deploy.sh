#!/bin/bash

# 🚀 Скрипт подготовки к деплою
# Выполните этот скрипт ПЕРЕД установкой на сервер

set -e

# Цвета
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
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

log_step() {
    echo -e "${BLUE}[→]${NC} $1"
}

echo "🚀 Подготовка к деплою Pyland"
echo ""

# 1. Проверка git статуса
log_step "Проверка git статуса..."
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    log_error "Это не git репозиторий!"
    exit 1
fi

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
log_info "Текущая ветка: $CURRENT_BRANCH"

# 2. Проверка несохраненных изменений
if ! git diff-index --quiet HEAD --; then
    log_warning "Есть несохраненные изменения:"
    git status --short
    echo ""
    read -p "Продолжить? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_error "Отменено пользователем"
        exit 1
    fi
fi

# 3. Проверка конфигурации nginx
log_step "Проверка конфигурации nginx..."
if [ -f "nginx/pyland.conf" ]; then
    if grep -q "pylandschool.com" nginx/pyland.conf; then
        log_info "Домен настроен: pylandschool.com"
    else
        log_error "Домен не настроен в nginx/pyland.conf"
        exit 1
    fi

    if grep -q "/opt/pyland" nginx/pyland.conf; then
        log_info "Пути настроены: /opt/pyland"
    else
        log_error "Пути не обновлены на /opt/pyland"
        exit 1
    fi
else
    log_error "Файл nginx/pyland.conf не найден!"
    exit 1
fi

# 4. Проверка скриптов
log_step "Проверка скриптов..."
for script in nginx/scripts/*.sh; do
    if [ -x "$script" ]; then
        log_info "$(basename $script) - исполняемый"
    else
        log_warning "$(basename $script) - не исполняемый (будет исправлено)"
        chmod +x "$script"
    fi
done

# 5. Выбор ветки для деплоя
echo ""
echo "📌 Выберите ветку для деплоя:"
echo "  1) main (production)"
echo "  2) dev (development/testing)"
echo "  3) Текущая ветка ($CURRENT_BRANCH)"
echo ""
read -p "Выбор (1-3): " -n 1 -r BRANCH_CHOICE
echo ""

case $BRANCH_CHOICE in
    1)
        TARGET_BRANCH="main"
        ;;
    2)
        TARGET_BRANCH="dev"
        ;;
    3)
        TARGET_BRANCH="$CURRENT_BRANCH"
        ;;
    *)
        log_error "Неверный выбор"
        exit 1
        ;;
esac

log_info "Выбрана ветка: $TARGET_BRANCH"

# 6. Переключение на нужную ветку (если требуется)
if [ "$CURRENT_BRANCH" != "$TARGET_BRANCH" ]; then
    log_step "Переключение на ветку $TARGET_BRANCH..."
    if git show-ref --verify --quiet refs/heads/$TARGET_BRANCH; then
        git checkout $TARGET_BRANCH
        log_info "Переключено на $TARGET_BRANCH"
    else
        log_error "Ветка $TARGET_BRANCH не существует"
        exit 1
    fi
fi

# 7. Получение последних изменений
log_step "Получение последних изменений..."
git fetch origin

# 8. Проверка что локальная ветка актуальна
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse @{u} 2>/dev/null || echo "no_remote")
BASE=$(git merge-base @ @{u} 2>/dev/null || echo "no_base")

if [ "$REMOTE" = "no_remote" ]; then
    log_warning "Удаленная ветка не настроена"
elif [ "$LOCAL" = "$REMOTE" ]; then
    log_info "Ветка актуальна"
elif [ "$LOCAL" = "$BASE" ]; then
    log_warning "Есть новые коммиты на сервере, нужно git pull"
    git pull origin $TARGET_BRANCH
elif [ "$REMOTE" = "$BASE" ]; then
    log_info "Есть локальные коммиты для push"
else
    log_warning "Ветки разошлись, требуется ручное слияние"
fi

# 9. Коммит изменений (если есть)
if ! git diff-index --quiet HEAD --; then
    echo ""
    log_step "Создание коммита..."
    echo ""
    git status --short
    echo ""
    read -p "Введите сообщение коммита: " COMMIT_MSG

    if [ -z "$COMMIT_MSG" ]; then
        COMMIT_MSG="Deploy configuration update for pylandschool.com"
    fi

    git add .
    git commit -m "$COMMIT_MSG"
    log_info "Коммит создан: $COMMIT_MSG"
fi

# 10. Push в удаленный репозиторий
echo ""
read -p "Запушить изменения в origin/$TARGET_BRANCH? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_step "Push в origin/$TARGET_BRANCH..."
    git push origin $TARGET_BRANCH
    log_info "Изменения отправлены на GitHub"
else
    log_warning "Push пропущен"
fi

# 11. Финальная проверка
echo ""
log_step "Финальная проверка..."
echo ""

# Последний коммит
LAST_COMMIT=$(git log -1 --pretty=format:"%h - %s (%ar)" 2>/dev/null)
log_info "Последний коммит: $LAST_COMMIT"

# URL репозитория
REPO_URL=$(git config --get remote.origin.url 2>/dev/null)
log_info "Репозиторий: $REPO_URL"

# 12. Итоговая информация
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ Готово к деплою!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 Следующие шаги:"
echo ""
echo "1. Настройте DNS (если еще не настроено):"
echo "   pylandschool.com → 78.40.219.145"
echo "   www.pylandschool.com → 78.40.219.145"
echo ""
echo "2. Подключитесь к серверу:"
echo "   ssh root@78.40.219.145"
echo ""
echo "3. Клонируйте репозиторий и запустите установку:"
echo "   mkdir -p /opt/pyland && cd /opt/pyland"
echo "   git clone -b $TARGET_BRANCH https://github.com/ps965xx7vn-lgtm/backend.git"
echo "   cd backend/nginx/scripts"
echo "   sudo ./install.sh"
echo ""
echo "4. После установки настройте .env и получите SSL:"
echo "   nano /opt/pyland/backend/.env"
echo "   sudo -u pyland /opt/pyland/.venv/bin/python /opt/pyland/backend/src/manage.py createsuperuser"
echo "   sudo certbot --nginx -d pylandschool.com -d www.pylandschool.com"
echo ""
echo "5. Проверьте: https://pylandschool.com"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
