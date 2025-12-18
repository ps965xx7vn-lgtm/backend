# Pyland Backend

[![CI](https://github.com/ps965xx7vn-lgtm/backend/actions/workflows/ci.yml/badge.svg)](https://github.com/ps965xx7vn-lgtm/backend/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/ps965xx7vn-lgtm/backend/branch/main/graph/badge.svg)](https://codecov.io/gh/ps965xx7vn-lgtm/backend)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Django 5.2](https://img.shields.io/badge/django-5.2-green.svg)](https://www.djangoproject.com/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Django 5.2 онлайн школа программирования с многоролевой системой пользователей.

## Технологии

- Django 5.2 + Django Ninja (REST API)
- Python 3.13+
- PostgreSQL
- Redis + Celery
- JWT аутентификация
- Poetry для управления зависимостями

## Установка

```bash
# Установка зависимостей
poetry install

# Применение миграций
poetry run python src/manage.py migrate

# Создание ролей пользователей
poetry run python src/manage.py create_roles

# Создание суперпользователя
poetry run python src/manage.py createsuperuser

# Запуск сервера разработки
poetry run python src/manage.py runserver
```

## Альтернативный способ (с активацией virtualenv)

```bash
# Активировать Poetry virtualenv
poetry shell

# Перейти в папку src
cd src

# Выполнить команды напрямую
python manage.py migrate
python manage.py create_roles
python manage.py createsuperuser
python manage.py runserver
```

## Тестирование

```bash
# Вариант 1: Прямой запуск через Poetry
poetry run pytest

# Вариант 2: С coverage
poetry run pytest --cov=. --cov-report=html

# Вариант 3: С активацией virtualenv
poetry shell
cd src
pytest
pytest --cov=. --cov-report=html
```

## CI/CD

Проект использует GitHub Actions для автоматического тестирования и проверки качества кода.

См. [.github/CI_README.md](.github/CI_README.md) для подробностей.
