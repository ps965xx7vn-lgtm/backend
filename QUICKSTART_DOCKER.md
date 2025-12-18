# 🐳 Docker Quick Start - Запуск за 5 минут

## Вариант 1: Docker Compose (рекомендуется для разработки)

```bash
# 1. Запуск всех сервисов (web + postgres + redis + celery)
docker-compose up -d

# 2. Проверка что все работает
docker-compose ps

# 3. Создание суперпользователя
docker-compose exec web python manage.py createsuperuser

# 4. Открыть в браузере
open http://localhost:8000
```

**Готово!** 🎉

## Вариант 2: Production Docker (минимальный образ)

```bash
# 1. Сборка образа
docker build -t pyland-backend:latest .

# 2. Запуск с внешними БД
docker run -d \
  --name pyland-web \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  -e REDIS_URL=redis://host:6379/0 \
  -e SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())') \
  -e DEBUG=False \
  pyland-backend:latest
```

## Health Checks

```bash
# Liveness - приложение живо?
curl http://localhost:8000/api/health/

# Readiness - готово принимать трафик?
curl http://localhost:8000/api/readiness/
```

## Логи

```bash
# Все сервисы
docker-compose logs -f

# Только веб
docker-compose logs -f web

# Только celery
docker-compose logs -f celery-worker
```

## Остановка

```bash
# Остановить без удаления данных
docker-compose down

# Остановить + удалить все данные (БД, media)
docker-compose down -v
```

Подробнее: [DOCKER.md](DOCKER.md)
