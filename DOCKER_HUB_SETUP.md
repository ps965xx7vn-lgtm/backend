# Docker Hub Integration Setup

## Обзор

Автоматическая публикация Docker образа в Docker Hub при каждом коммите в `main`
и при создании тегов версий.

## Настройка GitHub Secrets

Для работы workflow необходимо добавить следующие secrets в настройках
репозитория GitHub:

### 1. Создайте Access Token в Docker Hub

1. Войдите в [Docker Hub](https://hub.docker.com/)
2. Перейдите в **Account Settings** → **Security** →
   **New Access Token**
3. Создайте токен с именем `github-actions` и правами **Read, Write, Delete**
4. Скопируйте токен (он отобразится только один раз)

### 2. Добавьте Secrets в GitHub

1. Откройте репозиторий на GitHub
2. Перейдите в **Settings** → **Secrets and variables** → **Actions**
3. Нажмите **New repository secret** и добавьте:

**DOCKERHUB_USERNAME**
```text
Ваш username в Docker Hub (например: myusername)
```

**DOCKERHUB_TOKEN**
```text
Access token, созданный на предыдущем шаге
```

## Использование

### Автоматическая публикация

Workflow запускается автоматически при:

- **Push в main** → публикует образ с тегами:
  - `latest`
  - `main`
  - `main-<git-sha>` (например: `main-abc1234`)

- **Push тега версии** (например, `v1.0.0`) → публикует образ с тегами:
  - `1.0.0`
  - `1.0`
  - `1`
  - `v1.0.0`

### Ручной запуск

Можно запустить workflow вручную:

1. Откройте **Actions** в GitHub
2. Выберите **Docker Build and Push**
3. Нажмите **Run workflow**

## Теги образов

| Событие | Примеры тегов |
|---------|---------------|
| Push в main | `latest`, `main`, `main-abc1234` |
| Push тега v1.2.3 | `1.2.3`, `1.2`, `1`, `v1.2.3` |
| Pull Request | `pr-123` |

## Использование опубликованного образа

### Pull образа

```bash
# Latest версия
docker pull username/pyland-backend:latest

# Конкретная версия
docker pull username/pyland-backend:1.0.0

# Конкретный коммит
docker pull username/pyland-backend:main-abc1234
```

### Запуск контейнера

```bash
docker run -d \
  --name pyland-backend \
  -p 8000:8000 \
  -e DATABASE_URL=postgres://user:pass@host/db \
  -e REDIS_URL=redis://localhost:6379/0 \
  -e SECRET_KEY=your-secret-key \
  username/pyland-backend:latest
```

### Docker Compose

```yaml
version: '3.8'

services:
  backend:
    image: username/pyland-backend:latest
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgres://postgres:postgres@db:5432/pyland
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: pyland
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

## Мультиплатформенная поддержка

Образ собирается для:
- `linux/amd64` (Intel/AMD процессоры)
- `linux/arm64` (Apple Silicon, Raspberry Pi, и др.)

## Кэширование

Workflow использует Docker layer caching для ускорения сборки:
- Кэш сохраняется в Docker Hub с тегом `buildcache`
- Последующие сборки используют закэшированные слои
- Значительно ускоряет повторные сборки

## Мониторинг

### Проверка статуса сборки

1. Откройте **Actions** в GitHub
2. Найдите последний запуск **Docker Build and Push**
3. Проверьте логи сборки

### Проверка образа в Docker Hub

1. Откройте [Docker Hub](https://hub.docker.com/)
2. Перейдите в репозиторий `username/pyland-backend`
3. Проверьте список тегов и время последнего обновления

## Метаданные образа

Каждый образ содержит метаданные:

```bash
# Просмотр labels
docker inspect username/pyland-backend:latest | jq '.[0].Config.Labels'
```

Доступные labels:
- `org.opencontainers.image.created` - дата сборки
- `org.opencontainers.image.revision` - Git SHA коммита
- `org.opencontainers.image.version` - версия
- `org.opencontainers.image.source` - URL репозитория

## Troubleshooting

### Ошибка "unauthorized: authentication required"

**Проблема:** Неверные credentials для Docker Hub

**Решение:**
1. Проверьте корректность `DOCKERHUB_USERNAME`
2. Убедитесь, что `DOCKERHUB_TOKEN` не истек
3. Пересоздайте Access Token в Docker Hub

### Ошибка "denied: requested access to the resource is denied"

**Проблема:** Недостаточно прав у токена

**Решение:**
1. Создайте новый Access Token с правами **Read, Write, Delete**
2. Обновите `DOCKERHUB_TOKEN` в GitHub Secrets

### Медленная сборка

**Проблема:** Сборка занимает много времени

**Решение:**
1. Проверьте, что кэширование работает (смотрите логи сборки)
2. Убедитесь, что `.dockerignore` настроен правильно
3. Оптимизируйте Dockerfile (группируйте команды RUN)

### Образ не появляется в Docker Hub

**Проблема:** Workflow завершился успешно, но образа нет

**Решение:**
1. Проверьте имя репозитория (`DOCKERHUB_USERNAME/pyland-backend`)
2. Убедитесь, что репозиторий существует в Docker Hub
3. Проверьте логи шага "Build and push Docker image"

## Безопасность

### Секреты

- ✅ Никогда не коммитьте токены в Git
- ✅ Используйте GitHub Secrets для хранения credentials
- ✅ Регулярно обновляйте Access Tokens

### Образ

- ✅ Образ построен на официальном `python:3.13-slim`
- ✅ Multi-stage build минимизирует размер
- ✅ Не содержит секретов и приватных данных
- ✅ Использует non-root пользователя

## Дополнительные ресурсы

- [Docker Hub Documentation](https://docs.docker.com/docker-hub/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Buildx Documentation](https://docs.docker.com/buildx/working-with-buildx/)
- [OCI Image Spec](https://github.com/opencontainers/image-spec/blob/main/annotations.md)
