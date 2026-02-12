# 🚀 Быстрый деплой на VDS

## Информация о сервере

- **IP**: 78.40.219.145
- **Домен**: pylandschool.com
- **Протокол**: HTTPS (обязательно)

## ⚡ Быстрый старт (3 шага)

### 1. Настройте DNS (5-15 минут)

Добавьте A-записи в панели регистратора:
- `pylandschool.com` → `78.40.219.145`
- `www.pylandschool.com` → `78.40.219.145`

Проверьте:
```bash
./nginx/scripts/pre_deploy_check.sh
```

### 2. Установите на сервер

```bash
# Подключитесь к серверу и клонируйте репозиторий
ssh root@78.40.219.145
mkdir -p /opt/pyland
cd /opt/pyland
git clone https://github.com/ps965xx7vn-lgtm/backend.git

# Запустите установку
cd backend/nginx/scripts
sudo ./install.sh
```

### 3. Получите SSL сертификат

```bash
# Настройте .env
nano /opt/pyland/backend/.env

# Создайте суперпользователя
sudo -u pyland /opt/pyland/.venv/bin/python /opt/pyland/backend/src/manage.py createsuperuser

# Получите SSL (ОБЯЗАТЕЛЬНО!)
sudo certbot --nginx -d pylandschool.com -d www.pylandschool.com

# Перезапустите Nginx
sudo systemctl restart nginx
```

## 📚 Полная документация

- [nginx/README.md](nginx/README.md) - Подробная инструкция по деплою
- [nginx/DNS_SETUP.md](nginx/DNS_SETUP.md) - Настройка DNS
- [nginx/QUICKSTART.md](nginx/QUICKSTART.md) - Быстрый старт

## 🔄 Деплой обновлений

```bash
ssh root@78.40.219.145
cd /opt/pyland/backend/nginx/scripts
sudo ./deploy.sh
```

## 🎛️ Управление сервисами

```bash
# Статус всех сервисов
sudo ./nginx/scripts/manage_services.sh status

# Перезапуск всех сервисов
sudo ./nginx/scripts/manage_services.sh restart

# Просмотр логов
sudo ./nginx/scripts/manage_services.sh logs
```

## 💾 Бекапы

```bash
sudo ./nginx/scripts/backup.sh
```

Бекапы сохраняются в `/opt/pyland/backups/`

## ⚠️ Важно

- Сайт настроен для работы **только через HTTPS**
- До установки SSL сертификата сайт будет недоступен
- Убедитесь, что DNS записи корректны перед запуском certbot
- Все пароли и секретные ключи указывайте в файле `.env`

## 🐛 Решение проблем

См. раздел "Решение проблем" в [nginx/README.md](nginx/README.md#🐛-решение-проблем)
