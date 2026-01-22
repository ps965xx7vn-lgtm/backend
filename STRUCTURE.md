# 📁 Структура Проекта

## Корневая директория

```
backend/
├── README.md                     # Главная страница проекта
├── LICENSE                       # MIT License
│
├── docs/                        # 📚 Вся документация (организована)
│   ├── README.md               # Индекс документации
│   ├── getting-started/        # Начало работы
│   ├── deployment/             # Деплой и production
│   └── development/            # Для разработчиков
│
├── src/                        # Django приложение
│   ├── authentication/         # Пользователи, JWT auth
│   ├── students/              # Студенческий функционал
│   ├── courses/               # Курсы и уроки
│   ├── blog/                  # Блог с комментариями
│   ├── reviewers/             # Система ревью
│   ├── certificates/          # Сертификаты
│   ├── payments/              # Платежи
│   ├── notifications/         # Email/SMS/Telegram
│   ├── core/                  # Общий функционал
│   └── pyland/                # Настройки Django
│
├── k8s/                        # Kubernetes манифесты
│   ├── timeweb-deploy.yaml    # All-in-one deployment
│   ├── ingress.yaml           # Ingress + SSL
│   └── README.md
│
├── .github/workflows/          # CI/CD pipeline
│   ├── ci.yml                 # Тесты, линтеры
│   └── docker-publish.yml     # Docker build & push
│
├── docker-compose.yml          # Локальная разработка
├── docker-compose.prod.yml     # Production (GHCR)
├── Dockerfile                  # Production образ
├── docker-entrypoint.sh        # Entrypoint скрипт
├── deploy.sh                   # Автоматический деплой
│
├── pyproject.toml             # Poetry зависимости
├── pytest.ini                 # Pytest конфигурация
├── .pre-commit-config.yaml    # Pre-commit hooks
└── .env.example               # Пример переменных окружения
```

---

## Документация (docs/)

### 📖 [docs/README.md](docs/README.md) - Главный индекс документации

### 1. Начало работы (docs/getting-started/)

```
getting-started/
└── QUICK_START.md              # Локальная разработка, Git workflow
```

Для новичков: как начать работать с проектом локально.

### 2. Деплой (docs/deployment/)

```
deployment/
├── START_HERE.md               # ⭐ Деплой за 5 минут (начните здесь!)
├── DEPLOY_CHECKLIST.md         # Пошаговый чеклист
├── K8S_DEPLOY_GUIDE.md         # Полное руководство Kubernetes
├── PRODUCTION_READY.md         # Статус готовности к продакшену
├── EMAIL_SMTP_SETUP.md         # Настройка Gmail SMTP
├── TROUBLESHOOTING.md          # Решение типичных проблем
├── DEPLOYMENT.md               # Информация о production
└── DEPLOYMENT_SUMMARY.md       # История деплоев
```

Все что нужно для деплоя на production.

### 3. Разработка (docs/development/)

```
development/
├── ARCHITECTURE.md             # Архитектура проекта
├── CONTRIBUTING.md             # Руководство для контрибьюторов
└── GIT_WORKFLOW.md             # Git flow, commit guidelines, PR процесс
```

Для разработчиков: как устроен проект и как участвовать.

---

## Приложения (src/)

Каждое приложение может иметь свою документацию:

```
src/APP_NAME/
├── README.md                   # Обзор приложения
├── models.py                  # Django модели
├── api.py                     # Django Ninja API endpoints
├── schemas.py                 # Pydantic schemas
├── views.py                   # Django views
├── admin.py                   # Django admin
├── tasks.py                   # Celery tasks
└── tests/                     # Тесты
    ├── conftest.py           # Fixtures
    ├── factories.py          # Factory Boy
    ├── test_models.py        # Model tests
    └── test_api.py           # API tests
```

**Приложения с документацией:**
- [src/authentication/README.md](src/authentication/README.md) - Система аутентификации
- [src/blog/README.md](src/blog/README.md) - Блог с комментариями
- [src/reviewers/README.md](src/reviewers/README.md) - Система ревью

---

## Kubernetes (k8s/)

```
k8s/
├── README.md                   # Обзор K8s манифестов
├── timeweb-deploy.yaml        # All-in-one манифест
│                              # (Namespace, ConfigMap, Secret, Deployments, Services, Job)
├── ingress.yaml               # Ingress + Let's Encrypt SSL
└── letsencrypt-issuer.yaml    # ClusterIssuer для SSL
```

**Структура timeweb-deploy.yaml:**
1. Namespace (pyland)
2. ConfigMap (django-config) - ENV vars
3. Secret (django-secret) - Чувствительные данные
4. PostgreSQL Deployment + Service + PVC
5. Redis Deployment + Service + PVC
6. Django Web Deployment + Service + Health checks
7. Celery Worker Deployment
8. Celery Beat Deployment
9. Migrations Job (инициализация БД)

---

## CI/CD (.github/workflows/)

```
.github/workflows/
├── ci.yml                      # Тесты + Линтеры + Security
│   ├── pytest (unit/integration)
│   ├── ruff (linting)
│   ├── black (formatting check)
│   ├── isort (import sorting)
│   ├── bandit (security scanning)
│   └── safety (dependency check)
│
└── docker-publish.yml          # Docker build & push to GHCR
    ├── Multi-platform build (linux/amd64)
    ├── Push to ghcr.io
    └── Tag: production
```

---

## Скрипты

### deploy.sh

Автоматический деплой на Kubernetes:

```bash
./deploy.sh
```

**Что делает:**
1. Build Docker образа (linux/amd64)
2. Push в ghcr.io
3. Apply K8s манифесты
4. Restart deployments
5. Wait for rollout
6. Check pod status

**Использование:**
```bash
# Стандартный деплой
./deploy.sh

# С custom tag
./deploy.sh v1.2.0

# Debug mode
DEBUG=1 ./deploy.sh
```

---

## Навигация по задачам

### Я хочу...

**...запустить проект локально:**
→ [README.md](README.md) → [docs/getting-started/QUICK_START.md](docs/getting-started/QUICK_START.md)

**...задеплоить на production:**
→ [docs/deployment/START_HERE.md](docs/deployment/START_HERE.md)

**...понять архитектуру:**
→ [docs/development/ARCHITECTURE.md](docs/development/ARCHITECTURE.md)

**...внести вклад:**
→ [docs/development/CONTRIBUTING.md](docs/development/CONTRIBUTING.md)

**...настроить email:**
→ [docs/deployment/EMAIL_SMTP_SETUP.md](docs/deployment/EMAIL_SMTP_SETUP.md)

**...решить проблему:**
→ [docs/deployment/TROUBLESHOOTING.md](docs/deployment/TROUBLESHOOTING.md)

---

**Последнее обновление:** 22 января 2026
