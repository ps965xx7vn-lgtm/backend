import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from faker import Faker

from authentication.models import Role, Student
from courses.models import Course, Lesson, Step
from reviewers.models import StepProgress

User = get_user_model()
fake = Faker("ru_RU")


class Command(BaseCommand):
    help = "Создание тестовых данных для демонстрации системы"

    def add_arguments(self, parser):
        parser.add_argument(
            "--users", type=int, default=10, help="Количество пользователей для создания"
        )
        parser.add_argument(
            "--courses", type=int, default=3, help="Количество дополнительных курсов для создания"
        )
        parser.add_argument(
            "--clear", action="store_true", help="Очистить существующие тестовые данные"
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write("Очистка тестовых данных...")
            # Удаляем все, кроме суперпользователя
            User.objects.filter(is_superuser=False).delete()
            Course.objects.filter(name__startswith="Тестовый").delete()
            self.stdout.write(self.style.SUCCESS("Тестовые данные очищены"))
            return

        # Создаем роли
        student_role, created = Role.objects.get_or_create(
            name="Студент", defaults={"description": "Обычный студент платформы"}
        )
        mentor_role, created = Role.objects.get_or_create(
            name="Ментор", defaults={"description": "Ментор и куратор курсов"}
        )

        self.stdout.write("Создание пользователей...")
        users_created = 0

        for _ in range(options["users"]):
            email = fake.email()
            if User.objects.filter(email=email).exists():
                continue

            user = User.objects.create_user(
                email=email,
                password="testpass123",
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                is_active=True,
                email_is_verified=True,
            )

            # Создаем профиль
            profile = Student.objects.create(
                user=user,
                phone=fake.phone_number(),
                birthday=fake.date_of_birth(minimum_age=18, maximum_age=60),
                gender=random.choice(["male", "female"]),
                country="RU",
                city=fake.city(),
                bio=fake.text(max_nb_chars=200),
            )

            # Добавляем роль
            profile.role = student_role
            profile.save(update_fields=["role"])
            users_created += 1

        self.stdout.write(f"Создано пользователей: {users_created}")

        # Создаем дополнительные курсы
        self.stdout.write("Создание курсов...")
        course_topics = [
            ("Тестовый курс Python для начинающих", "Изучение основ программирования на Python"),
            ("Тестовый курс Django разработка", "Создание веб-приложений с помощью Django"),
            ("Тестовый курс JavaScript и React", "Фронтенд разработка с современными технологиями"),
            ("Тестовый курс Data Science", "Анализ данных и машинное обучение"),
            ("Тестовый курс DevOps практики", "Автоматизация развертывания и CI/CD"),
        ]

        courses_created = 0
        for i in range(options["courses"]):
            if i >= len(course_topics):
                break

            name, description = course_topics[i]
            if Course.objects.filter(name=name).exists():
                continue

            course = Course.objects.create(
                name=name, description=description, short_description=description[:200]
            )

            # Создаем уроки для курса
            for lesson_num in range(1, random.randint(3, 6)):
                lesson_name = f"Урок {lesson_num}: {fake.sentence(nb_words=4)}"
                lesson_slug = f"{course.slug}-lesson-{lesson_num}"

                lesson = Lesson.objects.create(
                    name=lesson_name,
                    course=course,
                    lesson_number=lesson_num,
                    short_description=fake.text(max_nb_chars=300),
                    slug=lesson_slug,
                )

                # Создаем шаги для урока
                for step_num in range(1, random.randint(3, 8)):
                    Step.objects.create(
                        name=f"Шаг {step_num}: {fake.sentence(nb_words=3)}",
                        lesson=lesson,
                        step_number=step_num,
                        description=fake.text(max_nb_chars=500),
                        actions=fake.text(max_nb_chars=400),
                        self_check=fake.text(max_nb_chars=200),
                    )

            courses_created += 1

        self.stdout.write(f"Создано курсов: {courses_created}")

        # Записываем пользователей на курсы и создаем прогресс
        self.stdout.write("Создание записей на курсы и прогресса...")

        profiles = Student.objects.all()
        courses = Course.objects.all()

        enrollments = 0
        progress_created = 0

        for profile in profiles:
            # Записываем на случайные курсы
            course_count = random.randint(1, min(3, courses.count()))
            selected_courses = random.sample(list(courses), course_count)

            for course in selected_courses:
                if not profile.courses.filter(id=course.id).exists():
                    profile.courses.add(course)
                    enrollments += 1

                    # Создаем случайный прогресс
                    all_steps = Step.objects.filter(lesson__course=course)

                    # Определяем процент прогресса для этого пользователя в этом курсе
                    progress_percentage = random.choice([0, 0, 15, 30, 45, 60, 75, 90, 100])
                    steps_to_complete = int(all_steps.count() * progress_percentage / 100)

                    if steps_to_complete > 0:
                        steps_to_complete_list = random.sample(
                            list(all_steps), min(steps_to_complete, all_steps.count())
                        )

                        for step in steps_to_complete_list:
                            StepProgress.objects.get_or_create(
                                profile=profile,
                                step=step,
                                defaults={
                                    "is_completed": True,
                                    "completed_at": fake.date_time_between(
                                        start_date="-30d", end_date="now"
                                    ),
                                },
                            )
                            progress_created += 1

        self.stdout.write(f"Создано записей на курсы: {enrollments}")
        self.stdout.write(f"Создано записей прогресса: {progress_created}")

        # Статистика
        self.stdout.write("\n--- СТАТИСТИКА ---")
        self.stdout.write(f"Всего пользователей: {User.objects.count()}")
        self.stdout.write(f"Всего студентов: {Student.objects.count()}")
        self.stdout.write(f"Всего курсов: {Course.objects.count()}")
        self.stdout.write(f"Всего уроков: {Lesson.objects.count()}")
        self.stdout.write(f"Всего шагов: {Step.objects.count()}")
        self.stdout.write(f"Всего записей прогресса: {StepProgress.objects.count()}")

        self.stdout.write(self.style.SUCCESS("\nТестовые данные успешно созданы!"))
