# 🚀 Конфигурация для деплоя Pyland на VDS

Эта папка содержит все необходимое для деплоя проекта Pyland на VDS с использованием Nginx, Gunicorn и systemd.

## 📁 Структура

```
nginx/
├── pyland.conf                    # Конфигурация Nginx
├── systemd/                       # Systemd сервисы
│   ├── pyland-gunicorn.service   # Gunicorn сервер
│   ├── pyland-celery-worker.service  # Celery worker
│   └── pyland-celery-beat.service    # Celery beat scheduler
├── scripts/                       # Скрипты управления
│   ├── install.sh                # Первоначальная установка
│   ├── deploy.sh                 # Деплой обновлений
│   ├── manage_services.sh        # Управление сервисами
│   ├── backup.sh                 # Создание бекапов
│   └── pre_deploy_check.sh       # Проверка перед деплоем
└── README.md                      # Эта инструкция
```

## 🔧 Первоначальная установка

### 0. Подготовка DNS (ОБЯЗАТЕЛЬНО!)

⚠️ **ДО начала установки настройте DNS записи!**

Добавьте A-записи в панели вашего регистратора:
- `pylandschool.com` → `78.40.219.145`
- `www.pylandschool.com` → `78.40.219.145`

Подождите 5-15 минут и проверьте:

```bash
# Локальная проверка перед деплоем
cd nginx/scripts
./pre_deploy_check.sh
```

📖 Подробная инструкция: [nginx/DNS_SETUP.md](DNS_SETUP.md)

### 0.5. Подготовка кода (ОБЯЗАТЕЛЬНО!)

⚠️ **Перед установкой на сервер закоммитьте и запушьте изменения!**

```bash
# Автоматическая подготовка (рекомендуется)
cd /path/to/backend
./nginx/scripts/prepare_deploy.sh

# Или вручную
git add .
git commit -m "Deploy configuration for pylandschool.com"
git push origin main  # или dev для тестирования
```

### 1. Подготовка сервера

```bash
# Подключитесь к серверу
ssh root@78.40.219.145

# Создайте директорию и клонируйте репозиторий
mkdir -p /opt/pyland
cd /opt/pyland

# Production (ветка main)
git clone -b main https://github.com/ps965xx7vn-lgtm/backend.git

# Или development/testing (ветка dev)
# git clone -b dev https://github.com/ps965xx7vn-lgtm/backend.git
```

### 2. Запуск скрипта установки

```bash
cd /opt/pyland/backend/nginx/scripts
sudo ./install.sh
```

Скрипт автоматически:
- Установит все системные зависимости (Python 3.13, PostgreSQL, Redis, Nginx)
- Создаст пользователя `pyland`
- Настроит PostgreSQL и Redis
- Установит Python зависимости через Poetry
- Создаст .env файл
- Настроит systemd сервисы
- Настроит Nginx

### 3. Ручная настройка

После установки выполните:

```bash
# 1. Отредактируйте .env файл (укажите пароли и API ключи)
nano /opt/pyland/backend/.env

# 2. Создайте суперпользователя
sudo -u pyland /opt/pyland/.venv/bin/python /opt/pyland/backend/src/manage.py createsuperuser

# 3. 🔐 ОБЯЗАТЕЛЬНО! Установите SSL сертификат
sudo certbot --nginx -d pylandschool.com -d www.pylandschool.com

# 4. Перезапустите Nginx
sudo systemctl restart nginx
```

⚠️ **ВАЖНО**: Убедитесь, что DNS A-запись для pylandschool.com и www.pylandschool.com указывает на IP сервера **78.40.219.145** до запуска certbot!

## 🔄 Деплой обновлений

После внесения изменений в код:

```bash
cd /opt/pyland/backend/nginx/scripts
sudo ./deploy.sh
```

Скрипт автоматически:
- Подтянет обновления из Git
- Обновит зависимости
- Применит миграции БД
- Соберет статику
- Скомпилирует переводы
- Перезапустит все сервисы

## 🎛️ Управление сервисами

### Использование скрипта manage_services.sh

```bash
cd /opt/pyland/backend/nginx/scripts

# Запустить все сервисы
sudo ./manage_services.sh start

# Остановить все сервисы
sudo ./manage_services.sh stop

# Перезапустить все сервисы
sudo ./manage_services.sh restart

# Проверить статус
sudo ./manage_services.sh status

# Посмотреть логи
sudo ./manage_services.sh logs
```

### Управление отдельными сервисами

```bash
# Gunicorn
sudo systemctl start pyland-gunicorn
sudo systemctl stop pyland-gunicorn
sudo systemctl restart pyland-gunicorn
sudo systemctl status pyland-gunicorn

# Celery Worker
sudo systemctl start pyland-celery-worker
sudo systemctl stop pyland-celery-worker
sudo systemctl restart pyland-celery-worker
sudo systemctl status pyland-celery-worker

# Celery Beat
sudo systemctl start pyland-celery-beat
sudo systemctl stop pyland-celery-beat
sudo systemctl restart pyland-celery-beat
sudo systemctl status pyland-celery-beat

# Nginx
sudo systemctl reload nginx
sudo systemctl restart nginx
sudo systemctl status nginx
```

