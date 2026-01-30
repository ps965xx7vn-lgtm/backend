from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from courses.models import Course, Lesson, Step

User = get_user_model()


class Command(BaseCommand):
    help = "Наполняет систему реальными курсами по программированию"

    def handle(self, *args, **options):
        self.stdout.write("Создание реальных курсов...")

        # Очищаем старые курсы
        Course.objects.filter(name__startswith="Тестовый").delete()
        Course.objects.filter(
            slug__in=[
                "python-beginners",
                "django-web-development",
                "javascript-fundamentals",
                "git-github-basics",
            ]
        ).delete()

        # Курс 1: Python для начинающих
        python_course = Course.objects.create(
            name="Python с нуля до первого проекта",
            description="""
Полный курс по изучению языка программирования Python с самых основ.

**Что вы изучите:**
- Основы синтаксиса Python
- Работа с переменными и типами данных
- Условные конструкции и циклы
- Функции и модули
- Работа с файлами
- Основы ООП
- Создание первого проекта

**Для кого этот курс:**
- Начинающих программистов
- Тех, кто хочет сменить профессию
- Студентов и школьников
- Всех, кто интересуется программированием

По окончании курса вы сможете создавать собственные программы на Python и будете готовы к изучению более сложных тем.
            """.strip(),
            short_description="Изучите Python с нуля за 8 недель. От основ синтаксиса до создания первого проекта.",
            slug="python-beginners",
        )

        # Уроки для Python курса
        python_lessons = [
            {
                "name": "Знакомство с Python",
                "description": 'Установка Python, настройка среды разработки, первая программа "Hello World"',
                "steps": [
                    {
                        "name": "Установка Python",
                        "description": "Скачайте и установите Python с официального сайта python.org",
                        "actions": "Перейдите на python.org, скачайте последнюю версию Python для вашей операционной системы и установите её",
                    },
                    {
                        "name": "Настройка IDE",
                        "description": "Установите и настройте среду разработки (PyCharm или VS Code)",
                        "actions": "Скачайте PyCharm Community или VS Code, установите расширения для Python",
                    },
                    {
                        "name": "Первая программа",
                        "description": 'Создайте файл hello.py и напишите программу print("Hello, World!")',
                        "actions": "Создайте новый файл, напишите код и запустите программу",
                    },
                    {
                        "name": "Запуск программы",
                        "description": "Научитесь запускать Python программы из командной строки и IDE",
                        "actions": "Откройте терминал, перейдите в папку с файлом и выполните python hello.py",
                    },
                ],
            },
            {
                "name": "Переменные и типы данных",
                "description": "Изучение основных типов данных в Python: числа, строки, булевы значения",
                "steps": [
                    {
                        "name": "Переменные",
                        "description": "Создание и использование переменных в Python",
                        "actions": 'Создайте переменные разных типов: name = "John", age = 25, is_student = True',
                    },
                    {
                        "name": "Числовые типы",
                        "description": "Работа с целыми числами (int) и числами с плавающей точкой (float)",
                        "actions": "Объявите переменные: x = 10, y = 3.14. Попробуйте арифметические операции",
                    },
                    {
                        "name": "Строки",
                        "description": "Создание и обработка строк, основные методы строк",
                        "actions": 'Создайте строку: text = "Python". Попробуйте методы: text.upper(), text.lower(), len(text)',
                    },
                    {
                        "name": "Ввод и вывод",
                        "description": "Функции input() и print() для взаимодействия с пользователем",
                        "actions": 'Напишите программу: name = input("Ваше имя: "), print(f"Привет, {name}!")',
                    },
                ],
            },
            {
                "name": "Условные конструкции",
                "description": "Изучение операторов if, elif, else для создания логики в программах",
                "steps": [
                    {
                        "name": "Оператор if",
                        "description": "Базовый условный оператор if",
                        "actions": 'Напишите: age = 18; if age >= 18: print("Совершеннолетний")',
                    },
                    {
                        "name": "Оператор else",
                        "description": "Обработка альтернативных случаев с помощью else",
                        "actions": 'Добавьте else: else: print("Несовершеннолетний")',
                    },
                    {
                        "name": "Множественные условия elif",
                        "description": "Использование elif для проверки нескольких условий",
                        "actions": "Создайте программу определения оценки по баллам с помощью elif",
                    },
                    {
                        "name": "Логические операторы",
                        "description": "Операторы and, or, not для сложных условий",
                        "actions": 'Напишите условие: if age >= 18 and has_license: print("Может водить")',
                    },
                ],
            },
            {
                "name": "Циклы",
                "description": "Циклы for и while для выполнения повторяющихся действий",
                "steps": [
                    {
                        "name": "Цикл for",
                        "description": "Итерация по последовательностям с помощью цикл for",
                        "actions": "Напишите: for i in range(5): print(i)",
                    },
                    {
                        "name": "Цикл while",
                        "description": "Выполнение кода пока условие истинно",
                        "actions": "Создайте счетчик: count = 0; while count < 5: print(count); count += 1",
                    },
                    {
                        "name": "Управление циклами",
                        "description": "Операторы break и continue для управления выполнением циклов",
                        "actions": "Попробуйте break для выхода из цикла и continue для пропуска итерации",
                    },
                    {
                        "name": "Вложенные циклы",
                        "description": "Использование циклов внутри других циклов",
                        "actions": "Создайте таблицу умножения с помощью вложенных циклов for",
                    },
                ],
            },
            {
                "name": "Списки и кортежи",
                "description": "Работа с коллекциями данных: списки, кортежи и их методы",
                "steps": [
                    {
                        "name": "Создание списков",
                        "description": "Создание и инициализация списков",
                        "actions": "Создайте список: numbers = [1, 2, 3, 4, 5]",
                    },
                    {
                        "name": "Методы списков",
                        "description": "Основные методы для работы со списками",
                        "actions": "Попробуйте: numbers.append(6), numbers.remove(3), numbers.sort()",
                    },
                    {
                        "name": "Индексы и срезы",
                        "description": "Доступ к элементам списка по индексу и создание срезов",
                        "actions": "Используйте: numbers[0], numbers[-1], numbers[1:3]",
                    },
                    {
                        "name": "Кортежи",
                        "description": "Неизменяемые последовательности - кортежи",
                        "actions": "Создайте кортеж: coordinates = (10, 20). Попробуйте доступ к элементам",
                    },
                ],
            },
            {
                "name": "Функции",
                "description": "Создание собственных функций для организации кода",
                "steps": [
                    {
                        "name": "Определение функций",
                        "description": "Создание функций с помощью ключевого слова def",
                        "actions": 'Создайте функцию: def greet(name): return f"Привет, {name}!"',
                    },
                    {
                        "name": "Параметры и аргументы",
                        "description": "Передача данных в функции через параметры",
                        "actions": "Создайте функцию сложения: def add(a, b): return a + b",
                    },
                    {
                        "name": "Локальные и глобальные переменные",
                        "description": "Область видимости переменных в функциях",
                        "actions": "Изучите разницу между локальными и глобальными переменными",
                    },
                    {
                        "name": "Документация функций",
                        "description": "Добавление docstring для документирования функций",
                        "actions": 'Добавьте документацию: """Эта функция приветствует пользователя"""',
                    },
                ],
            },
        ]

        self.create_lessons_and_steps(python_course, python_lessons)

        # Курс 2: Django веб-разработка
        django_course = Course.objects.create(
            name="Django: создание веб-приложений",
            description="""
Изучите Django - самый популярный Python фреймворк для веб-разработки.

**Что вы изучите:**
- Архитектура Django (MVT)
- Создание моделей и работа с базой данных
- Представления (Views) и шаблоны (Templates)
- Система маршрутизации URL
- Формы и валидация данных
- Аутентификация и авторизация
- Развертывание приложения

**Требования:**
- Базовые знания Python
- Понимание основ веб-разработки
- Знание HTML/CSS (базовый уровень)

По окончании курса вы создадите полноценное веб-приложение на Django.
            """.strip(),
            short_description="Создавайте мощные веб-приложения с Django. От основ фреймворка до развертывания проекта.",
            slug="django-web-development",
        )

        django_lessons = [
            {
                "name": "Введение в Django",
                "description": "Установка Django, создание первого проекта и приложения",
                "steps": [
                    {
                        "name": "Установка Django",
                        "description": "Установите Django через pip",
                        "actions": "Выполните в терминале: pip install django",
                    },
                    {
                        "name": "Создание проекта",
                        "description": "Создайте новый Django проект",
                        "actions": "Выполните: django-admin startproject mysite",
                    },
                    {
                        "name": "Запуск сервера",
                        "description": "Запустите локальный сервер разработки",
                        "actions": "Перейдите в папку проекта и выполните: python manage.py runserver",
                    },
                    {
                        "name": "Создание приложения",
                        "description": "Создайте первое приложение в проекте",
                        "actions": "Выполните: python manage.py startapp blog",
                    },
                ],
            },
            {
                "name": "Модели и базы данных",
                "description": "Создание моделей данных и работа с ORM Django",
                "steps": [
                    {
                        "name": "Создание модели",
                        "description": "Определите модель в models.py",
                        "actions": "Создайте класс модели с полями CharField, TextField, DateTimeField",
                    },
                    {
                        "name": "Миграции",
                        "description": "Создание и применение миграций базы данных",
                        "actions": "Выполните: python manage.py makemigrations, затем python manage.py migrate",
                    },
                    {
                        "name": "Django Admin",
                        "description": "Регистрация модели в админ-панели",
                        "actions": "Зарегистрируйте модель в admin.py и создайте суперпользователя",
                    },
                    {
                        "name": "Запросы к БД",
                        "description": "Основные операции с данными через ORM",
                        "actions": "Попробуйте создать, читать, обновлять и удалять записи",
                    },
                ],
            },
            {
                "name": "Представления и URL",
                "description": "Создание представлений и настройка маршрутизации",
                "steps": [
                    {
                        "name": "Функциональные представления",
                        "description": "Создание простых функций-представлений",
                        "actions": "Создайте функцию в views.py, которая возвращает HttpResponse",
                    },
                    {
                        "name": "URL-маршруты",
                        "description": "Настройка маршрутизации в urls.py",
                        "actions": "Создайте файл urls.py в приложении и настройте маршруты",
                    },
                    {
                        "name": "Передача параметров",
                        "description": "Передача параметров через URL",
                        "actions": 'Создайте URL с параметром: path("post/<int:id>/", views.post_detail)',
                    },
                    {
                        "name": "Перенаправления",
                        "description": "Использование redirect для перенаправления пользователей",
                        "actions": "Используйте функцию redirect() для перенаправления на другие страницы",
                    },
                ],
            },
        ]

        self.create_lessons_and_steps(django_course, django_lessons)

        # Курс 3: JavaScript для веб-разработки
        js_course = Course.objects.create(
            name="JavaScript: от основ до DOM",
            description="""
Изучите JavaScript - язык программирования для создания интерактивных веб-страниц.

**Что вы изучите:**
- Основы синтаксиса JavaScript
- Переменные, функции, объекты
- Работа с DOM
- Обработка событий
- Асинхронное программирование
- Работа с API
- Современный JavaScript (ES6+)

**Для кого этот курс:**
- Начинающих веб-разработчиков
- Тех, кто знает HTML/CSS
- Python-разработчиков, изучающих фронтенд

Курс включает практические задания и мини-проекты.
            """.strip(),
            short_description="Освойте JavaScript для создания интерактивных веб-страниц. От переменных до работы с API.",
            slug="javascript-fundamentals",
        )

        js_lessons = [
            {
                "name": "Основы JavaScript",
                "description": "Синтаксис JavaScript, переменные и типы данных",
                "steps": [
                    {
                        "name": "Подключение JavaScript",
                        "description": "Подключение JavaScript к HTML странице",
                        "actions": "Создайте HTML файл и подключите JS через тег <script>",
                    },
                    {
                        "name": "Переменные let, const, var",
                        "description": "Объявление переменных в JavaScript",
                        "actions": 'Попробуйте: let name = "John"; const age = 25; var city = "Moscow";',
                    },
                    {
                        "name": "Типы данных",
                        "description": "Примитивные типы данных в JavaScript",
                        "actions": "Изучите: string, number, boolean, null, undefined, symbol",
                    },
                    {
                        "name": "Операторы",
                        "description": "Арифметические, логические и операторы сравнения",
                        "actions": "Попробуйте различные операторы: +, -, *, /, ===, !==, &&, ||",
                    },
                ],
            },
            {
                "name": "Функции в JavaScript",
                "description": "Создание и использование функций, стрелочные функции",
                "steps": [
                    {
                        "name": "Объявление функций",
                        "description": "Различные способы создания функций",
                        "actions": "Создайте функцию: function greet(name) { return `Hello, ${name}!`; }",
                    },
                    {
                        "name": "Стрелочные функции",
                        "description": "Современный синтаксис стрелочных функций",
                        "actions": "Перепишите функцию: const greet = (name) => `Hello, ${name}!`;",
                    },
                    {
                        "name": "Параметры по умолчанию",
                        "description": "Задание значений параметров по умолчанию",
                        "actions": 'Создайте функцию с параметром по умолчанию: function greet(name = "World")',
                    },
                    {
                        "name": "Возвращение значений",
                        "description": "Возвращение результатов из функций",
                        "actions": "Создайте функцию, которая возвращает результат вычислений",
                    },
                ],
            },
            {
                "name": "Работа с DOM",
                "description": "Манипулирование элементами веб-страницы через DOM API",
                "steps": [
                    {
                        "name": "Поиск элементов",
                        "description": "Методы поиска элементов на странице",
                        "actions": "Используйте: document.getElementById(), document.querySelector()",
                    },
                    {
                        "name": "Изменение содержимого",
                        "description": "Изменение текста и HTML содержимого элементов",
                        "actions": 'Попробуйте: element.textContent = "Новый текст"; element.innerHTML = "<b>Жирный текст</b>";',
                    },
                    {
                        "name": "Изменение стилей",
                        "description": "Изменение CSS свойств элементов через JavaScript",
                        "actions": 'Измените стили: element.style.color = "red"; element.style.display = "none";',
                    },
                    {
                        "name": "Создание элементов",
                        "description": "Динамическое создание новых HTML элементов",
                        "actions": 'Создайте элемент: const div = document.createElement("div"); document.body.appendChild(div);',
                    },
                ],
            },
        ]

        self.create_lessons_and_steps(js_course, js_lessons)

        # Курс 4: Git и GitHub
        git_course = Course.objects.create(
            name="Git и GitHub: система контроля версий",
            description="""
Изучите Git - незаменимый инструмент любого разработчика для контроля версий кода.

**Что вы изучите:**
- Основы системы контроля версий
- Работа с локальными репозиториями
- Ветвление и слияние (branching, merging)
- Работа с удаленными репозиториями
- GitHub: создание репозиториев, pull requests
- Командная работа с Git
- Лучшие практики Git

**Для кого этот курс:**
- Начинающих разработчиков
- Всех, кто работает с кодом
- Команд разработчиков

Git - основа современной разработки программного обеспечения.
            """.strip(),
            short_description="Освойте Git и GitHub для эффективного управления кодом. От базовых команд до командной работы.",
            slug="git-github-basics",
        )

        git_lessons = [
            {
                "name": "Введение в Git",
                "description": "Установка и первоначальная настройка Git",
                "steps": [
                    {
                        "name": "Установка Git",
                        "description": "Установите Git на ваш компьютер",
                        "actions": "Скачайте Git с git-scm.com и установите для вашей ОС",
                    },
                    {
                        "name": "Первоначальная настройка",
                        "description": "Настройте имя пользователя и email",
                        "actions": 'Выполните: git config --global user.name "Your Name"; git config --global user.email "your@email.com"',
                    },
                    {
                        "name": "Создание репозитория",
                        "description": "Инициализация нового Git репозитория",
                        "actions": "В папке проекта выполните: git init",
                    },
                    {
                        "name": "Первый коммит",
                        "description": "Создание первого коммита",
                        "actions": 'Добавьте файлы: git add .; Создайте коммит: git commit -m "Initial commit"',
                    },
                ],
            },
            {
                "name": "Основные команды Git",
                "description": "Базовые операции: add, commit, status, log",
                "steps": [
                    {
                        "name": "git status",
                        "description": "Проверка состояния рабочей директории",
                        "actions": "Выполните git status чтобы увидеть измененные файлы",
                    },
                    {
                        "name": "git add",
                        "description": "Добавление файлов в индекс (staging area)",
                        "actions": "Добавьте файл: git add filename.txt или все файлы: git add .",
                    },
                    {
                        "name": "git commit",
                        "description": "Сохранение изменений в репозиторий",
                        "actions": 'Создайте коммит с сообщением: git commit -m "Описание изменений"',
                    },
                    {
                        "name": "git log",
                        "description": "Просмотр истории коммитов",
                        "actions": "Посмотрите историю: git log или краткий вид: git log --oneline",
                    },
                ],
            },
            {
                "name": "Работа с GitHub",
                "description": "Создание репозитория на GitHub и работа с удаленными репозиториями",
                "steps": [
                    {
                        "name": "Создание репозитория на GitHub",
                        "description": "Создайте новый репозиторий на github.com",
                        "actions": 'Зайдите на GitHub, нажмите "New repository", заполните название и описание',
                    },
                    {
                        "name": "Связывание с удаленным репозиторием",
                        "description": "Подключение локального репозитория к GitHub",
                        "actions": "Выполните: git remote add origin https://github.com/username/repo.git",
                    },
                    {
                        "name": "git push",
                        "description": "Отправка изменений на GitHub",
                        "actions": "Отправьте код: git push -u origin main",
                    },
                    {
                        "name": "git clone",
                        "description": "Клонирование репозитория с GitHub",
                        "actions": "Склонируйте репозиторий: git clone https://github.com/username/repo.git",
                    },
                ],
            },
        ]

        self.create_lessons_and_steps(git_course, git_lessons)

        self.stdout.write(self.style.SUCCESS("Реальные курсы успешно созданы!"))

        # Статистика
        total_courses = Course.objects.count()
        total_lessons = Lesson.objects.count()
        total_steps = Step.objects.count()

        self.stdout.write("\n--- СТАТИСТИКА ---")
        self.stdout.write(f"Всего курсов: {total_courses}")
        self.stdout.write(f"Всего уроков: {total_lessons}")
        self.stdout.write(f"Всего шагов: {total_steps}")

    def create_lessons_and_steps(self, course, lessons_data):
        """Создает уроки и шаги для курса"""
        for lesson_num, lesson_data in enumerate(lessons_data, 1):
            lesson = Lesson.objects.create(
                name=lesson_data["name"],
                course=course,
                lesson_number=lesson_num,
                short_description=lesson_data["description"],
                slug=f"{course.slug}-lesson-{lesson_num}",
            )

            for step_num, step_data in enumerate(lesson_data["steps"], 1):
                Step.objects.create(
                    name=step_data["name"],
                    lesson=lesson,
                    step_number=step_num,
                    description=step_data["description"],
                    actions=step_data["actions"],
                    self_check=f"Убедитесь, что вы выполнили: {step_data['actions']}",
                )
