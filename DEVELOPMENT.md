# Локальная Разработка

Руководство по настройке локального окружения для разработки Pyland Backend.

## Предварительные Требования

- Python 3.13+
- Poetry 1.8+
- PostgreSQL 15+ (для продакшена) или SQLite (для разработки)
- Redis 7+ (опционально, для кэширования)
- Git

## Быстрый Старт

### 1. Клонирование репозитория

```bash
git clone https://github.com/ps965xx7vn-lgtm/backend.git pyland-backend
cd pyland-backend
```

### 2. Установка зависимостей

```bash
# Установка всех зависимостей (включая dev)
poetry install

# Только production зависимости
poetry install --without dev
```

### 3. Настройка окружения

Создайте `.env` файл из примера:

```bash
cp .env.example .env
```

Отредактируйте `.env` под ваши нужды:

```env
# Django
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite для разработки)
DATABASE_URL=sqlite:///src/db.sqlite3

# Или PostgreSQL
# DATABASE_URL=postgresql://user:password@localhost:5432/pyland

# Redis (опционально)
REDIS_URL=redis://localhost:6379/0

# Email (для разработки используйте console backend)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
```

### 4. Инициализация базы данных

```bash
poetry run python src/manage.py migrate
poetry run python src/manage.py create_roles
poetry run python src/manage.py createsuperuser
```

### 5. Загрузка тестовых данных (опционально)

```bash
poetry run python src/manage.py populate_courses_data
poetry run python src/manage.py populate_blog_data
```

### 6. Запуск сервера

```bash
# Вариант 1: С активацией virtualenv
poetry shell
cd src
python manage.py runserver

# Вариант 2: Без активации
poetry run python src/manage.py runserver
```

Приложение доступно по адресу: http://localhost:8000

## Разработка

### Pre-commit Hooks

Установите git hooks для автоматической проверки кода перед коммитом:

```bash
poetry run pre-commit install
```

Ручной запуск проверок:

```bash
# На всех файлах
poetry run pre-commit run --all-files

# На staged файлах
poetry run pre-commit run
```

### Форматирование Кода

```bash
# Black
poetry run black src/

# isort
poetry run isort src/

# Ruff (линтинг + автофикс)
poetry run ruff check src/ --fix
```

### Тестирование

```bash
# Все тесты
poetry run pytest

# Конкретное приложение
poetry run pytest src/authentication/tests/

# С coverage
poetry run pytest --cov=src --cov-report=html

# Параллельно (быстрее)
poetry run pytest -n auto

# С verbose output
poetry run pytest -v --tb=short
```

### Линтинг и Проверки

```bash
# Ruff
poetry run ruff check src/

# MyPy (проверка типов)
poetry run mypy src/

# Безопасность
poetry run safety check
poetry run bandit -r src/

# Сложность кода
poetry run radon cc src/ -a -nb
```

### Работа с Celery

Запуск Celery worker (в отдельном терминале):

```bash
# Redis должен быть запущен
redis-server

# Worker
poetry run celery -A pyland worker -l info

# Beat scheduler (для периодических задач)
poetry run celery -A pyland beat -l info

# Все вместе (только для разработки)
poetry run celery -A pyland worker -B -l info
```

### Переводы (i18n)

```bash
# Создание сообщений
poetry run python src/manage.py makemessages -l en
poetry run python src/manage.py makemessages -l ka

# Компиляция
poetry run python src/manage.py compilemessages
```

## Структура Проекта

```
pyland-backend/
├── .github/              # GitHub Actions workflows
│   └── workflows/
│       ├── ci.yml       # Основной CI pipeline
│       ├── pr-checks.yml # PR validation
│       ├── docs.yml     # Documentation checks
│       └── dependency-updates.yml # Auto-updates
├── src/                 # Django проект
│   ├── authentication/  # Аутентификация и роли
│   ├── blog/           # Блог
│   ├── courses/        # Курсы и уроки
│   ├── students/       # Студенческий дашборд
│   ├── reviewers/      # Система ревью
│   ├── managers/       # Админ панель
│   ├── pyland/         # Настройки Django
│   └── manage.py
├── pyproject.toml      # Poetry конфигурация
├── pytest.ini          # Pytest настройки
├── .pre-commit-config.yaml # Pre-commit hooks
└── README.md

```

## Полезные Команды

### Django Management

```bash
# Создать миграции
poetry run python src/manage.py makemigrations

# Применить миграции
poetry run python src/manage.py migrate

# Django shell
poetry run python src/manage.py shell

# Создать суперпользователя
poetry run python src/manage.py createsuperuser

# Собрать статику
poetry run python src/manage.py collectstatic --no-input

# Проверка системы
poetry run python src/manage.py check
```

### Custom Management Commands

```bash
# Создание ролей
poetry run python src/manage.py create_roles

# Тестовые данные
poetry run python src/manage.py populate_courses_data
poetry run python src/manage.py populate_blog_data

# Генерация sitemap
poetry run python src/manage.py generate_sitemap

# Статистика
poetry run python src/manage.py show_stats
```

### Poetry

```bash
# Добавить зависимость
poetry add package-name

# Добавить dev зависимость
poetry add --group dev package-name

# Обновить зависимости
poetry update

# Показать зависимости
poetry show

# Экспорт requirements.txt
poetry export -f requirements.txt --output requirements.txt
```

## Отладка

### Django Debug Toolbar

Debug Toolbar доступен в режиме `DEBUG=True` по адресу http://localhost:8000

### Логирование

Логи находятся в `src/logs/`:
- `django.log` - основной лог
- `celery.log` - Celery tasks

### База данных

```bash
# SQLite
poetry run python src/manage.py dbshell

# PostgreSQL
psql -U postgres -d pyland
```

## Производительность

### Кэширование

Redis используется для:
- Кэширование представлений
- Прогресс студентов
- Статистика блога
- Celery broker

Очистка кэша:

```bash
poetry run python src/manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()
```

### Мониторинг Запросов

```python
# В Django shell
from django.db import connection
print(len(connection.queries))  # Количество запросов
print(connection.queries)        # Детали запросов
```

## Troubleshooting

### Redis не доступен

Если Redis не запущен, проект использует dummy cache (в памяти). Для полного функционала запустите Redis:

```bash
# macOS
brew services start redis

# Linux
sudo systemctl start redis
```

### Проблемы с миграциями

```bash
# Откатить последнюю миграцию
poetry run python src/manage.py migrate app_name 0001_previous_migration

# Пересоздать миграции (только для разработки!)
rm -rf src/*/migrations/0*.py
poetry run python src/manage.py makemigrations
poetry run python src/manage.py migrate
```

### Конфликты зависимостей

```bash
# Очистить lock file и пересобрать
rm poetry.lock
poetry lock
poetry install
```

## CI/CD

### Локальное Тестирование CI

Проверьте код перед пушем:

```bash
# Форматирование
poetry run black src/ --check
poetry run isort src/ --check-only

# Линтинг
poetry run ruff check src/

# Тесты
poetry run pytest --cov=src

# Безопасность
poetry run safety check
poetry run bandit -r src/

# Все проверки сразу (как в CI)
poetry run pre-commit run --all-files
```

### Secrets для CI

Для работы CI нужны secrets в GitHub:
- `CODECOV_TOKEN` - для загрузки coverage (опционально)

## Дополнительные Ресурсы

- [GitHub Repository](https://github.com/ps965xx7vn-lgtm/backend)
- [CI/CD Documentation](.github/CI_README.md)
- [GitHub Setup](GITHUB_SETUP.md)
- [Authentication README](src/authentication/README.md)
- [Blog README](src/blog/README.md)
