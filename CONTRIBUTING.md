# Contributing to Pyland Backend

Спасибо за интерес к проекту! Мы рады любому вкладу.

## Быстрый Старт

1. **Fork репозиторий**
2. **Clone свой fork:**

   ```bash
   git clone <https://github.com/YOUR_USERNAME/backend.git>
   cd backend
   ```

3. **Установите зависимости:**

   ```bash
   poetry install
   poetry run pre-commit install
   ```

4. **Создайте feature branch:**

   ```bash
   git checkout -b feature/your-feature-name
   ```

## Процесс Разработки

### 1. Настройка Окружения

См. подробности в [DEVELOPMENT.md](DEVELOPMENT.md)

```bash

# Копируем .env

cp .env.example .env

# Применяем миграции

poetry run python src/manage.py migrate

# Создаем роли

poetry run python src/manage.py create_roles
```text
### 2. Написание Кода

**Следуйте стандартам:**

- Black для форматирования (line-length=100)
- Type hints где возможно
- Docstrings на русском языке
- Комментарии на русском

**Пример:**

```python
def calculate_progress(student_id: int, course_id: int) -> dict:
    """
    Вычисляет прогресс студента по курсу.

    Args:
        student_id: ID студента
        course_id: ID курса

    Returns:
        dict: Словарь с данными прогресса

    Raises:
        Student.DoesNotExist: Если студент не найден
    """
    student = Student.objects.get(id=student_id)

    #

```text
### 3. Тестирование

**Обязательно пишите тесты для новой функциональности!**

```bash

# Запуск тестов

poetry run pytest

# С coverage

poetry run pytest --cov=src

# Конкретный модуль

poetry run pytest src/authentication/tests/
```text
**Структура тестов:**

```python
@pytest.mark.django_db
class TestYourFeature:
    def test_something(self, user, course):
        """Тестирует что-то важное."""

        # Arrange

        data = {...}

        # Act

        result = your_function(data)

        # Assert

        assert result.status == "success"
```text
### 4. Pre-commit Checks

Pre-commit hooks запускаются автоматически перед каждым коммитом:

```bash

# Ручной запуск всех проверок

poetry run pre-commit run --all-files

# Только для staged файлов

poetry run pre-commit run
```text
Что проверяется:

- ✅ Ruff linting + formatting
- ✅ Black code style
- ✅ isort import sorting
- ✅ Bandit security
- ✅ File quality (trailing whitespace, etc)
- ✅ Django version upgrades

### 5. Коммиты

**Используйте Conventional Commits:**

```bash

# Типы коммитов

feat:     Новая функциональность
fix:      Исправление бага
docs:     Документация
style:    Форматирование (не влияет на код)
refactor: Рефакторинг
test:     Добавление тестов
chore:    Обновление зависимостей, конфигурации
ci:       Изменения CI/CD
perf:     Улучшение производительности

# Примеры

git commit -m "feat: Add lesson submission workflow"
git commit -m "fix: Resolve cache invalidation issue"
git commit -m "docs: Update API documentation"
git commit -m "test: Add tests for review system"
```text
**Хороший коммит:**

- Понятный заголовок (до 72 символов)
- Описывает ЧТО и ПОЧЕМУ (не КАК)
- Один логический change

```bash
git commit -m "feat: Add email notifications for reviews

- Send email when review is completed
- Include improvement suggestions in email
- Add Celery task for async sending
- Add tests for notification logic

Closes #123"
```text
### 6. Pull Request

1. **Push в свой fork:**

   ```bash
   git push origin feature/your-feature-name
   ```

2. **Создайте PR на GitHub:**
   - Понятный title (как коммит)
   - Подробное описание изменений
   - Ссылки на связанные issues
   - Screenshots/GIFs если UI изменения

3. **PR Template:**

   ```markdown

   ## Описание

   Краткое описание изменений

   ## Тип изменений

   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update

   ## Тестирование

   - [ ] Юнит-тесты добавлены/обновлены
   - [ ] Все тесты проходят локально
   - [ ] Pre-commit hooks проходят

   ## Чеклист

   - [ ] Код следует стайлгайду
   - [ ] Документация обновлена
   - [ ] Нет конфликтов с main
   - [ ] CI checks проходят

   Closes #123
   ```

## Code Review Process

### Что проверяют reviewers

1. **Функциональность:**
   - Код делает то, что заявлено
   - Нет очевидных багов
   - Edge cases обработаны

2. **Качество кода:**
   - Читаемость и поддерживаемость
   - Нет дублирования
   - Правильное использование паттернов

3. **Тесты:**
   - Покрытие достаточное
   - Тесты проверяют правильные вещи
   - Тесты не хрупкие

4. **Документация:**
   - Docstrings актуальны
   - README обновлен если нужно
   - API docs корректны

5. **Performance:**
   - Нет N+1 queries
   - Правильное использование кэша
   - Async где нужно

### Ответ на review

```markdown
@reviewer спасибо за фидбек!

✅ Исправил N+1 query через select_related
✅ Добавил тесты для edge case
🔄 Переименовал функцию как предложил
❓ По поводу кэширования - какой TTL лучше использовать?
```text
## Разработка Features

### Новый API Endpoint

