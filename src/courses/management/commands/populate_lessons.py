from django.core.management.base import BaseCommand

from courses.models import Course, Lesson, Step


class Command(BaseCommand):
    help = "Populate courses with lessons and steps"

    def handle(self, *args, **kwargs):
        # Django веб-разработка
        django_course = Course.objects.filter(slug="django-web-development").first()
        if django_course:
            lessons_data = [
                {
                    "name": "Введение в Django",
                    "slug": "django-intro",
                    "lesson_number": 1,
                    "short_description": "Знакомство с фреймворком Django и его архитектурой MVT. Установка, создание проекта и изучение структуры.",
                    "steps": [
                        {
                            "name": "Установка Django",
                            "step_number": 1,
                            "content": "# Установка Django\n\npip install django",
                        },
                        {
                            "name": "Создание проекта",
                            "step_number": 2,
                            "content": "# Создание проекта\n\ndjango-admin startproject mysite",
                        },
                        {
                            "name": "Структура проекта",
                            "step_number": 3,
                            "content": "# Структура проекта Django\n\nРазбор файлов и директорий",
                        },
                    ],
                },
                {
                    "name": "Модели и базы данных",
                    "slug": "django-models",
                    "lesson_number": 2,
                    "short_description": "Работа с моделями Django и ORM. Создание моделей, миграции и работа с QuerySet API.",
                    "steps": [
                        {
                            "name": "Создание моделей",
                            "step_number": 1,
                            "content": "# Модели Django\n\nclass Post(models.Model):\n    title = models.CharField(max_length=200)",
                        },
                        {
                            "name": "Миграции",
                            "step_number": 2,
                            "content": "# Миграции\n\npython manage.py makemigrations\npython manage.py migrate",
                        },
                        {
                            "name": "QuerySet API",
                            "step_number": 3,
                            "content": "# QuerySet API\n\nPost.objects.all()\nPost.objects.filter(title__contains='Django')",
                        },
                        {
                            "name": "Связи между моделями",
                            "step_number": 4,
                            "content": "# ForeignKey, ManyToMany, OneToOne",
                        },
                    ],
                },
                {
                    "name": "Представления и URL",
                    "slug": "django-views-urls",
                    "lesson_number": 3,
                    "short_description": "Создание представлений и маршрутизация. Function-based и Class-based views.",
                    "steps": [
                        {
                            "name": "Function-based views",
                            "step_number": 1,
                            "content": "# FBV\n\ndef my_view(request):\n    return HttpResponse('Hello')",
                        },
                        {
                            "name": "Class-based views",
                            "step_number": 2,
                            "content": "# CBV\n\nclass MyView(View):\n    def get(self, request):\n        return HttpResponse('Hello')",
                        },
                        {
                            "name": "URL routing",
                            "step_number": 3,
                            "content": "# urls.py\n\npath('post/<int:pk>/', views.post_detail)",
                        },
                    ],
                },
                {
                    "name": "Шаблоны Django",
                    "slug": "django-templates",
                    "lesson_number": 4,
                    "short_description": "Работа с шаблонами и контекстом. Синтаксис, наследование и встроенные теги.",
                    "steps": [
                        {
                            "name": "Синтаксис шаблонов",
                            "step_number": 1,
                            "content": "# Templates\n\n{{ variable }}\n{% for item in list %}\n{% endfor %}",
                        },
                        {
                            "name": "Наследование шаблонов",
                            "step_number": 2,
                            "content": "# Template inheritance\n\n{% extends 'base.html' %}\n{% block content %}{% endblock %}",
                        },
                        {
                            "name": "Template tags и filters",
                            "step_number": 3,
                            "content": "# Tags and filters\n\n{{ value|date:'Y-m-d' }}\n{% if user.is_authenticated %}",
                        },
                    ],
                },
                {
                    "name": "Формы Django",
                    "slug": "django-forms",
                    "lesson_number": 5,
                    "short_description": "Создание и обработка форм. ModelForm, валидация данных и CSRF защита.",
                    "steps": [
                        {
                            "name": "ModelForm",
                            "step_number": 1,
                            "content": "# ModelForm\n\nclass PostForm(forms.ModelForm):\n    class Meta:\n        model = Post",
                        },
                        {
                            "name": "Валидация форм",
                            "step_number": 2,
                            "content": "# Form validation\n\ndef clean_email(self):\n    email = self.cleaned_data['email']",
                        },
                        {
                            "name": "CSRF защита",
                            "step_number": 3,
                            "content": "# CSRF\n\n{% csrf_token %}",
                        },
                    ],
                },
                {
                    "name": "Аутентификация и авторизация",
                    "slug": "django-auth",
                    "lesson_number": 6,
                    "short_description": "Система пользователей Django. Работа с User model, Login/Logout и правами доступа.",
                    "steps": [
                        {
                            "name": "User model",
                            "step_number": 1,
                            "content": "# User model\n\nfrom django.contrib.auth.models import User",
                        },
                        {
                            "name": "Login/Logout",
                            "step_number": 2,
                            "content": "# Authentication views\n\nLoginView, LogoutView",
                        },
                        {
                            "name": "Permissions",
                            "step_number": 3,
                            "content": "# Permissions\n\n@login_required\n@permission_required('blog.add_post')",
                        },
                    ],
                },
            ]

            for lesson_data in lessons_data:
                steps_data = lesson_data.pop("steps")
                lesson, created = Lesson.objects.update_or_create(
                    course=django_course, slug=lesson_data["slug"], defaults=lesson_data
                )

                for step_data in steps_data:
                    Step.objects.update_or_create(
                        lesson=lesson,
                        step_number=step_data["step_number"],
                        defaults={
                            "name": step_data["name"],
                            "description": step_data.get("content", ""),
                        },
                    )

                if created:
                    self.stdout.write(self.style.SUCCESS(f"✓ Created lesson: {lesson.name}"))
                else:
                    self.stdout.write(self.style.WARNING(f"⟳ Updated lesson: {lesson.name}"))

        # Python для начинающих
        python_course = Course.objects.filter(slug="python-beginners").first()
        if python_course:
            lessons_data = [
                {
                    "name": "Первые шаги в Python",
                    "slug": "python-first-steps",
                    "lesson_number": 1,
                    "short_description": "Установка Python и первая программа. Hello World, переменные и основы синтаксиса.",
                    "steps": [
                        {
                            "name": "Установка Python",
                            "step_number": 1,
                            "content": "# Установка Python\n\nСкачайте Python с python.org",
                        },
                        {
                            "name": "Hello World",
                            "step_number": 2,
                            "content": "# Hello World\n\nprint('Hello, World!')",
                        },
                        {
                            "name": "Переменные",
                            "step_number": 3,
                            "content": "# Variables\n\nname = 'Python'\nage = 30",
                        },
                    ],
                },
                {
                    "name": "Типы данных",
                    "slug": "python-data-types",
                    "lesson_number": 2,
                    "short_description": "Строки, числа, списки, словари. Изучите основные типы данных в Python.",
                    "steps": [
                        {
                            "name": "Числа",
                            "step_number": 1,
                            "content": "# Numbers\n\nx = 5\ny = 3.14",
                        },
                        {
                            "name": "Строки",
                            "step_number": 2,
                            "content": "# Strings\n\ntext = 'Python'\ntext.upper()",
                        },
                        {
                            "name": "Списки",
                            "step_number": 3,
                            "content": "# Lists\n\nmy_list = [1, 2, 3, 4, 5]",
                        },
                        {
                            "name": "Словари",
                            "step_number": 4,
                            "content": "# Dictionaries\n\nmy_dict = {'name': 'John', 'age': 30}",
                        },
                    ],
                },
                {
                    "name": "Условия и циклы",
                    "slug": "python-conditions-loops",
                    "lesson_number": 3,
                    "short_description": "If, for, while. Управление потоком выполнения программы.",
                    "steps": [
                        {
                            "name": "If условия",
                            "step_number": 1,
                            "content": "# If statement\n\nif x > 5:\n    print('x больше 5')",
                        },
                        {
                            "name": "For циклы",
                            "step_number": 2,
                            "content": "# For loop\n\nfor i in range(10):\n    print(i)",
                        },
                        {
                            "name": "While циклы",
                            "step_number": 3,
                            "content": "# While loop\n\nwhile x < 10:\n    x += 1",
                        },
                    ],
                },
                {
                    "name": "Функции",
                    "slug": "python-functions",
                    "lesson_number": 4,
                    "short_description": "Создание и использование функций. Научитесь создавать переиспользуемый код.",
                    "steps": [
                        {
                            "name": "Определение функции",
                            "step_number": 1,
                            "content": "# Functions\n\ndef greet(name):\n    return f'Hello, {name}!'",
                        },
                        {
                            "name": "Параметры и аргументы",
                            "step_number": 2,
                            "content": "# Parameters\n\ndef add(a, b=0):\n    return a + b",
                        },
                        {
                            "name": "Lambda функции",
                            "step_number": 3,
                            "content": "# Lambda\n\nsquare = lambda x: x ** 2",
                        },
                    ],
                },
                {
                    "name": "Работа с файлами",
                    "slug": "python-files",
                    "lesson_number": 5,
                    "short_description": "Чтение и запись файлов. Научитесь работать с файловой системой.",
                    "steps": [
                        {
                            "name": "Чтение файлов",
                            "step_number": 1,
                            "content": "# Reading files\n\nwith open('file.txt', 'r') as f:\n    content = f.read()",
                        },
                        {
                            "name": "Запись файлов",
                            "step_number": 2,
                            "content": "# Writing files\n\nwith open('file.txt', 'w') as f:\n    f.write('Hello')",
                        },
                    ],
                },
            ]

            for lesson_data in lessons_data:
                steps_data = lesson_data.pop("steps")
                lesson, created = Lesson.objects.update_or_create(
                    course=python_course, slug=lesson_data["slug"], defaults=lesson_data
                )

                for step_data in steps_data:
                    Step.objects.update_or_create(
                        lesson=lesson,
                        step_number=step_data["step_number"],
                        defaults={
                            "name": step_data["name"],
                            "description": step_data.get("content", ""),
                        },
                    )

                if created:
                    self.stdout.write(self.style.SUCCESS(f"✓ Created lesson: {lesson.name}"))
                else:
                    self.stdout.write(self.style.WARNING(f"⟳ Updated lesson: {lesson.name}"))

        self.stdout.write(self.style.SUCCESS("\n✅ Lessons populated successfully!"))
