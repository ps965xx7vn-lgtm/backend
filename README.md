# Pyland Backend

[![CI](https://github.com/ps965xx7vn-lgtm/backend/actions/workflows/ci.yml/badge.svg)](https://github.com/ps965xx7vn-lgtm/backend/actions/workflows/ci.yml)
[![Docker](https://github.com/ps965xx7vn-lgtm/backend/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/ps965xx7vn-lgtm/backend/actions/workflows/docker-publish.yml)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Django 5.2](https://img.shields.io/badge/django-5.2-green.svg)](https://www.djangoproject.com/)
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)

Django 5.2 онлайн школа программирования с многоролевой системой пользователей.

**Стек:** Django 5.2 + Django Ninja (REST API) · Python 3.13+ · PostgreSQL · Redis · Celery · Docker · K8s-ready

---

## 🚀 Быстрый старт

### Production Deployment (Kubernetes)

```bash
# Полный автоматический деплой на Kubernetes
./manage.sh deploy

# Или с пропуском Docker build (для тестирования)
SKIP_DOCKER_BUILD=1 SKIP_GIT_CHECK=1 ./manage.sh deploy

# Очистка всех ресурсов
./manage.sh cleanup

# Интерактивное меню
./manage.sh
```

> 🚢 **Production:** Приложение развернуто на Timeweb Kubernetes Cloud:
> - 🌐 **URL:** https://pylandschool.com
> - 🔒 **SSL:** Let's Encrypt (автообновление)
> - 📦 **Docker:** ghcr.io/ps965xx7vn-lgtm/backend:production
> - ☸️ **K8s:** Ingress + Cert-Manager + hostNetwork

### Вариант 1: GHCR (GitHub Container Registry)

```bash
# Pull образа из GHCR
docker pull ghcr.io/ps965xx7vn-lgtm/backend:latest

# Запуск с docker-compose
docker-compose up -d

# Создание суперпользователя
docker-compose exec web python manage.py createsuperuser

# Открыть: http://localhost:8000
```

> 📦 См. [docs/deployment/](docs/deployment/) для подробной
> документации по деплою

### Вариант 2: Docker (локальная сборка)

```bash
# Запуск всех сервисов (web + postgres + redis + celery)
docker-compose up -d

# Создание суперпользователя
docker-compose exec web python manage.py createsuperuser

# Открыть: <http://localhost:8000>
```

### Вариант 3: Локально (без Docker)

```bash
# 1. Установка зависимостей
poetry install

# 2. Применение миграций
poetry run python src/manage.py migrate
poetry run python src/manage.py create_roles

# 3. Создание суперпользователя
poetry run python src/manage.py createsuperuser

# 4. Запуск сервера
poetry run python src/manage.py runserver
```text
**Важно для локальной разработки:**

- PostgreSQL должен быть запущен (или используется SQLite по умолчанию)
- Redis опционален (будет использован dummy cache если Redis недоступен)

---

## 📂 Структура проекта

```text
backend/
├── src/                          # Django приложение
│   ├── authentication/          # 🔐 Пользователи, роли, JWT auth (с автоподпиской)
│   ├── students/                # 👨‍🎓 Функционал для студентов
│   ├── courses/                 # 📚 Курсы, уроки, задания
│   ├── blog/                    # 📝 Статьи, комментарии, реакции
│   ├── reviewers/               # ✅ Ревью и обратная связь
│   ├── certificates/            # 🎓 Сертификаты о завершении
│   ├── payments/                # 💳 Система оплаты (CloudPayments, TBC Bank)
│   ├── notifications/           # 📧 Централизованная система подписок + уведомления
│   ├── core/                    # 🛠️ Общие функции, health checks, middleware
│   ├── pyland/                  # ⚙️ Настройки Django
│   ├── static/                  # 🎨 CSS, JS, изображения
│   ├── locale/                  # 🌐 Переводы (ru, en, ka)
│   └── manage.py
├── docs/                        # 📖 Документация
│   ├── deployment/              # Деплой и production
│   ├── development/             # Разработка
│   ├── examples/                # Примеры и гайды
│   └── getting-started/         # Быстрый старт
├── .github/workflows/           # 🤖 CI/CD конфигурация
├── Dockerfile                   # 🐳 Production образ
├── docker-compose.yml           # 🐳 Локальная разработка
├── pyproject.toml              # 📦 Poetry зависимости
├── CHANGELOG.md                # 📋 История изменений
└── README.md                   # 📄 Эта инструкция
```

### 🎯 Ключевые приложения

#### 💳 Payments
**Система оплаты курсов** с поддержкой двух платежных провайдеров:
- **CloudPayments** (Россия) - USD, RUB
- **TBC Bank** (Грузия) - GEL
- Автоматическая конвертация валют
- Красивый checkout с респонсивным дизайном
- Автоматическое зачисление на курс после оплаты
- 📚 [Подробная документация](src/payments/README.md)

#### 📝 Blog
**Полнофункциональный блог** с продвинутыми возможностями:
- 149 unit тестов, Redis кэширование
- Nested comments (до 3 уровней)
- Реакции, закладки, прогресс чтения
- SEO оптимизация (meta-tags, schema.org, sitemap)
- Newsletter подписки через централизованную систему notifications

#### 📧 Notifications
**Централизованная система уведомлений и подписок:**
- Единое хранение всех подписок (email, course_updates, reminders и т.д.)
- Типы подписок полностью соответствуют настройкам Student модели
- Многоканальная отправка: Email, SMS (Twilio), Telegram Bot
- Celery задачи для асинхронной обработки
- 📚 [Документация системы](docs/NOTIFICATIONS_PURPOSE.md)
- 📚 [Подробности приложения](src/notifications/README.md)

#### 👨‍🎓 Students
**Личный кабинет студента:**
- Dashboard с прогрессом по курсам
- Управление профилем и аватаром
- Настройки уведомлений (6 типов)
- История покупок

#### 📚 Courses
**Система курсов:**
- Иерархия: Course → Lesson → Step
- Submissions с workflow статусами
- Прогресс отслеживание
- Integration с payments для зачисления
---

## 🔄 Git Workflow (Ветки и CI)

### Основные ветки

```text
main         - Production-ready код (защищена, только PR)
  ↑
  └── develop  - Development ветка (текущая разработка)
       ↑
       └── feature/* - Фичи/фиксы (короткоживущие)
```text
### ⚠️ ВАЖНО: НЕ переключайтесь вручную между ветками

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

poetry run python src/manage.py runserver

# 4. Коммиты по ходу работы

git add .
git commit -m "feat: add user profile page"
git commit -m "feat: add profile edit form"

# 5. Залей на GitHub

git push origin feature/add-user-profile
```text
### Этап 2: Pull Request в develop (через GitHub UI)

1. **Открой GitHub:** <https://github.com/your-repo/backend>
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

curl <http://localhost:8000/api/health/>
```text
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
```text
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
```text
✅ **Создай feature ветку даже для hotfix:**

```bash
git checkout -b hotfix/critical-bug
git commit -m "fix: critical security issue"
git push origin hotfix/critical-bug

# Открой PR в GitHub

```text
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

### Когда использовать Docker

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
```text
### Когда использовать локально

✅ **Рекомендуется для:**

- Быстрая итерация кода (hot reload)
- Debugging с breakpoints
- IDE интеграция (PyCharm, VS Code)
- Работа без Docker Desktop

**Запуск:**

```bash
poetry run python src/manage.py runserver  # Django dev server
poetry run pytest -v                       # Тесты
```text
### Health Checks (для k8s readiness)

```bash

# Приложение живо

curl <http://localhost:8000/api/health/>

# Готово принимать трафик? (проверка БД + Redis)

curl <http://localhost:8000/api/readiness/>
```text
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
```text
**Статус тестов:** 134 passed, 9 skipped (некоторые тесты временно отключены из-за Ninja API конфликтов)

---

## 🔧 Полезные команды

### Django Management

```bash
# Миграции
poetry run python src/manage.py makemigrations
poetry run python src/manage.py migrate

# Создание данных
poetry run python src/manage.py create_roles              # Роли пользователей
poetry run python src/manage.py populate_courses_data     # Тестовые курсы
poetry run python src/manage.py populate_blog_data        # Тестовые статьи

# Суперпользователь
poetry run python src/manage.py createsuperuser

# Shell
poetry run python src/manage.py shell

# Статика
poetry run python src/manage.py collectstatic --noinput
```text
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
```text
### Pre-commit Hooks

```bash

# Установка

pre-commit install

# Ручной запуск

pre-commit run --all-files

# Обновление хуков

pre-commit autoupdate
```text
---

## 🌐 API Документация

- **Swagger UI:** <http://localhost:8000/api/docs>
- **ReDoc:** <http://localhost:8000/api/redoc>
- **OpenAPI Schema:** <http://localhost:8000/api/openapi.json>

**Основные endpoints:**

- `/api/auth/*` - Аутентификация (JWT)
- `/api/blog/*` - Блог (статьи, комментарии, newsletter)
- `/api/courses/*` - Курсы и уроки
- `/api/students/*` - Студенты и профили
- `/api/payments/*` - Платежи (TODO - webhooks)
- `/api/health/` - Health check (liveness)
- `/api/readiness/` - Readiness check (БД + Redis)

---

## 🚧 Production Readiness (~45%)

**Готово:**

- ✅ CI/CD (GitHub Actions)
- ✅ Docker containerization
- ✅ Health checks для k8s
- ✅ Pre-commit hooks
- ✅ Security checks (bandit, safety)
- ✅ Payment system (CloudPayments, TBC Bank)
- ✅ Newsletter HTML emails
- ✅ Multi-currency support (USD, GEL, RUB)

**В процессе (план на k8s):**

- ⏳ Kubernetes manifests (ConfigMap, Deployments, Services)
- ⏳ GitHub Actions → GHCR (Docker registry)
- ⏳ Observability (Prometheus, Grafana, Loki)
- ⏳ Autoscaling (HPA)
- ⏳ Payment webhooks integration (CloudPayments, TBC)
- ⏳ SMTP production setup для emails

**См. также:**
- 📋 [CHANGELOG.md](CHANGELOG.md) - Последние изменения (30.01.2026)
- 💳 [Payments README](src/payments/README.md) - Документация системы оплаты

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

SENTRY_DSN=<https://...>
```text
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
- **GitHub Issues:** <https://github.com/ps965xx7vn-lgtm/backend/issues>

---

## � Docker Hub Integration

Проект автоматически публикуется в Docker Hub при каждом коммите в `main`.

### Быстрая настройка

1. **Создайте Docker Hub Access Token:**
   - Войдите в [Docker Hub](https://hub.docker.com/)
   - Settings → Security → New Access Token
   - Скопируйте токен

2. **Добавьте GitHub Secrets:**
   - Откройте Settings → Secrets and variables → Actions
   - Добавьте `DOCKERHUB_USERNAME` (ваш username)
   - Добавьте `DOCKERHUB_TOKEN` (токен из шага 1)

3. **Обновите имя образа:**
   - Замените `username` на ваш Docker Hub username в файлах:
     - `.github/workflows/docker-publish.yml`
     - `docker-compose.prod.yml`
     - `README.md`

**Готово!** При следующем push в `main` образ автоматически соберется и
опубликуется.

📦 **Подробная документация:** [docs/deployment/](docs/deployment/)

---

## ☸️ Kubernetes Deployment

### Автоматический деплой (Production)

Единый скрипт `manage.sh` для управления Kubernetes deployment:

```bash
# Интерактивное меню выбора
./manage.sh

# Или напрямую команда
./manage.sh deploy    # Полный деплой
./manage.sh cleanup   # Очистка ресурсов
```

**Что делает автоматически:**
1. ✅ Обновляет kubeconfig с актуальным API сервером
2. ✅ Собирает и публикует Docker образ в GHCR
3. ✅ Устанавливает Nginx Ingress Controller (если нужно)
4. ✅ Устанавливает Cert-Manager для SSL (если нужно)
5. ✅ Генерирует ConfigMap и Secret из .env
6. ✅ Применяет все Kubernetes манифесты
7. ✅ Получает SSL сертификаты от Let's Encrypt
8. ✅ Проверяет health и статус всех сервисов

### Быстрый тест (без Docker build)

```bash
SKIP_DOCKER_BUILD=1 SKIP_GIT_CHECK=1 ./manage.sh deploy
```

### Production конфигурация

**Infrastructure:**
- ☸️ **Kubernetes:** Timeweb Cloud (1 node, 2GB RAM, 1 CPU)
- 🌐 **Domain:** pylandschool.com (A → 72.56.105.54)
- 🔒 **SSL:** Let's Encrypt (автообновление)
- 📦 **Registry:** GitHub Container Registry (GHCR)

**Services:**
- 🌐 Web (Django + Gunicorn)
- 🐘 PostgreSQL 15
- 📦 Redis 7
- 🔄 Celery Worker + Beat

**Network:**
- Ingress: nginx with hostNetwork (ports 80/443)
- SSL: Cert-Manager + Let's Encrypt ClusterIssuer
- HTTP → HTTPS auto-redirect

### Helpful Commands

```bash
# Проверка статуса
kubectl get pods -n pyland --insecure-skip-tls-verify
kubectl get ingress -n pyland --insecure-skip-tls-verify
kubectl get certificate -n pyland --insecure-skip-tls-verify

# Логи
kubectl logs -f deployment/web -n pyland --insecure-skip-tls-verify
kubectl logs -f deployment/celery-worker -n pyland --insecure-skip-tls-verify

# Health check
curl https://pylandschool.com/api/health/
```

**Документация:** См. [docs/deployment/K8S_DEPLOY_GUIDE.md](docs/deployment/K8S_DEPLOY_GUIDE.md)

---

## 📄 Лицензия

Proprietary License © 2025-2026 Dmitrii Masliaev. Все права защищены.

Это проприетарное программное обеспечение. Использование, копирование,
распространение или модификация без письменного разрешения строго запрещены.

См. [LICENSE](LICENSE) для получения подробной информации.

По вопросам лицензирования: masliaevdmitrii@gmail.com

---

## 📚 Документация

### 📖 Полная документация: **[docs/README.md](docs/README.md)**

### 🚀 Быстрые ссылки:

**Для деплоя:**
- ⭐ **[START HERE](docs/deployment/START_HERE.md)** - Деплой за 5 минут (одна команда!)
- 📋 **[Чеклист деплоя](docs/deployment/DEPLOY_CHECKLIST.md)** - Пошаговая инструкция
- ☸️ **[Kubernetes Guide](docs/deployment/K8S_DEPLOY_GUIDE.md)** - Полное руководство
- ✅ **[Готовность к продакшену](docs/deployment/PRODUCTION_READY.md)** - Статус готовности

**Для разработки:**
- 🚀 **[Быстрый старт](docs/getting-started/QUICK_START.md)** - Локальная разработка
- 🏗️ **[Архитектура](docs/development/ARCHITECTURE.md)** - Структура проекта
- 🤝 **[Участие в проекте](docs/development/CONTRIBUTING.md)** - Как участвовать
- 🌳 **[Git Workflow](docs/development/GIT_WORKFLOW.md)** - Работа с Git

**Устранение проблем:**
- 📧 **[Email Setup](docs/deployment/EMAIL_SMTP_SETUP.md)** - Настройка SMTP
- 🔧 **[Troubleshooting](docs/deployment/TROUBLESHOOTING.md)** - Решение проблем
