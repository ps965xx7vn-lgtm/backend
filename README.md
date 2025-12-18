# Pyland Backend

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