## 📊 Просмотр логов

### Логи systemd сервисов

```bash
# Gunicorn
sudo journalctl -u pyland-gunicorn -f

# Celery Worker
sudo journalctl -u pyland-celery-worker -f

# Celery Beat
sudo journalctl -u pyland-celery-beat -f

# Nginx
sudo tail -f /var/log/nginx/pyland_access.log
sudo tail -f /var/log/nginx/pyland_error.log
```

### Логи приложения

```bash
# Gunicorn логи
sudo tail -f /opt/pyland/backend/logs/gunicorn-access.log
sudo tail -f /opt/pyland/backend/logs/gunicorn-error.log

# Celery логи
sudo tail -f /opt/pyland/backend/logs/celery-worker.log
sudo tail -f /opt/pyland/backend/logs/celery-beat.log

# Django логи
sudo tail -f /opt/pyland/backend/src/logs/*.log
```

## 💾 Создание бекапов

```bash
cd /opt/pyland/backend/nginx/scripts
sudo ./backup.sh
```

Бекапы сохраняются в `/opt/pyland/backups/`:
- База данных (PostgreSQL dump)
- Медиа файлы (tar.gz архив)
- Автоматическое удаление бекапов старше 30 дней

### Восстановление из бекапа

```bash
# Восстановление БД
gunzip -c /opt/pyland/backups/pyland_backup_YYYYMMDD_HHMMSS.sql.gz | sudo -u postgres psql pyland_db

# Восстановление медиа
tar -xzf /opt/pyland/backups/media_backup_YYYYMMDD_HHMMSS.tar.gz -C /opt/pyland/backend/src/
```

## 🔐 Настройка SSL (Let's Encrypt)

```bash
# Установка Certbot
sudo apt install certbot python3-certbot-nginx

# Получение сертификата
sudo certbot --nginx -d pylandschool.com -d www.pylandschool.com

# Автоматическое обновление
sudo certbot renew --dry-run
```

⚠️ **ВАЖНО**: Конфигурация настроена для работы только через HTTPS! До установки SSL сертификата сайт будет недоступен.

## 🐛 Решение проблем

### Сервис не запускается

```bash
# Проверить статус
sudo systemctl status pyland-gunicorn

# Посмотреть подробные логи
sudo journalctl -u pyland-gunicorn -n 100 --no-pager

# Проверить конфигурацию
cd /opt/pyland/backend/src
/opt/pyland/.venv/bin/gunicorn --check-config pyland.wsgi:application
```

### Nginx возвращает 502 Bad Gateway

```bash
# Проверить, запущен ли Gunicorn
sudo systemctl status pyland-gunicorn

# Проверить socket файл
ls -la /opt/pyland/gunicorn.sock

# Проверить права доступа
sudo chown -R pyland:www-data /opt/pyland
```

### Статические файлы не загружаются

```bash
# Пересобрать статику
cd /opt/pyland/backend/src
sudo -u pyland /opt/pyland/.venv/bin/python manage.py collectstatic --noinput --clear

# Проверить права доступа
sudo chmod -R 755 /opt/pyland/backend/src/staticfiles
```

### Celery задачи не выполняются

```bash
# Проверить Redis
redis-cli ping  # Должен вернуть PONG

# Проверить Celery Worker
sudo systemctl status pyland-celery-worker

# Посмотреть очередь задач
cd /opt/pyland/backend/src
sudo -u pyland /opt/pyland/.venv/bin/celery -A pyland inspect active
```

## 📝 Важные файлы и пути

| Путь | Описание |
|------|----------|
| `/opt/pyland/backend/` | Корень проекта |
| `/opt/pyland/.venv/` | Виртуальное окружение |
| `/opt/pyland/backend/.env` | Переменные окружения |
| `/opt/pyland/backend/src/` | Django приложение |
| `/opt/pyland/backend/src/staticfiles/` | Статические файлы |
| `/opt/pyland/backend/src/media/` | Медиа файлы |
| `/opt/pyland/backend/logs/` | Логи приложения |
| `/opt/pyland/gunicorn.sock` | Unix socket Gunicorn |
| `/etc/nginx/sites-available/pyland` | Конфигурация Nginx |
| `/etc/systemd/system/pyland-*.service` | Systemd сервисы |

## 🔄 Автоматизация

### Cron для бекапов

Добавьте в crontab:

```bash
sudo crontab -e

# Ежедневный бекап в 3:00
0 3 * * * /opt/pyland/backend/nginx/scripts/backup.sh
```

### Мониторинг сервисов

Можно настроить systemd для отправки уведомлений при падении сервисов или использовать сторонние решения (UptimeRobot, Pingdom).

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи сервисов
2. Убедитесь, что все зависимости установлены
3. Проверьте права доступа к файлам
4. Убедитесь, что PostgreSQL и Redis запущены

---

**Автор**: Pyland Team
**Версия**: 1.0
**Дата**: Февраль 2026
