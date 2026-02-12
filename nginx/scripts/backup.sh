#!/bin/bash

# Скрипт создания бекапа базы данных
# Использование: ./backup.sh

set -e

# Переменные
BACKUP_DIR="/opt/pyland/backups"
PROJECT_DIR="/opt/pyland/backend"
DB_NAME="pyland_db"
DB_USER="pyland_user"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="pyland_backup_$DATE.sql.gz"

# Цвета
GREEN='\033[0;32m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

# Создание директории для бекапов
mkdir -p $BACKUP_DIR

# Бекап базы данных
log_info "Создание бекапа базы данных..."
sudo -u postgres pg_dump $DB_NAME | gzip > $BACKUP_DIR/$BACKUP_FILE

# Бекап медиа файлов
log_info "Создание бекапа медиа файлов..."
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz -C $PROJECT_DIR/src media/

# Удаление старых бекапов (старше 30 дней)
log_info "Удаление старых бекапов..."
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

# Вывод информации
log_info "✓ Бекап создан: $BACKUP_DIR/$BACKUP_FILE"
log_info "✓ Размер: $(du -h $BACKUP_DIR/$BACKUP_FILE | cut -f1)"
log_info "✓ Всего бекапов: $(ls -1 $BACKUP_DIR/*.sql.gz | wc -l)"
