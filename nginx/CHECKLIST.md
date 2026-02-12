# ✅ Проверочный список конфигурации Pyland

## Информация о деплое

- ✅ **Сервер**: 78.40.219.145
- ✅ **Домен**: pylandschool.com, www.pylandschool.com
- ✅ **Путь**: /opt/pyland
- ✅ **Git**: https://github.com/ps965xx7vn-lgtm/backend.git
- ✅ **HTTPS**: Обязательно (редирект с HTTP)

## Обновленные файлы

### Nginx конфигурация
- ✅ `nginx/pyland.conf` - пути обновлены на /opt/pyland
  - Socket: unix:/opt/pyland/gunicorn.sock
  - Static: /opt/pyland/backend/src/staticfiles/
  - Media: /opt/pyland/backend/src/media/
  - HTTPS редирект включен
  - Домен: pylandschool.com

### Systemd сервисы
- ✅ `nginx/systemd/pyland-gunicorn.service`
  - WorkingDirectory: /opt/pyland/backend/src
  - Environment: /opt/pyland/.venv/bin
  - Socket: /opt/pyland/gunicorn.sock

- ✅ `nginx/systemd/pyland-celery-worker.service`
  - WorkingDirectory: /opt/pyland/backend/src
  - Logs: /opt/pyland/backend/logs/

- ✅ `nginx/systemd/pyland-celery-beat.service`
  - WorkingDirectory: /opt/pyland/backend/src
  - Logs: /opt/pyland/backend/logs/

### Скрипты
- ✅ `nginx/scripts/install.sh`
  - PROJECT_DIR: /opt/pyland
  - GIT_REPO: https://github.com/ps965xx7vn-lgtm/backend.git
  - Автоматическое клонирование репозитория
  - HTTPS настройки в .env

- ✅ `nginx/scripts/deploy.sh`
  - PROJECT_DIR: /opt/pyland/backend
  - Git pull из origin main

- ✅ `nginx/scripts/backup.sh`
  - BACKUP_DIR: /opt/pyland/backups
  - PROJECT_DIR: /opt/pyland/backend

- ✅ `nginx/scripts/pre_deploy_check.sh`
  - Проверка DNS для pylandschool.com → 78.40.219.145
  - Инструкции по git clone

- ✅ `nginx/scripts/manage_services.sh`
  - Управление всеми сервисами

### Конфигурация
- ✅ `nginx/gunicorn_config.py`
  - bind: unix:/opt/pyland/gunicorn.sock
  - Пути к логам обновлены

### Документация
- ✅ `nginx/README.md` - полная инструкция
  - Все пути обновлены на /opt/pyland
  - Git clone инструкции
  - DNS настройка для pylandschool.com

- ✅ `nginx/QUICKSTART.md` - быстрый старт
  - Git clone вместо scp
  - Путь: /opt/pyland

- ✅ `nginx/DNS_SETUP.md` - настройка DNS
  - IP: 78.40.219.145
  - Домен: pylandschool.com

- ✅ `DEPLOY.md` - краткая инструкция
  - Git clone команды
  - Пути обновлены

- ✅ `INSTALL_GUIDE.md` - пошаговая установка
  - 3 простых шага
  - Git clone
  - HTTPS обязательно

## Структура установки

```
/opt/pyland/
├── .venv/                      # Виртуальное окружение
├── gunicorn.sock              # Unix socket для Gunicorn
├── backups/                   # Бекапы БД и медиа
└── backend/                   # Git репозиторий
    ├── .env                   # Переменные окружения
    ├── logs/                  # Логи приложения
    │   ├── gunicorn-access.log
    │   ├── gunicorn-error.log
    │   ├── celery-worker.log
    │   └── celery-beat.log
    ├── src/                   # Django проект
    │   ├── manage.py
    │   ├── staticfiles/       # Собранная статика
    │   ├── media/             # Загруженные файлы
    │   └── ...
    └── nginx/                 # Конфигурация деплоя
        ├── pyland.conf
        ├── gunicorn_config.py
        ├── systemd/
        ├── scripts/
        └── *.md
```

## Порядок установки

1. **DNS настройка**
   ```bash
   # Добавить A-записи
   pylandschool.com → 78.40.219.145
   www.pylandschool.com → 78.40.219.145
   ```

2. **Клонирование репозитория**
   ```bash
   ssh root@78.40.219.145
   mkdir -p /opt/pyland
   cd /opt/pyland
   git clone https://github.com/ps965xx7vn-lgtm/backend.git
   ```

3. **Автоустановка**
   ```bash
   cd backend/nginx/scripts
   chmod +x *.sh
   sudo ./install.sh
   ```

4. **Настройка**
   ```bash
   nano /opt/pyland/backend/.env
   sudo -u pyland /opt/pyland/.venv/bin/python /opt/pyland/backend/src/manage.py createsuperuser
   ```

5. **SSL сертификат**
   ```bash
   sudo certbot --nginx -d pylandschool.com -d www.pylandschool.com
   sudo systemctl restart nginx
   ```

## Проверка конфигурации

```bash
# Проверить nginx
sudo nginx -t

# Проверить пути в сервисах
grep -r "/var/www" nginx/
# Не должно быть результатов

grep -r "/opt/pyland" nginx/ | wc -l
# Должно быть много результатов

# Проверить домен
grep -r "pylandschool.com" nginx/ | wc -l
# Должно быть несколько результатов

# Проверить git repo
grep "git clone" nginx/scripts/install.sh
# Должно быть: https://github.com/ps965xx7vn-lgtm/backend.git
```

## Важные моменты

- ✅ Все пути используют `/opt/pyland` вместо `/var/www/pyland`
- ✅ Git репозиторий клонируется автоматически
- ✅ HTTPS обязателен, HTTP редиректится
- ✅ Домен: pylandschool.com
- ✅ IP: 78.40.219.145
- ✅ Systemd сервисы с автоперезапуском
- ✅ Все скрипты исполняемые (chmod +x)

## Готово! ✅

Все файлы обновлены и готовы к деплою.
