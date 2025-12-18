from django.core.management.base import BaseCommand

from authentication.models import User
from blog.models import Article, Author, Category


class Command(BaseCommand):
    help = "Populate blog with articles"

    def handle(self, *args, **kwargs):
        # Получаем или создаём автора
        admin_user, _ = User.objects.get_or_create(
            email="admin@pyschool.ru",
            defaults={
                "username": "admin",
                "first_name": "Администратор",
                "is_staff": True,
                "is_superuser": True,
            },
        )

        author, _ = Author.objects.get_or_create(
            user=admin_user,
            defaults={
                "display_name": "Команда PySchool",
                "bio": "Образовательная платформа для изучения программирования",
                "is_featured": True,
            },
        )

        # Создаём категории
        categories_data = [
            {"name": "Python", "slug": "python", "description": "Статьи о языке Python"},
            {"name": "Django", "slug": "django", "description": "Фреймворк Django"},
            {"name": "JavaScript", "slug": "javascript", "description": "Язык JavaScript"},
            {
                "name": "Web Development",
                "slug": "web-dev",
                "description": "Статьи о веб-разработке",
            },
            {"name": "Git", "slug": "git", "description": "Система контроля версий Git"},
        ]

        categories = {}
        for cat_data in categories_data:
            cat, created = Category.objects.get_or_create(slug=cat_data["slug"], defaults=cat_data)
            categories[cat_data["slug"]] = cat
            if created:
                self.stdout.write(self.style.SUCCESS(f"✓ Создана категория: {cat.name}"))
            else:
                self.stdout.write(f"↻ Категория уже существует: {cat.name}")

        # Создаём статьи
        articles_data = [
            {
                "title": "Начало работы с Python",
                "slug": "getting-started-with-python",
                "category": "python",
                "excerpt": "Введение в Python для начинающих: установка, первая программа и основные концепции.",
                "content": """# Начало работы с Python

Python - один из самых популярных языков программирования в мире. В этой статье мы рассмотрим, как начать работу с Python.

## Установка Python

1. Скачайте Python с официального сайта python.org
2. Установите Python на ваш компьютер
3. Проверьте установку командой: `python --version`

## Первая программа

```python
print("Hello, World!")
```

## Основные концепции

- Переменные
- Типы данных
- Функции
- Циклы и условия

Python - отличный выбор для начинающих программистов!
""",
                "status": "published",
                "reading_time": 5,
            },
            {
                "title": "Django: создание веб-приложений",
                "slug": "django-web-apps",
                "category": "django",
                "excerpt": "Узнайте, как создавать мощные веб-приложения с помощью Django - популярного Python-фреймворка.",
                "content": """# Django: создание веб-приложений

Django - это высокоуровневый Python веб-фреймворк, который упрощает создание сложных веб-приложений.

## Преимущества Django

- ORM для работы с базами данных
- Встроенная панель администратора
- Система аутентификации
- Защита от распространённых уязвимостей

## Создание проекта

```bash
django-admin startproject myproject
cd myproject
python manage.py runserver
```

## MVT архитектура

Django использует архитектуру Model-View-Template:

- **Model**: работа с данными
- **View**: бизнес-логика
- **Template**: отображение

Django - отличный выбор для быстрой разработки веб-приложений!
""",
                "status": "published",
                "reading_time": 8,
            },
            {
                "title": "JavaScript для начинающих",
                "slug": "javascript-for-beginners",
                "category": "javascript",
                "excerpt": "Основы JavaScript: синтаксис, переменные, функции и работа с DOM.",
                "content": """# JavaScript для начинающих

JavaScript - язык программирования для веб-разработки. Он делает веб-страницы интерактивными.

## Основы синтаксиса

```javascript
// Переменные
let name = "John";
const age = 25;

// Функции
function greet(name) {
    return `Hello, ${name}!`;
}

// Массивы
let numbers = [1, 2, 3, 4, 5];
```

## Работа с DOM

```javascript
// Выбор элементов
document.getElementById('myId');
document.querySelector('.myClass');

// Изменение содержимого
element.textContent = 'New text';
element.innerHTML = '<p>HTML content</p>';
```

## События

```javascript
button.addEventListener('click', function() {
    alert('Button clicked!');
});
```

JavaScript - основа современной веб-разработки!
""",
                "status": "published",
                "reading_time": 6,
            },
            {
                "title": "Git и GitHub: основы",
                "slug": "git-github-basics",
                "category": "git",
                "excerpt": "Изучите основы работы с Git и GitHub для эффективного управления версиями кода.",
                "content": """# Git и GitHub: основы

Git - распределённая система контроля версий. GitHub - платформа для хостинга Git-репозиториев.

## Основные команды Git

```bash
# Инициализация репозитория
git init

# Добавление файлов
git add .

# Создание коммита
git commit -m "Initial commit"

# Отправка на GitHub
git push origin main
```

## Работа с ветками

```bash
# Создание ветки
git branch feature

# Переключение на ветку
git checkout feature

# Слияние веток
git merge feature
```

## Полезные команды

```bash
git status
git log
git diff
git pull
```

Git и GitHub - необходимые инструменты для любого разработчика!
""",
                "status": "published",
                "reading_time": 7,
            },
            {
                "title": "Современная веб-разработка",
                "slug": "modern-web-development",
                "category": "web-dev",
                "excerpt": "Обзор современных технологий и подходов в веб-разработке.",
                "content": """# Современная веб-разработка

Веб-разработка постоянно развивается. Рассмотрим современные технологии и подходы.

## Frontend

- **React**: библиотека для создания UI
- **Vue.js**: прогрессивный фреймворк
- **TypeScript**: типизированный JavaScript

## Backend

- **Django**: Python веб-фреймворк
- **Node.js**: JavaScript на сервере
- **FastAPI**: современный Python фреймворк

## Базы данных

- **PostgreSQL**: реляционная БД
- **MongoDB**: документо-ориентированная БД
- **Redis**: кэширование данных

## DevOps

- **Docker**: контейнеризация
- **CI/CD**: автоматизация
- **Kubernetes**: оркестрация

Современная веб-разработка требует знания множества технологий!
""",
                "status": "published",
                "reading_time": 10,
            },
        ]

        for article_data in articles_data:
            category_slug = article_data.pop("category")
            category = categories[category_slug]

            article, created = Article.objects.get_or_create(
                slug=article_data["slug"],
                defaults={
                    **article_data,
                    "author": admin_user,  # Используем User, а не Author
                    "category": category,
                },
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"✓ Создана статья: {article.title}"))
            else:
                self.stdout.write(f"↻ Статья уже существует: {article.title}")

        self.stdout.write(self.style.SUCCESS("\n✅ Статьи успешно созданы!"))
