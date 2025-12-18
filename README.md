# Pyland Backend

[![CI](https://github.com/ps965xx7vn-lgtm/backend/actions/workflows/ci.yml/badge.svg)](https://github.com/ps965xx7vn-lgtm/backend/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/ps965xx7vn-lgtm/backend/branch/main/graph/badge.svg)](https://codecov.io/gh/ps965xx7vn-lgtm/backend)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Django 5.2](https://img.shields.io/badge/django-5.2-green.svg)](https://www.djangoproject.com/)

Django 5.2 онлайн школа программирования с многоролевой системой пользователей.

**Стек:** Django 5.2 + Django Ninja (REST API) · Python 3.13 · PostgreSQL · Redis · Celery · Docker

---

## 🚀 Быстрый старт

### Вариант 1: Docker (рекомендуется)

```bash
# Запуск всех сервисов (web + postgres + redis + celery)
docker-compose up -d

# Создание суперпользователя
docker-compose exec web python manage.py createsuperuser

# Открыть: http://localhost:8000
```

### Вариант 2: Локально (без Docker)

```bash
# 1. Установка зависимостей
poetry install

# 2. Активация virtualenv
poetry shell
cd src

# 3. Применение миграций
python manage.py migrate
python manage.py create_roles

# 4. Создание суперпользователя
python manage.py createsuperuser

# 5. Запуск сервера
python manage.py runserver
```

**Важно для локальной разработки:**
- PostgreSQL должен быть запущен (или используется SQLite по умолчанию)
- Redis опционален (будет использован dummy cache если Redis недоступен)

---

## 📂 Структура проекта

```
backend/
├── src/                          # Django приложение
│   ├── authentication/          # Пользователи, роли, JWT auth
│   ├── students/                # Функционал для студентов
│   ├── courses/                 # Курсы, уроки, задания
│   ├── blog/                    # Статьи, комментарии, реакции
│   ├── reviewers/               # Ревью и обратная связь
│   ├── certificates/            # Сертификаты о завершении
│   ├── payments/                # Платежи
│   ├── notifications/           # Email/SMS/Telegram уведомления
│   ├── core/                    # Общие функции, health checks
│   ├── pyland/                  # Настройки Django
│   └── manage.py
├── .github/workflows/           # CI/CD конфигурация
├── Dockerfile                   # Production образ
├── docker-compose.yml           # Локальная разработка
├── pyproject.toml              # Poetry зависимости
└── README.md                   # Эта инструкция
```

---

## 🔄 Git Workflow (Ветки и CI)

### Основные ветки

```
main         - Production-ready код (защищена, только PR)
  ↑
  └── develop  - Development ветка (текущая разработка)
       ↑
       └── feature/* - Фичи/фиксы (короткоживущие)
```

### Как работать с ветками

**1. Создание новой фичи:**
```bash
# Переключиться на develop
git checkout develop
git pull origin develop

# Создать feature ветку
git checkout -b feature/my-new-feature

# Работа над фичей
git add .
git commit -m "feat: add new feature"
git push origin feature/my-new-feature
```

**2. Pull Request → develop:**
- GitHub Actions запускает CI (тесты, линтинг, security checks)
- Code review от команды
- Merge в `develop` после проверки

**3. Release → main:**
```bash
# После тестирования на develop
git checkout main
git merge develop
git tag -a v1.0.0 -m "Release 1.0.0"
git push origin main --tags
```

### CI/CD на разных ветках

| Ветка | Триггер | Что запускается | Результат |
|-------|---------|-----------------|-----------|
| `feature/*` | Push | ❌ Не запускается | Локальная разработка |
| `develop` | Push/PR | ✅ CI (тесты + линтинг) | Проверка перед merge |
| `main` | Push/PR | ✅ CI + Security + Docs | Production checks |

**CI включает:**
- ✅ Тесты (pytest): 134 passed, 9 skipped
- ✅ Линтинг (ruff, black, isort)
- ✅ Security (bandit, safety)
- ✅ Coverage upload (Codecov)

---

## 🐳 Docker vs Локальная разработка

### Когда использовать Docker:

✅ **Рекомендуется для:**
- Быстрый старт проекта
- Тестирование production окружения
- Celery worker/beat разработка
- Полная изоляция окружения

**Запуск:**
```bash
docker-compose up -d                    # Все сервисы
docker-compose logs -f web              # Просмотр логов
docker-compose exec web bash            # Shell внутри контейнера
docker-compose down                     # Остановка
```

### Когда использовать локально:

✅ **Рекомендуется для:**
- Быстрая итерация кода (hot reload)
- Debugging с breakpoints
- IDE интеграция (PyCharm, VS Code)
- Работа без Docker Desktop

**Запуск:**
```bash
poetry shell                            # Активация virtualenv
cd src
python manage.py runserver              # Django dev server
pytest -v                               # Тесты
```

### Health Checks (для k8s readiness)

```bash
# Приложение живо?
curl http://localhost:8000/api/health/

# Готово принимать трафик? (проверка БД + Redis)
curl http://localhost:8000/api/readiness/
```

---

## 🧪 Тестирование

```bash
# Все тесты
poetry run pytest

# С coverage
poetry run pytest --cov=src --cov-report=html

# Конкретное приложение
poetry run pytest blog/tests/

# С verbose
poetry run pytest -v --tb=short

# Быстро (параллельно)
poetry run pytest -n auto
```

**Статус тестов:** 134 passed, 9 skipped (некоторые тесты временно отключены из-за Ninja API конфликтов)

---

## 🔧 Полезные команды

### Django Management

```bash
# Миграции
python manage.py makemigrations
python manage.py migrate

# Создание данных
python manage.py create_roles              # Роли пользователей
python manage.py populate_courses_data     # Тестовые курсы
python manage.py populate_blog_data        # Тестовые статьи

# Суперпользователь
python manage.py createsuperuser

# Shell
python manage.py shell

# Статика
python manage.py collectstatic --noinput
```

### Docker Compose

```bash
# Управление сервисами
docker-compose up -d                       # Запуск
docker-compose down                        # Остановка
docker-compose down -v                     # Остановка + удаление БД
docker-compose restart web                 # Перезапуск сервиса
docker-compose ps                          # Статус

# Логи
docker-compose logs -f                     # Все сервисы
docker-compose logs -f web                 # Только web
docker-compose logs -f celery-worker       # Только celery

# Выполнение команд
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py shell
docker-compose exec postgres psql -U pyland_user -d pyland
```

### Pre-commit Hooks

```bash
# Установка
pre-commit install

# Ручной запуск
pre-commit run --all-files

# Обновление хуков
pre-commit autoupdate
```

---

## 🌐 API Документация

- **Swagger UI:** http://localhost:8000/api/docs
- **ReDoc:** http://localhost:8000/api/redoc
- **OpenAPI Schema:** http://localhost:8000/api/openapi.json

**Основные endpoints:**
- `/api/auth/*` - Аутентификация (JWT)
- `/api/blog/*` - Блог (статьи, комментарии)
- `/api/courses/*` - Курсы и уроки
- `/api/students/*` - Студенты
- `/api/health/` - Health check (liveness)
- `/api/readiness/` - Readiness check (БД + Redis)

---

## 🚧 Production Readiness (~40%)

**Готово:**
- ✅ CI/CD (GitHub Actions)
- ✅ Docker containerization
- ✅ Health checks для k8s
- ✅ Pre-commit hooks
- ✅ Security checks (bandit, safety)

**В процессе (план на k8s):**
- ⏳ Kubernetes manifests (ConfigMap, Deployments, Services)
- ⏳ GitHub Actions → GHCR (Docker registry)
- ⏳ Observability (Prometheus, Grafana, Loki)
- ⏳ Autoscaling (HPA)

---

## 📝 Переменные окружения

Создайте `.env` файл (см. `.env.example`):

```bash
# Django
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/pyland

# Redis
REDIS_URL=redis://localhost:6379/0

# Sentry (опционально)
SENTRY_DSN=https://...
```

---

## 🤝 Участие в разработке

1. Fork репозитория
2. Создайте feature ветку от `develop`
3. Коммиты следуют [Conventional Commits](https://www.conventionalcommits.org/)
4. Запустите тесты и pre-commit
5. Откройте Pull Request в `develop`

**Типы коммитов:**
- `feat:` - новая фича
- `fix:` - исправление бага
- `docs:` - документация
- `test:` - тесты
- `refactor:` - рефакторинг
- `chore:` - технические изменения

---

## 📞 Контакты

- **Документация проекта:** См. `src/*/README.md` в каждом приложении
- **GitHub Issues:** https://github.com/ps965xx7vn-lgtm/backend/issues

---

## 📄 Лицензия

MIT License - см. LICENSE файл
