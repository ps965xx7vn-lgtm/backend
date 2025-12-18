"""
Management команда для создания тестовых статей блога.

Использование:
    python manage.py populate_blog_data
    python manage.py populate_blog_data --clear  # Очистить старые данные
"""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from blog.models import Article, Category

User = get_user_model()


class Command(BaseCommand):
    help = "Создает тестовые статьи для блога"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Очистить существующие статьи перед созданием",
        )

    def handle(self, *args, **options):
        """Создает набор тестовых статей"""

        if options["clear"]:
            self.stdout.write(self.style.WARNING("Очистка существующих данных..."))
            Article.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("✓ Данные очищены\n"))

        self.stdout.write(self.style.HTTP_INFO("=== СОЗДАНИЕ БЛОГА ===\n"))

        # Создаём или получаем автора
        author, _ = User.objects.get_or_create(
            email="blog@pyland.dev",
            defaults={
                "first_name": "Блог",
                "last_name": "Автор",
                "is_staff": True,
            },
        )

        self.stdout.write(self.style.WARNING("Создание категорий блога...\n"))

        categories_data = [
            {
                "name": "Туториалы",
                "slug": "tutorials",
                "description": "Обучающие материалы и пошаговые руководства",
                "icon": "📚",
                "color": "#3498db",
            },
            {
                "name": "Новости",
                "slug": "news",
                "description": "Новости из мира программирования",
                "icon": "📰",
                "color": "#e74c3c",
            },
            {
                "name": "Кейсы",
                "slug": "cases",
                "description": "Реальные примеры и истории успеха",
                "icon": "💼",
                "color": "#2ecc71",
            },
            {
                "name": "Советы",
                "slug": "tips",
                "description": "Полезные советы и лайфхаки",
                "icon": "💡",
                "color": "#f39c12",
            },
            {
                "name": "Обзоры",
                "slug": "reviews",
                "description": "Обзоры технологий и инструментов",
                "icon": "⭐",
                "color": "#9b59b6",
            },
        ]

        categories = {}
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data["slug"], defaults=cat_data
            )
            categories[cat_data["slug"]] = category
            status = "✓" if created else "↻"
            self.stdout.write(f"{status} Категория: {category.name}")

        self.stdout.write("\n" + self.style.WARNING("Создание статей блога...\n"))

        articles_data = [
            {
                "title": "Начало работы с Django: Полное руководство для новичков",
                "slug": "django-getting-started",
                "subtitle": "Узнайте, как создать своё первое веб-приложение на Django",
                "content": """# Введение в Django

Django — это мощный веб-фреймворк на Python, который позволяет быстро создавать безопасные и масштабируемые веб-приложения.

## Установка Django

Установите Django с помощью pip:

```bash
pip install django
```

## Создание проекта

Создайте новый проект Django:

```bash
django-admin startproject myproject
cd myproject
python manage.py runserver
```

Теперь ваше приложение доступно по адресу http://127.0.0.1:8000/

## Структура проекта

Django создаёт следующую структуру:

- `manage.py` - утилита командной строки
- `settings.py` - настройки проекта
- `urls.py` - маршрутизация URL
- `wsgi.py` и `asgi.py` - точки входа для сервера

## Создание приложения

```bash
python manage.py startapp blog
```

## Модели данных

Определите модели в `models.py`:

```python
from django.db import models

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
```

## Миграции

Примените изменения к базе данных:

```bash
python manage.py makemigrations
python manage.py migrate
```

Готово! Вы создали свой первый Django проект.""",
                "excerpt": "Пошаговое руководство по созданию вашего первого веб-приложения на Django. От установки до первых моделей.",
                "category": categories["tutorials"],
                "difficulty": "beginner",
                "status": "published",
                "tags": ["Django", "Python", "Web", "Backend"],
                "views_count": 1250,
                "reading_time": 8,
            },
            {
                "title": "10 лучших практик Python для чистого кода",
                "slug": "python-best-practices",
                "subtitle": "Советы по написанию понятного и поддерживаемого кода",
                "content": '''# Лучшие практики Python

## 1. Используйте виртуальные окружения

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
```

## 2. Следуйте PEP 8

PEP 8 — это руководство по стилю кода Python.

```python
# Хорошо
def calculate_total(items):
    return sum(item.price for item in items)

# Плохо
def calcTotal(items):
    total=0
    for i in items:total+=i.price
    return total
```

## 3. Используйте list comprehensions

```python
# Хорошо
squares = [x**2 for x in range(10)]

# Плохо
squares = []
for x in range(10):
    squares.append(x**2)
```

## 4. Документируйте код

```python
def fetch_user_data(user_id: int) -> dict:
    """
    Получает данные пользователя по ID.

    Args:
        user_id: Уникальный идентификатор пользователя

    Returns:
        Словарь с данными пользователя
    """
    pass
```

## 5. Используйте context managers

```python
with open('file.txt', 'r') as f:
    data = f.read()
```

## 6. Обрабатывайте исключения правильно

```python
try:
    result = risky_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    raise
```

## 7. Используйте type hints

```python
def greet(name: str) -> str:
    return f"Hello, {name}!"
```

## 8. Пишите тесты

```python
def test_calculate_total():
    items = [Item(price=100), Item(price=200)]
    assert calculate_total(items) == 300
```

## 9. Используйте виртуальные окружения

Изолируйте зависимости проектов друг от друга.

## 10. Логируйте, а не print()

```python
import logging

logger = logging.getLogger(__name__)
logger.info("Operation completed")
```

Следуя этим практикам, вы напишете более качественный код!''',
                "excerpt": "Узнайте 10 важнейших практик Python, которые сделают ваш код чище, понятнее и профессиональнее.",
                "category": categories["tips"],
                "difficulty": "intermediate",
                "status": "published",
                "tags": ["Python", "Best Practices", "Clean Code"],
                "views_count": 3420,
                "reading_time": 6,
            },
            {
                "title": "FastAPI vs Django: Что выбрать в 2025?",
                "slug": "fastapi-vs-django-2025",
                "subtitle": "Сравнение двух популярных Python фреймворков",
                "content": """# FastAPI vs Django

## Django

**Преимущества:**
- Полнофункциональный фреймворк ("batteries included")
- ORM, аутентификация, админка из коробки
- Огромное сообщество
- Стабильность и надёжность

**Недостатки:**
- Медленнее FastAPI
- Больше кода для API
- Сложнее асинхронность

## FastAPI

**Преимущества:**
- Очень быстрый (асинхронный)
- Автоматическая документация API
- Type hints и валидация с Pydantic
- Современный подход

**Недостатки:**
- Нет встроенной админки
- Меньше готовых решений
- Нужно больше настраивать

## Когда выбрать Django

- Полноценное веб-приложение
- Нужна админка
- Важна стабильность

## Когда выбрать FastAPI

- REST API или микросервисы
- Высокая производительность
- Асинхронная обработка

```python
# Django
from django.http import JsonResponse

def get_users(request):
    users = User.objects.all()
    return JsonResponse({'users': list(users)})

# FastAPI
from fastapi import FastAPI

app = FastAPI()

@app.get("/users")
async def get_users():
    return {"users": await fetch_users()}
```

Выбор зависит от ваших задач!""",
                "excerpt": "Детальное сравнение Django и FastAPI. Разбираем преимущества, недостатки и ситуации, когда лучше выбрать каждый из фреймворков.",
                "category": categories["reviews"],
                "difficulty": "intermediate",
                "status": "published",
                "tags": ["Django", "FastAPI", "Python", "Backend"],
                "views_count": 5230,
                "reading_time": 10,
            },
            {
                "title": "Docker для Python разработчиков",
                "slug": "docker-for-python-developers",
                "subtitle": "Контейнеризация Python приложений",
                "content": """# Docker для Python

## Что такое Docker?

Docker позволяет упаковать приложение и все его зависимости в контейнер.

## Dockerfile для Django

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "myproject.wsgi:application"]
```

## docker-compose.yml

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db/dbname
    depends_on:
      - db

  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_PASSWORD=password

volumes:
  postgres_data:
```

## Запуск

```bash
docker-compose up --build
```

Ваше приложение теперь в контейнере!""",
                "excerpt": "Научитесь контейнеризировать ваши Python приложения с Docker. Полное руководство от Dockerfile до docker-compose.",
                "category": categories["tutorials"],
                "difficulty": "intermediate",
                "status": "published",
                "tags": ["Docker", "Python", "DevOps", "Deploy"],
                "views_count": 2890,
                "reading_time": 12,
            },
            {
                "title": "Асинхронное программирование в Python",
                "slug": "async-python-guide",
                "subtitle": "Asyncio, async/await и многое другое",
                "content": """# Асинхронный Python

## Зачем нужна асинхронность?

Асинхронность позволяет эффективно обрабатывать множество задач одновременно.

## Основы asyncio

```python
import asyncio

async def fetch_data(url):
    # Симуляция HTTP запроса
    await asyncio.sleep(1)
    return f"Data from {url}"

async def main():
    tasks = [
        fetch_data("api.example.com/users"),
        fetch_data("api.example.com/posts"),
        fetch_data("api.example.com/comments"),
    ]
    results = await asyncio.gather(*tasks)
    print(results)

asyncio.run(main())
```

## Async/await

```python
async def process_data():
    data = await fetch_data()
    result = await transform_data(data)
    await save_result(result)
```

## Асинхронные HTTP запросы

```python
import aiohttp

async def fetch_url(session, url):
    async with session.get(url) as response:
        return await response.json()

async def main():
    async with aiohttp.ClientSession() as session:
        data = await fetch_url(session, "https://api.example.com")
```

## FastAPI и асинхронность

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/data")
async def get_data():
    result = await expensive_operation()
    return {"result": result}
```

Асинхронность значительно повышает производительность!""",
                "excerpt": "Полное руководство по асинхронному программированию в Python. Asyncio, async/await, aiohttp и практические примеры.",
                "category": categories["tutorials"],
                "difficulty": "advanced",
                "status": "published",
                "tags": ["Python", "Async", "Asyncio", "Performance"],
                "views_count": 4120,
                "reading_time": 15,
            },
        ]

        created_count = 0
        updated_count = 0
        now = timezone.now()

        for i, article_data in enumerate(articles_data):
            # Удаляем tags из данных для get_or_create
            tags = article_data.pop("tags", [])

            # Устанавливаем дату публикации (последние 30 дней)
            article_data["published_at"] = now - timedelta(days=30 - i * 3)
            article_data["author"] = author

            article, created = Article.objects.get_or_create(
                slug=article_data["slug"], defaults=article_data
            )

            # Добавляем теги через taggit
            if tags:
                article.tags.add(*tags)

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"✓ Создана статья: {article.title}"))
            else:
                updated_count += 1
                self.stdout.write(f"↻ Статья уже существует: {article.title}")

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"Создано статей: {created_count}"))
        self.stdout.write(self.style.WARNING(f"Уже существовало: {updated_count}"))
        self.stdout.write(self.style.SUCCESS("✓ Блог успешно наполнен!"))
