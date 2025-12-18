"""
Management команда для наполнения БД курсами

Использование:
    python manage.py populate_courses
"""

from django.core.management.base import BaseCommand

from courses.models import Course


class Command(BaseCommand):
    help = "Наполняет БД тестовыми курсами"

    def handle(self, *args, **options):
        self.stdout.write("Создание курсов...")

        courses_data = [
            {
                "name": "Python для начинающих",
                "slug": "python-beginners",
                "short_description": "Изучите основы Python с нуля. Переменные, функции, ООП и практические проекты.",
                "description": "Комплексный курс по основам Python для тех, кто только начинает свой путь в программировании. Вы изучите синтаксис, типы данных, функции, ООП и создадите несколько практических проектов.",
                "category": "python",
                "price": 0.00,
                "rating": 4.9,
                "is_featured": True,
            },
            {
                "name": "Django веб-разработка",
                "slug": "django-web-development",
                "short_description": "Создайте полноценные веб-приложения на Django. От основ до деплоя проекта.",
                "description": "Научитесь создавать современные веб-приложения на Django. Изучите работу с базами данных, аутентификацию, REST API и деплой на production.",
                "category": "web",
                "price": 0.00,
                "rating": 4.8,
                "is_featured": True,
            },
            {
                "name": "JavaScript: основы и практика",
                "slug": "javascript-fundamentals",
                "short_description": "Освойте JavaScript от базовых концепций до современных возможностей ES6+.",
                "description": "Полный курс по JavaScript для начинающих и продолжающих. Изучите основы языка, DOM, асинхронное программирование и современные фреймворки.",
                "category": "javascript",
                "price": 0.00,
                "rating": 4.7,
                "is_featured": False,
            },
            {
                "name": "Git и GitHub для разработчиков",
                "slug": "git-github-basics",
                "short_description": "Научитесь профессионально работать с системой контроля версий Git и платформой GitHub.",
                "description": "Изучите Git с нуля до продвинутого уровня. Ветвление, слияние, работа в команде, GitHub Flow и best practices.",
                "category": "other",
                "price": 0.00,
                "rating": 4.9,
                "is_featured": False,
            },
            {
                "name": "Python для анализа данных",
                "slug": "python-data-analysis",
                "short_description": "Pandas, NumPy, Matplotlib - всё для работы с данными на Python.",
                "description": "Освойте инструменты data science на Python. Работа с данными, визуализация, статистический анализ и машинное обучение.",
                "category": "data-science",
                "price": 0.00,
                "rating": 4.8,
                "is_featured": True,
            },
            {
                "name": "Full Stack JavaScript",
                "slug": "fullstack-javascript",
                "short_description": "React, Node.js, Express, MongoDB - станьте full-stack разработчиком.",
                "description": "Комплексный курс по созданию современных веб-приложений. Frontend на React, Backend на Node.js, работа с базами данных и деплой.",
                "category": "javascript",
                "price": 0.00,
                "rating": 4.9,
                "is_featured": True,
            },
            {
                "name": "Современная веб-разработка",
                "slug": "modern-web-development",
                "short_description": "HTML5, CSS3, JavaScript, адаптивная вёрстка и современные инструменты.",
                "description": "Научитесь создавать современные адаптивные сайты. HTML5, CSS3, Flexbox, Grid, JavaScript, препроцессоры и инструменты разработки.",
                "category": "web",
                "price": 0.00,
                "rating": 4.7,
                "is_featured": False,
            },
        ]

        created_count = 0
        updated_count = 0

        for course_data in courses_data:
            course, created = Course.objects.update_or_create(
                slug=course_data["slug"], defaults=course_data
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"✓ Создан курс: {course.name}"))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f"↻ Обновлен курс: {course.name}"))

        self.stdout.write(
            self.style.SUCCESS(f"\nГотово! Создано: {created_count}, Обновлено: {updated_count}")
        )
