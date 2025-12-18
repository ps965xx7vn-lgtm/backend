"""
Management команда для создания уроков и шагов для существующих курсов.

Использование:
    python manage.py populate_lessons_data
    python manage.py populate_lessons_data --clear  # Очистить старые данные
"""

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from courses.models import Course, Lesson, Step


class Command(BaseCommand):
    help = "Создает уроки и шаги для существующих курсов"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Очистить существующие уроки и шаги перед созданием",
        )

    def handle(self, *args, **options):
        """Создает уроки и шаги для всех курсов"""

        if options["clear"]:
            self.stdout.write(self.style.WARNING("Очистка существующих данных..."))
            Step.objects.all().delete()
            Lesson.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("✓ Данные очищены\n"))

        self.stdout.write(self.style.HTTP_INFO("=== СОЗДАНИЕ УРОКОВ И ШАГОВ ===\n"))

        # Получаем все курсы
        courses = Course.objects.all()

        if not courses.exists():
            self.stdout.write(
                self.style.ERROR("Курсы не найдены! Сначала запустите populate_courses_data")
            )
            return

        # Данные для уроков по категориям
        lessons_templates = {
            "python": [
                {
                    "name": "Введение в Python",
                    "short_description": "Знакомство с Python, установка и первая программа",
                    "steps": [
                        {
                            "name": "Что такое Python",
                            "description": "Python — это высокоуровневый язык программирования, который отличается простым и понятным синтаксисом.",
                            "actions": "Изучите основные преимущества Python: простота, читаемость, большое сообщество",
                            "self_check": "Понимаете ли вы, почему Python популярен?",
                        },
                        {
                            "name": "Установка Python",
                            "description": "Загрузите Python с официального сайта python.org и установите на свой компьютер.",
                            "actions": 'Скачайте установщик Python 3.11+, запустите установку, отметьте "Add Python to PATH"',
                            "self_check": "Выполните в терминале: python --version",
                        },
                        {
                            "name": "Первая программа",
                            "description": 'Напишите классическую программу "Hello, World!"',
                            "actions": 'Создайте файл hello.py и напишите: print("Hello, World!")',
                            "self_check": "Запустите программу и увидите вывод в консоли",
                        },
                    ],
                },
                {
                    "name": "Переменные и типы данных",
                    "short_description": "Работа с переменными, числами, строками и булевыми значениями",
                    "steps": [
                        {
                            "name": "Переменные",
                            "description": "Переменная — это контейнер для хранения данных. В Python не нужно указывать тип.",
                            "actions": 'Создайте переменные: name = "Иван", age = 25, is_student = True',
                            "self_check": "Выведите значения переменных с помощью print()",
                        },
                        {
                            "name": "Числовые типы",
                            "description": "Python поддерживает целые числа (int), дробные (float) и комплексные числа.",
                            "actions": "Попробуйте операции: 10 + 5, 20 - 8, 3 * 4, 15 / 3",
                            "self_check": "Проверьте результаты математических операций",
                        },
                        {
                            "name": "Строки",
                            "description": "Строки используются для хранения текста. Можно использовать одинарные или двойные кавычки.",
                            "actions": "Создайте строки, объедините их с помощью +, используйте методы upper(), lower()",
                            "self_check": 'Попробуйте форматирование f-строк: f"Привет, {name}"',
                        },
                    ],
                },
                {
                    "name": "Условные операторы",
                    "short_description": "Условия if, elif, else для управления потоком программы",
                    "steps": [
                        {
                            "name": "Оператор if",
                            "description": "Оператор if выполняет код только если условие истинно.",
                            "actions": 'Напишите: if age >= 18: print("Совершеннолетний")',
                            "self_check": "Проверьте работу с разными значениями age",
                        },
                        {
                            "name": "else и elif",
                            "description": "else выполняется если условие ложно, elif проверяет дополнительные условия.",
                            "actions": "Создайте проверку возраста с несколькими условиями",
                            "self_check": "Протестируйте все ветки условий",
                        },
                    ],
                },
            ],
            "web": [
                {
                    "name": "Основы HTML",
                    "short_description": "Структура HTML документа, основные теги",
                    "steps": [
                        {
                            "name": "Структура HTML",
                            "description": "HTML документ состоит из <!DOCTYPE html>, <html>, <head> и <body>",
                            "actions": "Создайте базовый HTML файл с правильной структурой",
                            "self_check": "Откройте файл в браузере и проверьте отображение",
                        },
                        {
                            "name": "Основные теги",
                            "description": "Изучите теги: <h1>-<h6>, <p>, <a>, <img>, <div>, <span>",
                            "actions": "Добавьте заголовки, параграфы, ссылки и изображения",
                            "self_check": "Все элементы корректно отображаются?",
                        },
                    ],
                },
                {
                    "name": "Основы CSS",
                    "short_description": "Стилизация элементов, селекторы, свойства",
                    "steps": [
                        {
                            "name": "Подключение CSS",
                            "description": "CSS можно подключить через тег <link> или <style>",
                            "actions": "Создайте файл style.css и подключите к HTML",
                            "self_check": "Стили применяются к элементам?",
                        },
                        {
                            "name": "Селекторы",
                            "description": "Селекторы позволяют выбрать элементы: по тегу, классу, ID",
                            "actions": "Примените стили к разным элементам используя различные селекторы",
                            "self_check": "Понимаете разницу между .class, #id и tag?",
                        },
                    ],
                },
                {
                    "name": "Основы JavaScript",
                    "short_description": "Переменные, функции, DOM манипуляции",
                    "steps": [
                        {
                            "name": "Переменные в JavaScript",
                            "description": "Используйте let, const для объявления переменных",
                            "actions": "Объявите переменные разных типов: число, строка, массив, объект",
                            "self_check": "Выведите значения в консоль браузера",
                        },
                        {
                            "name": "Функции",
                            "description": "Функции позволяют переиспользовать код",
                            "actions": 'Создайте функцию для приветствия: function greet(name) { return "Hello, " + name; }',
                            "self_check": "Вызовите функцию с разными параметрами",
                        },
                    ],
                },
            ],
            "javascript": [
                {
                    "name": "ES6+ особенности",
                    "short_description": "Современный JavaScript: стрелочные функции, деструктуризация",
                    "steps": [
                        {
                            "name": "Стрелочные функции",
                            "description": "Краткий синтаксис для функций: const add = (a, b) => a + b",
                            "actions": "Перепишите обычные функции в стрелочные",
                            "self_check": "Понимаете разницу в контексте this?",
                        },
                        {
                            "name": "Деструктуризация",
                            "description": "Извлечение значений из объектов и массивов",
                            "actions": "const {name, age} = user; const [first, second] = array;",
                            "self_check": "Примените деструктуризацию к своим данным",
                        },
                    ],
                },
                {
                    "name": "Асинхронность",
                    "short_description": "Promises, async/await, работа с API",
                    "steps": [
                        {
                            "name": "Promises",
                            "description": "Promise представляет результат асинхронной операции",
                            "actions": "Создайте Promise с resolve и reject",
                            "self_check": "Обработайте результат через .then() и .catch()",
                        },
                        {
                            "name": "async/await",
                            "description": "Синтаксический сахар для работы с промисами",
                            "actions": "Напишите async функцию с await для fetch запроса",
                            "self_check": "Получите данные из публичного API",
                        },
                    ],
                },
            ],
            "data-science": [
                {
                    "name": "Введение в NumPy",
                    "short_description": "Работа с массивами, математические операции",
                    "steps": [
                        {
                            "name": "Установка NumPy",
                            "description": "NumPy — библиотека для научных вычислений",
                            "actions": "pip install numpy",
                            "self_check": "import numpy as np; print(np.__version__)",
                        },
                        {
                            "name": "Создание массивов",
                            "description": "Массивы NumPy эффективнее списков Python",
                            "actions": "arr = np.array([1, 2, 3, 4, 5])",
                            "self_check": "Создайте многомерные массивы с помощью reshape",
                        },
                    ],
                },
                {
                    "name": "Введение в Pandas",
                    "short_description": "DataFrame, чтение данных, базовые операции",
                    "steps": [
                        {
                            "name": "DataFrame",
                            "description": "DataFrame — основная структура данных в Pandas",
                            "actions": "import pandas as pd; df = pd.DataFrame(data)",
                            "self_check": "Создайте DataFrame из словаря",
                        },
                        {
                            "name": "Чтение файлов",
                            "description": "Pandas умеет читать CSV, Excel, JSON",
                            "actions": 'df = pd.read_csv("data.csv")',
                            "self_check": "Загрузите и изучите структуру данных с помощью .head(), .info()",
                        },
                    ],
                },
            ],
            "other": [
                {
                    "name": "Основы алгоритмов",
                    "short_description": "Временная сложность, базовые алгоритмы",
                    "steps": [
                        {
                            "name": "Big O нотация",
                            "description": "Big O описывает сложность алгоритма",
                            "actions": "Изучите O(1), O(n), O(log n), O(n²)",
                            "self_check": "Определите сложность простых алгоритмов",
                        },
                        {
                            "name": "Сортировка пузырьком",
                            "description": "Простой алгоритм сортировки",
                            "actions": "Реализуйте bubble sort на Python",
                            "self_check": "Какая сложность у bubble sort?",
                        },
                    ],
                },
                {
                    "name": "Структуры данных",
                    "short_description": "Списки, стеки, очереди, деревья",
                    "steps": [
                        {
                            "name": "Списки и массивы",
                            "description": "Линейные структуры данных",
                            "actions": "Реализуйте операции вставки и удаления",
                            "self_check": "Какие преимущества у связных списков?",
                        },
                        {
                            "name": "Стеки и очереди",
                            "description": "LIFO и FIFO структуры",
                            "actions": "Реализуйте Stack и Queue классы",
                            "self_check": "Где применяются стеки и очереди?",
                        },
                    ],
                },
            ],
        }

        total_lessons = 0
        total_steps = 0

        for course in courses:
            # Получаем шаблоны уроков для категории курса
            templates = lessons_templates.get(course.category, lessons_templates["other"])

            self.stdout.write(self.style.WARNING(f"\nКурс: {course.name} ({course.category})"))

            for lesson_num, lesson_data in enumerate(templates, start=1):
                # Создаем урок
                slug = slugify(f"{course.slug}-lesson-{lesson_num}-{lesson_data['name']}")
                lesson, created = Lesson.objects.get_or_create(
                    course=course,
                    lesson_number=lesson_num,
                    defaults={
                        "name": lesson_data["name"],
                        "slug": slug,
                        "short_description": lesson_data["short_description"],
                    },
                )

                if created:
                    total_lessons += 1
                    self.stdout.write(self.style.SUCCESS(f"  ✓ Урок {lesson_num}: {lesson.name}"))
                else:
                    self.stdout.write(f"  ↻ Урок уже существует: {lesson.name}")

                # Создаем шаги для урока
                for step_num, step_data in enumerate(lesson_data["steps"], start=1):
                    step, step_created = Step.objects.get_or_create(
                        lesson=lesson,
                        step_number=step_num,
                        defaults={
                            "name": step_data["name"],
                            "description": step_data.get("description", ""),
                            "actions": step_data.get("actions", ""),
                            "self_check": step_data.get("self_check", ""),
                        },
                    )

                    if step_created:
                        total_steps += 1
                        self.stdout.write(f"    → Шаг {step_num}: {step.name}")

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"Создано уроков: {total_lessons}"))
        self.stdout.write(self.style.SUCCESS(f"Создано шагов: {total_steps}"))
        self.stdout.write(self.style.SUCCESS("✓ Уроки и шаги успешно добавлены!"))
