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

### ⚠️ ВАЖНО: НЕ переключайтесь вручную между ветками!

**Используй Pull Requests через GitHub UI, а не ручной merge!**

---

## 📋 Полный Workflow (шаг за шагом)

### Этап 1: Разработка новой фичи

```bash
# 1. Убедись что на develop
git checkout develop
git pull origin develop

# 2. Создай feature ветку
git checkout -b feature/add-user-profile

# 3. Разработка (локально или Docker)
poetry shell && cd src
python manage.py runserver

# 4. Коммиты по ходу работы
git add .
git commit -m "feat: add user profile page"
git commit -m "feat: add profile edit form"

# 5. Залей на GitHub
git push origin feature/add-user-profile
```

### Этап 2: Pull Request в develop (через GitHub UI)

1. **Открой GitHub:** https://github.com/your-repo/backend
2. **Создай Pull Request:**
   - Source: `feature/add-user-profile`
   - Target: `develop`
   - Добавь описание изменений

3. **GitHub Actions автоматически:**
   - ✅ Запустит тесты (pytest)
   - ✅ Проверит линтинг (ruff, black)
   - ✅ Проверит security (bandit)
   - ✅ Покажет coverage

4. **Если CI прошел:**
   - ✅ Зелёная галочка в PR
   - 👀 Code review (опционально)
   - 🔀 Нажми "Merge Pull Request"
   - 🗑️ Удали feature ветку (GitHub предложит)

5. **Если CI упал:**
   - ❌ Красный крестик
   - 🔍 Посмотри логи в Actions
   - 🛠️ Исправь локально:
     ```bash
     git add .
     git commit -m "fix: resolve test failures"
     git push origin feature/add-user-profile
     ```
   - CI запустится заново автоматически

### Этап 3: Тестирование на develop (опционально)

После merge в `develop` можешь протестировать:

```bash
# Переключись на develop
git checkout develop
git pull origin develop

# Запусти локально или в Docker
docker-compose up -d

# Проверь что всё работает
curl http://localhost:8000/api/health/
```

**Или** задеплой на dev окружение (когда настроим k8s).

### Этап 4: Release в main (через GitHub UI)

Когда накопились фичи и готов релиз:

1. **Создай Pull Request на GitHub:**
   - Source: `develop`
   - Target: `main`
   - Название: "Release v1.2.0"
   - Опиши все изменения (changelog)

2. **GitHub Actions запустит полный CI:**
   - ✅ Все тесты
   - ✅ Security checks
   - ✅ Coverage upload
   - ✅ Documentation checks

3. **После проверки:**
   - 🔀 Merge в `main` через UI
   - 🏷️ Создай Git tag:
     ```bash
     git checkout main
     git pull origin main
     git tag -a v1.2.0 -m "Release 1.2.0: User profiles, bug fixes"
     git push origin v1.2.0
     ```

4. **Production deploy:**
   - Пока вручную (позже автоматизируем через GitHub Actions)
   - К этому моменту `main` уже протестирован дважды (в feature PR и в develop)

---

## 🚫 Что НЕ делать

❌ **НЕ делай `git merge` вручную:**
```bash
# ❌ ПЛОХО - пропускает CI и code review
git checkout main
git merge develop
git push origin main
```

✅ **Используй Pull Request:**
- Открой PR: `develop` → `main`
- CI проверит автоматически
- Merge через GitHub UI

❌ **НЕ пушь напрямую в main:**
```bash
# ❌ ПЛОХО - нарушает защиту ветки
git checkout main
git commit -m "quick fix"
git push origin main  # Будет отклонен если настроена защита
```

✅ **Создай feature ветку даже для hotfix:**
```bash
git checkout -b hotfix/critical-bug
git commit -m "fix: critical security issue"
git push origin hotfix/critical-bug
# Открой PR в GitHub
```

---

## 🔄 Краткая шпаргалка

| Действие | Команда/Где |
|----------|-------------|
| Новая фича | `git checkout -b feature/name` от `develop` |
| Залить код | `git push origin feature/name` |
| **Merge фичи в develop** | **GitHub UI → Pull Request** |
| Проверить develop | `git checkout develop && git pull` |
| **Release в main** | **GitHub UI → Pull Request (develop → main)** |
| Создать tag | `git tag -a v1.0.0 && git push origin v1.0.0` |

**Главное правило:** Весь код попадает в `develop` и `main` только через Pull Requests!

### 🤖 Как работает CI/CD

| Ветка | Когда запускается CI | Что проверяет |
|-------|---------------------|---------------|
| `feature/*` | При push | ❌ НЕ запускается (только локально) |
| `develop` | При **Pull Request** | ✅ Тесты + Линтинг + Security |
| `main` | При **Pull Request** | ✅ Полный CI + Coverage + Docs |

**Что делает CI автоматически:**
- ✅ `pytest` - запускает 134 теста
- ✅ `ruff` + `black` + `isort` - проверяет форматирование
- ✅ `bandit` + `safety` - security сканирование
- ✅ `codecov` - загружает coverage отчет

**CI показывает результат прямо в Pull Request:**
- 🟢 Зелёная галочка = всё ОК, можно мержить
- 🔴 Красный крестик = есть ошибки, нужно исправить
- 🟡 Жёлтый кружок = CI ещё работает, подожди

**Важно:** CI запускается **автоматически** при создании/обновлении PR. Тебе ничего не нужно запускать вручную!

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
