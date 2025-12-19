# CI/CD Configuration

## GitHub Actions Workflows

### 1. Main CI Pipeline (`ci.yml`)

Запускается при push в `main` и `develop`, а также при Pull Requests.

**Jobs:**

- **test** - Основное тестирование
  - PostgreSQL 15 + Redis 7
  - Python 3.13 + Poetry
  - Линтинг (ruff)
  - Type checking (mypy)
  - Миграции БД
  - Компиляция переводов
  - Запуск тестов с coverage
  - Загрузка coverage на Codecov

- **security** - Проверка безопасности
  - Safety - проверка зависимостей на уязвимости
  - Bandit - статический анализ безопасности кода

- **code-quality** - Качество кода
  - Black - форматирование
  - isort - сортировка импортов

### 2. PR Checks (`pr-checks.yml`)

Дополнительные проверки для Pull Requests.

**Jobs:**

- **pr-validation**
  - Проверка конфликтов миграций
  - Валидация шаблонов
  - Проверка на непереведённые строки

- **complexity-check**
  - Цикломатическая сложность (radon)
  - Индекс поддерживаемости

## Локальный запуск проверок

### Установка зависимостей

```bash
poetry install
```text
### Запуск линтера

```bash
poetry run ruff check src/
```text
### Автофикс проблем линтера

```bash
poetry run ruff check src/ --fix
```text
### Форматирование кода

```bash
poetry run black src/
```text
### Сортировка импортов

```bash
poetry run isort src/
```text
### Type checking

```bash
poetry run mypy src/
```text
### Проверка безопасности

```bash
poetry run safety check
poetry run bandit -r src/
```text
### Запуск тестов

```bash
cd src
poetry run pytest
```text
### Тесты с coverage

```bash
cd src
poetry run pytest --cov=. --cov-report=html
```text
### Проверка миграций

```bash
cd src
poetry run python manage.py makemigrations --check --dry-run
```text
### Компиляция переводов

```bash
cd src
poetry run python manage.py compilemessages
```text
## Pre-commit хуки (опционально)

Для автоматической проверки перед коммитом можно настроить pre-commit:

```bash
pip install pre-commit
pre-commit install
```text
## Переменные окружения для CI

В GitHub Secrets нужно добавить:

- `CODECOV_TOKEN` - токен для Codecov (опционально)

## Требования для мерджа PR

1. ✅ Все тесты проходят
2. ✅ Coverage не падает
3. ✅ Линтер не находит ошибок
4. ✅ Type checking проходит
5. ✅ Нет конфликтов миграций
6. ✅ Code review approved

## Статусы CI

После настройки в GitHub можно увидеть статусы:

- ✅ CI / test - Основные тесты
- ✅ CI / security - Безопасность
- ✅ CI / code-quality - Качество кода
- ✅ PR Checks / pr-validation - Валидация PR
- ✅ PR Checks / complexity-check - Сложность кода
