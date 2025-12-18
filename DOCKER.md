# Docker Quick Start Guide

## 🚀 Быстрый старт

### 1. Создайте .env файл
```bash
cp .env.example .env
# Отредактируйте .env по необходимости
```

### 2. Запустите все сервисы
```bash
docker-compose up -d
```

### 3. Создайте суперпользователя
```bash
docker-compose exec web python manage.py createsuperuser
```

### 4. Откройте приложение
- Веб: http://localhost:8000
- Админка: http://localhost:8000/admin
- API Docs: http://localhost:8000/api/docs

## 📦 Доступные команды

### Управление контейнерами
```bash
# Запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка всех сервисов
docker-compose down

# Остановка + удаление volumes (БД будет очищена!)
docker-compose down -v

# Пересборка образов
docker-compose build

# Перезапуск конкретного сервиса
docker-compose restart web
```

### Django команды
```bash
# Миграции
docker-compose exec web python manage.py migrate

# Создание миграций
docker-compose exec web python manage.py makemigrations

# Создание суперпользователя
docker-compose exec web python manage.py createsuperuser

# Сбор статики
docker-compose exec web python manage.py collectstatic --noinput

# Django shell
docker-compose exec web python manage.py shell

# Создание ролей
docker-compose exec web python manage.py create_roles

# Заполнение тестовыми данными
docker-compose exec web python manage.py populate_courses_data
```

### Celery команды
```bash
# Просмотр логов Celery worker
docker-compose logs -f celery-worker

# Просмотр логов Celery beat
docker-compose logs -f celery-beat

# Перезапуск worker
docker-compose restart celery-worker
```

### Базы данных
```bash
# PostgreSQL shell
docker-compose exec postgres psql -U pyland_user -d pyland

# Бэкап БД
docker-compose exec postgres pg_dump -U pyland_user pyland > backup.sql

# Восстановление БД
cat backup.sql | docker-compose exec -T postgres psql -U pyland_user pyland

# Redis CLI
docker-compose exec redis redis-cli
```

## 🔍 Health Checks

```bash
# Проверка что приложение живо (liveness)
curl http://localhost:8000/api/health/

# Проверка готовности (readiness - БД + Redis)
curl http://localhost:8000/api/readiness/
```

## 🐛 Отладка

### Просмотр логов конкретного сервиса
```bash
docker-compose logs web
docker-compose logs postgres
docker-compose logs redis
docker-compose logs celery-worker
```

### Запуск bash внутри контейнера
```bash
docker-compose exec web bash
```

### Проверка переменных окружения
```bash
docker-compose exec web env | grep DATABASE
```

### Просмотр запущенных процессов
```bash
docker-compose ps
```

## 🔧 Production Build

### Сборка production образа
```bash
docker build -t pyland-backend:latest .
```

### Запуск production образа
```bash
docker run -d \
  --name pyland-web \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  -e REDIS_URL=redis://host:6379/0 \
  -e SECRET_KEY=your-secret-key \
  -e DEBUG=False \
  pyland-backend:latest
```

## 📊 Мониторинг ресурсов

```bash
# Использование CPU/RAM
docker stats

# Размер контейнеров
docker-compose ps --size

# Очистка неиспользуемых образов
docker system prune -a
```

## 🔒 Security

### Не используйте в продакшене
- Дефолтные пароли из .env.example
- DEBUG=True
- Слабый SECRET_KEY

### Обязательно в продакшене
- Сгенерируйте надёжный SECRET_KEY
- Используйте HTTPS (SSL/TLS)
- Настройте ALLOWED_HOSTS
- Используйте managed PostgreSQL/Redis (не в docker)

## 🌐 Переменные окружения

См. `.env.example` для полного списка доступных переменных.

Основные:
- `DEBUG` - режим отладки (True/False)
- `SECRET_KEY` - секретный ключ Django
- `DATABASE_URL` - URL подключения к PostgreSQL
- `REDIS_URL` - URL подключения к Redis
- `ALLOWED_HOSTS` - разрешенные хосты (через запятую)
