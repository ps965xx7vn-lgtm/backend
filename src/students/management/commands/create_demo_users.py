import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from authentication.models import Role, Student
from courses.models import Course, Step
from reviewers.models import StepProgress

User = get_user_model()
fake = Faker("ru_RU")


class Command(BaseCommand):
    help = "Создает пользователей с реальным прогрессом по курсам"

    def add_arguments(self, parser):
        parser.add_argument(
            "--users", type=int, default=8, help="Количество пользователей для создания"
        )

    def handle(self, *args, **options):
        # Создаем роли
        student_role, created = Role.objects.get_or_create(
            name="Студент", defaults={"description": "Обычный студент платформы"}
        )

        self.stdout.write("Создание пользователей с реальным прогрессом...")

        # Получаем все курсы
        courses = list(Course.objects.all())
        if not courses:
            self.stdout.write(self.style.ERROR("Курсы не найдены! Сначала создайте курсы."))
            return

        users_created = 0

        # Создаем пользователей с реальными именами
        real_users = [
            {"first_name": "Алексей", "last_name": "Петров", "email": "alexey.petrov@example.com"},
            {"first_name": "Мария", "last_name": "Иванова", "email": "maria.ivanova@example.com"},
            {
                "first_name": "Дмитрий",
                "last_name": "Сидоров",
                "email": "dmitriy.sidorov@example.com",
            },
            {"first_name": "Анна", "last_name": "Козлова", "email": "anna.kozlova@example.com"},
            {"first_name": "Максим", "last_name": "Волков", "email": "maxim.volkov@example.com"},
            {"first_name": "Елена", "last_name": "Смирнова", "email": "elena.smirnova@example.com"},
            {"first_name": "Андрей", "last_name": "Новиков", "email": "andrey.novikov@example.com"},
            {"first_name": "Ольга", "last_name": "Федорова", "email": "olga.fedorova@example.com"},
        ]

        for i in range(min(options["users"], len(real_users))):
            user_data = real_users[i]

            # Проверяем, существует ли уже пользователь
            if User.objects.filter(email=user_data["email"]).exists():
                self.stdout.write(
                    f'Пользователь {user_data["email"]} уже существует, пропускаем...'
                )
                continue

            user = User.objects.create_user(
                email=user_data["email"],
                password="demo123",  # Простой пароль для демо
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                is_active=True,
                email_is_verified=True,
            )

            # Создаем студента
            profile = Student.objects.create(
                user=user,
                phone=fake.phone_number(),
                birthday=fake.date_of_birth(minimum_age=18, maximum_age=45),
                gender=random.choice(["male", "female"]),
                country="RU",
                city=random.choice(
                    ["Москва", "Санкт-Петербург", "Новосибирск", "Екатеринбург", "Казань"]
                ),
                bio="Изучаю программирование. Интересуюсь веб-разработкой и Python.",
            )

            # Добавляем роль
            profile.role = student_role
            profile.save(update_fields=["role"])

            # Записываем на курсы и создаем реалистичный прогресс
            self.create_realistic_progress(profile, courses)
            users_created += 1

        self.stdout.write(f"Создано пользователей: {users_created}")

        # Статистика
        total_users = User.objects.count()
        total_profiles = Student.objects.count()
        total_progress = StepProgress.objects.count()

        self.stdout.write("\n--- СТАТИСТИКА ---")
        self.stdout.write(f"Всего пользователей: {total_users}")
        self.stdout.write(f"Всего профилей: {total_profiles}")
        self.stdout.write(f"Всего записей прогресса: {total_progress}")

        self.stdout.write(self.style.SUCCESS("\nПользователи с реальным прогрессом созданы!"))

    def create_realistic_progress(self, profile, courses):
        """Создает реалистичный прогресс для пользователя"""

        # Определяем сценарии прогресса
        progress_scenarios = [
            # Новичок - только начал изучать Python
            {"courses": ["python-beginners"], "progress": [25]},
            # Продвинутый новичок - почти закончил Python, начал Django
            {"courses": ["python-beginners", "django-web-development"], "progress": [85, 15]},
            # Веб-разработчик - знает Python и Django, изучает JavaScript
            {
                "courses": [
                    "python-beginners",
                    "django-web-development",
                    "javascript-fundamentals",
                ],
                "progress": [100, 70, 30],
            },
            # Опытный - изучил основы, теперь Git
            {"courses": ["python-beginners", "git-github-basics"], "progress": [100, 60]},
            # Полноценный разработчик - знает все курсы
            {
                "courses": [
                    "python-beginners",
                    "django-web-development",
                    "javascript-fundamentals",
                    "git-github-basics",
                ],
                "progress": [100, 90, 80, 95],
            },
            # Фронтенд фокус - JavaScript и Git
            {"courses": ["javascript-fundamentals", "git-github-basics"], "progress": [65, 40]},
            # Только начинающий - изучает Git для начала
            {"courses": ["git-github-basics"], "progress": [35]},
            # Интенсивное изучение - много курсов, но небольшой прогресс
            {
                "courses": [
                    "python-beginners",
                    "django-web-development",
                    "javascript-fundamentals",
                ],
                "progress": [45, 20, 10],
            },
        ]

        # Выбираем случайный сценарий
        scenario = random.choice(progress_scenarios)

        course_slugs = scenario["courses"]
        progress_percentages = scenario["progress"]

        for course_slug, target_progress in zip(course_slugs, progress_percentages, strict=False):
            # Находим курс
            course = next((c for c in courses if c.slug == course_slug), None)
            if not course:
                continue

            # Записываем пользователя на курс
            profile.courses.add(course)

            # Получаем все шаги курса
            all_steps = list(
                Step.objects.filter(lesson__course=course).order_by(
                    "lesson__lesson_number", "step_number"
                )
            )

            if not all_steps:
                continue

            # Вычисляем количество шагов для достижения целевого прогресса
            steps_to_complete = int(len(all_steps) * target_progress / 100)

            # Выбираем шаги последовательно (реалистично - изучают по порядку)
            steps_to_complete_list = all_steps[:steps_to_complete]

            # Создаем прогресс с реалистичными датами
            base_date = timezone.now() - timezone.timedelta(days=30)  # Начал изучать месяц назад

            for i, step in enumerate(steps_to_complete_list):
                # Реалистичное распределение времени - не все шаги в один день
                days_offset = i * random.uniform(0.5, 2.0)  # От 0.5 до 2 дней на шаг
                completed_date = base_date + timezone.timedelta(days=days_offset)

                StepProgress.objects.get_or_create(
                    profile=profile,
                    step=step,
                    defaults={"is_completed": True, "completed_at": completed_date},
                )
