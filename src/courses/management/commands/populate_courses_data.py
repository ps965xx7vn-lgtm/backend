"""
Management команда для создания тестовых курсов с реальным содержимым.

Использование:
    python manage.py populate_courses_data
    python manage.py populate_courses_data --clear  # Очистить старые данные
"""

from decimal import Decimal

from django.core.management.base import BaseCommand

from courses.models import Course


class Command(BaseCommand):
    help = "Создает тестовые курсы с реальным содержимым"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Очистить существующие курсы перед созданием",
        )

    def handle(self, *args, **options):
        """Создает набор тестовых курсов"""

        if options["clear"]:
            self.stdout.write(self.style.WARNING("Очистка существующих данных..."))
            Course.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("✓ Данные очищены\n"))

        self.stdout.write(self.style.HTTP_INFO("=== СОЗДАНИЕ КУРСОВ ===\n"))

        # Категории доступны в модели: 'python', 'javascript', 'web', 'data-science', 'other'
        courses_data = [
            {
                "name": "Python для начинающих",
                "slug": "python-beginners",
                "description": "Изучите основы программирования на Python с нуля. Курс охватывает синтаксис, структуры данных, ООП и практические проекты. Вы научитесь писать чистый и эффективный код, работать с файлами, создавать свои модули и пакеты.",
                "short_description": "Полный курс по основам Python для начинающих разработчиков",
                "category": "python",
                "price": Decimal("9900.00"),
                "rating": Decimal("4.8"),
                "is_featured": True,
            },
            {
                "name": "Django: Разработка веб-приложений",
                "slug": "django-web-apps",
                "description": "Полный курс по Django Framework. Создайте профессиональные веб-приложения с использованием лучших практик. Изучите модели, представления, формы, аутентификацию, REST API и деплой приложений.",
                "short_description": "Профессиональная разработка веб-приложений на Django",
                "category": "web",
                "price": Decimal("14900.00"),
                "rating": Decimal("4.9"),
                "is_featured": True,
            },
            {
                "name": "Machine Learning на Python",
                "slug": "ml-python",
                "description": "Изучите машинное обучение с нуля. Scikit-learn, TensorFlow, pandas, numpy и практические кейсы. Научитесь создавать модели предсказания, классификации и кластеризации данных.",
                "short_description": "Практический курс по машинному обучению",
                "category": "data-science",
                "price": Decimal("19900.00"),
                "rating": Decimal("4.7"),
                "is_featured": False,
            },
            {
                "name": "JavaScript: От основ до продвинутого уровня",
                "slug": "javascript-advanced",
                "description": "Полное погружение в JavaScript. Изучите ES6+, асинхронность, промисы, async/await, замыкания, прототипы и современные паттерны разработки.",
                "short_description": "Глубокое изучение JavaScript для фронтенд-разработки",
                "category": "javascript",
                "price": Decimal("12900.00"),
                "rating": Decimal("4.8"),
                "is_featured": False,
            },
            {
                "name": "React и современный фронтенд",
                "slug": "react-frontend",
                "description": "Современная фронтенд разработка с React. Изучите компоненты, хуки, контекст, роутинг, состояние приложения. Создайте полноценное SPA с Redux и TypeScript.",
                "short_description": "React, TypeScript, Redux и современные инструменты",
                "category": "javascript",
                "price": Decimal("16900.00"),
                "rating": Decimal("4.9"),
                "is_featured": True,
            },
            {
                "name": "FastAPI: Современные API на Python",
                "slug": "fastapi-course",
                "description": "Создание высокопроизводительных API с FastAPI. Изучите асинхронное программирование, валидацию данных с Pydantic, работу с базами данных и документированием API.",
                "short_description": "Разработка современных API с FastAPI",
                "category": "python",
                "price": Decimal("13900.00"),
                "rating": Decimal("4.8"),
                "is_featured": False,
            },
            {
                "name": "Data Analysis с Pandas и NumPy",
                "slug": "data-analysis-pandas",
                "description": "Анализ данных на Python. Научитесь работать с pandas, numpy, matplotlib для обработки и визуализации данных. Практические кейсы с реальными датасетами.",
                "short_description": "Практический анализ данных с Pandas",
                "category": "data-science",
                "price": Decimal("11900.00"),
                "rating": Decimal("4.7"),
                "is_featured": False,
            },
            {
                "name": "Full Stack Web Development",
                "slug": "fullstack-web",
                "description": "Комплексный курс по Full Stack разработке. Python/Django на бэкенде, React на фронтенде, PostgreSQL, Redis, Docker. Создайте полноценное веб-приложение от начала до конца.",
                "short_description": "Полный стек веб-разработки: Python, React, Docker",
                "category": "web",
                "price": Decimal("24900.00"),
                "rating": Decimal("5.0"),
                "is_featured": True,
            },
            {
                "name": "Python для автоматизации",
                "slug": "python-automation",
                "description": "Автоматизируйте рутинные задачи с Python. Работа с файлами, веб-скрапинг, автоматизация браузера, работа с API, создание ботов и скриптов для повседневных задач.",
                "short_description": "Автоматизация задач и создание полезных скриптов",
                "category": "python",
                "price": Decimal("8900.00"),
                "rating": Decimal("4.6"),
                "is_featured": False,
            },
            {
                "name": "Алгоритмы и структуры данных на Python",
                "slug": "algorithms-python",
                "description": "Изучите классические алгоритмы и структуры данных. Сортировки, поиск, графы, деревья, динамическое программирование. Подготовка к техническим собеседованиям.",
                "short_description": "Алгоритмы, структуры данных и подготовка к собеседованиям",
                "category": "other",
                "price": Decimal("15900.00"),
                "rating": Decimal("4.9"),
                "is_featured": False,
            },
        ]

        created_count = 0
        updated_count = 0

        for course_data in courses_data:
            course, created = Course.objects.get_or_create(
                slug=course_data["slug"], defaults=course_data
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"✓ Создан курс: {course.name}"))
            else:
                updated_count += 1
                self.stdout.write(f"↻ Курс уже существует: {course.name}")

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"Создано курсов: {created_count}"))
        self.stdout.write(self.style.WARNING(f"Уже существовало: {updated_count}"))
        self.stdout.write(self.style.SUCCESS("✓ Курсы успешно добавлены!"))
