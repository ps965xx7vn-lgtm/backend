# Contributing to Pyland Backend

Спасибо за интерес к проекту! Мы рады любому вкладу.

## 📚 Документация

Перед началом работы ознакомьтесь с:

- **[GIT_WORKFLOW.md](./GIT_WORKFLOW.md)** — полное руководство по Git Flow, commit guidelines, PR процессу
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** — архитектура проекта, структура кода
- **[DOCKER_HUB_SETUP.md](./DOCKER_HUB_SETUP.md)** — настройка Docker и деплой
- **[README.md](./README.md)** — общая информация и quick start

## 🚀 Быстрый Старт

### 1. Fork и Clone

```bash
# Fork репозиторий через GitHub UI

# Clone свой fork
git clone https://github.com/YOUR_USERNAME/backend.git
cd backend

# Добавить upstream remote
git remote add upstream https://github.com/ps965xx7vn-lgtm/backend.git
```

### 2. Установка окружения

```bash
# Установить зависимости через Poetry
poetry install

# Установить pre-commit hooks
poetry run pre-commit install

# Скопировать .env
cp .env.example .env

# Запустить БД и Redis (Docker)
docker-compose up -d db redis

# Применить миграции
poetry run python src/manage.py migrate

# Создать роли
poetry run python src/manage.py create_roles

# Создать superuser
poetry run python src/manage.py createsuperuser
```

### 3. Создать feature branch

```bash
# Обновить dev
git checkout dev
git pull upstream dev

# Создать feature branch
git checkout -b feature/your-feature-name
```

## 💻 Процесс Разработки

### 1. Code Style

**Автоматическое форматирование** (через pre-commit):

- **ruff** — linting
- **black** — code formatting (line-length=100)
- **isort** — import sorting
- **mypy** — type checking

**Правила:**

```python
# ✅ Хорошо
def get_student_progress(student_id: int, course_id: int) -> dict[str, Any]:
    """
    Получает прогресс студента по курсу.

    Args:
        student_id: ID студента
        course_id: ID курса

    Returns:
        Словарь с данными прогресса

    Raises:
        Student.DoesNotExist: Если студент не найден
    """
    student = Student.objects.select_related('user').get(id=student_id)
    return calculate_progress(student, course_id)
```

### 2. Тестирование

**Обязательно** пишите тесты для новой функциональности!

```bash
# Запуск всех тестов
poetry run pytest

# С coverage report
poetry run pytest --cov=src --cov-report=html

# Конкретный модуль
poetry run pytest src/authentication/tests/

# Параллельно (быстрее)
poetry run pytest -n auto
```

### 3. Commit Messages

**Используйте Conventional Commits** (подробно в [GIT_WORKFLOW.md](./GIT_WORKFLOW.md)):

```bash
# Формат: <type>(<scope>): <subject>

# Примеры
feat(authentication): добавлена JWT аутентификация
fix(blog): исправлена пагинация статей
docs(api): обновлена документация endpoints
```

### 4. Pull Requests

**Перед созданием PR:**

```bash
# 1. Убедитесь что тесты проходят
poetry run pytest

# 2. Проверьте code quality
poetry run ruff check .
poetry run black --check .

# 3. Обновите ветку от upstream
git fetch upstream
git rebase upstream/dev

# 4. Push в свой fork
git push origin feature/your-feature-name
```

**Создание PR:**

```bash
gh pr create \
  --base dev \
  --head your-username:feature/your-feature-name \
  --title "feat: краткое описание" \
  --body "Подробное описание изменений..."
```

**PR Template:**

```markdown
## Описание
Что делает этот PR?

## Изменения
- Добавлено X
- Исправлено Y

## Тестирование
- [x] Unit тесты пройдены
- [x] Проверено вручную

## Чеклист
- [x] Код соответствует style guide
- [x] Тесты добавлены
- [x] Документация обновлена

Closes #123
```

## 🔍 Code Review Process

### Для автора PR

1. Отвечайте на комментарии быстро и конструктивно
2. Вносите изменения по замечаниям
3. Resolve conversations после исправления

### Для reviewer

1. Проверьте код внимательно
2. Оставляйте конструктивные комментарии
3. Approve когда всё в порядке

## 📋 Checklist перед Merge

- [ ] Все тесты пройдены (CI green)
- [ ] Code coverage не упал
- [ ] Нет конфликтов с base branch
- [ ] Получен approval от reviewer
- [ ] Документация обновлена

## 🐛 Баги и Issues

### Reporting Bugs

```markdown
**Описание бага:**
Что произошло?

**Как воспроизвести:**
1. Шаг 1
2. Шаг 2

**Ожидаемое поведение:**
Что должно было произойти?

**Окружение:**
- OS: macOS 14
- Python: 3.13
```

### Feature Requests

```markdown
**Описание фичи:**
Что хотите добавить?

**Зачем это нужно:**
Какую проблему решает?
```

## 📝 Документация

### API Документация

Django Ninja генерирует автоматическую документацию:

```bash
poetry run python src/manage.py runserver
open http://127.0.0.1:8000/api/docs
```

## 🤝 Community Guidelines

- Будьте уважительны к другим
- Конструктивная критика приветствуется
- Помогайте новичкам
- Нет токсичности

## 📚 Дополнительные Ресурсы

- [GIT_WORKFLOW.md](./GIT_WORKFLOW.md) — полный Git workflow guide
- [ARCHITECTURE.md](./ARCHITECTURE.md) — архитектура проекта
- [Django Ninja Docs](https://django-ninja.rest-framework.com/)
- [pytest-django Docs](https://pytest-django.readthedocs.io/)

---

**Спасибо за вклад в проект!** 🎉