1. **Создать схему в `app/schemas.py`:**

```python
class FeatureOut(Schema):
    id: int
    name: str

class FeatureIn(Schema):
    name: str = Field(..., min_length=3)
```text
2. **Добавить endpoint в `app/api.py`:**

```python
@router.post("/features/", response=FeatureOut)
def create_feature(request, payload: FeatureIn):
    feature = Feature.objects.create(**payload.dict())
    return feature
```text
3. **Написать тесты:**

```python
def test_create_feature_api(api_client):
    response = api_client.post(
        "/api/features/",
        json={"name": "Test Feature"}
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Test Feature"
```text
### Новая Модель

1. **Определить в `app/models.py`:**

```python
class Feature(Model):
    """Описание модели на русском."""
    name = CharField(max_length=255)
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Фича"
        verbose_name_plural = "Фичи"
        ordering = ['-created_at']

    def __str__(self) -> str:
        return self.name
```text
2. **Создать миграцию:**

```bash
poetry run python src/manage.py makemigrations
poetry run python src/manage.py migrate
```text
3. **Зарегистрировать в admin:**

```python
@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
```text
4. **Создать factory:**

```python
class FeatureFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Feature

    name = factory.Faker('word')
```text
### Новый Celery Task

```python

# app/tasks.py

@shared_task(bind=True, max_retries=3)
def process_feature(self, feature_id: int) -> dict:
    """Обрабатывает фичу асинхронно."""
    try:
        feature = Feature.objects.get(id=feature_id)

        # Processing logic

        return {"status": "success"}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
```text
## Исправление Багов

### Процесс

1. **Создать issue** (если нет)
2. **Воспроизвести** баг локально
3. **Написать failing test**
4. **Исправить** код
5. **Убедиться что test проходит**
6. **Создать PR** с fix + test

### Пример

```python

# Bug: Cache not invalidated on update

# 1. Failing test

def test_cache_invalidation_on_update(article):
    cached = cache.get(f'article:{article.slug}')
    article.title = "Updated"
    article.save()
    assert cache.get(f'article:{article.slug}') is None

# 2. Fix

class Article(Model):
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete(f'article:{self.slug}')  # Add this
```text
## Performance Optimization

### Database Queries

```python

# ❌ Bad - N+1 queries

for article in Article.objects.all():
    print(article.author.name)  # Query per article!

# ✅ Good - 2 queries total

articles = Article.objects.select_related('author')
for article in articles:
    print(article.author.name)
```text
### Caching

```python

# ❌ Bad - cache key collision

cache_key = 'articles'  # Same for all queries!

# ✅ Good - unique keys

cache_key = f'articles:{category}:{page}:{lang}'
```text
### Async Tasks

```python

# ❌ Bad - blocking request

def view(request):
    send_email(user)  # Blocks!
    return response

# ✅ Good - async

def view(request):
    send_email.delay(user.id)  # Non-blocking
    return response
```text
## Security

### Обязательные проверки

1. **Авторизация:**

```python
@require_role(['manager'])  # Всегда проверяем роль
def sensitive_view(request):
    pass
```text
2. **Валидация:**

```python

# Pydantic схемы для всех inputs

class DataIn(Schema):
    email: EmailStr
    age: int = Field(..., ge=0, le=150)
```text
3. **SQL Injection:**

```python

# ❌ Bad

Article.objects.raw(f"SELECT * FROM articles WHERE id={request.GET['id']}")

# ✅ Good

Article.objects.get(id=request.GET['id'])
```text
4. **XSS:**

```django
{# ❌ Bad #}
{{ user_input|safe }}

{# ✅ Good - auto-escaped #}
{{ user_input }}
```text
## Documentation

### Что документировать

1. **Функции/методы:**

```python
def complex_function(arg1: int, arg2: str) -> dict:
    """
    Краткое описание.

    Args:
        arg1: Описание первого аргумента
        arg2: Описание второго

    Returns:
        dict: Что возвращает

    Raises:
        ValueError: Когда возникает
    """
```text
2. **API endpoints:**

```python
@router.get("/items/", response=List[ItemOut])
def list_items(
    request,
    category: str = None,  # Filter by category
    page: int = 1,         # Page number
):
    """
    Возвращает список items с пагинацией.

    Фильтры:

    - category: slug категории
    - page: номер страницы (default: 1)

    """
```text
3. **Модели:**

```python
class Item(Model):
    """
    Представляет item в системе.

    Fields:
        name: Название item
        category: Категория (FK)
        is_active: Активен ли item
    """
```text
## Release Process

1. **Обновить версию** в `pyproject.toml`
2. **Обновить CHANGELOG.md**
3. **Создать tag:**

   ```bash
   git tag -a v1.0.0 -m "Release v1.0.0"
   git push origin v1.0.0
   ```

4. **GitHub Release** с описанием изменений

## Получение Помощи

- **GitHub Issues** - для багов и feature requests
- **GitHub Discussions** - для вопросов
- **Documentation** - см. README.md, DEVELOPMENT.md, ARCHITECTURE.md

## Code of Conduct

- Будьте уважительны
- Конструктивная критика приветствуется
- Все PR рассматриваются одинаково

Спасибо за вклад в проект! 🚀
