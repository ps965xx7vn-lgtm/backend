"""
Management команда для создания тестовых работ студентов.
Использование: python manage.py populate_submissions
"""

import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from authentication.models import Reviewer, User
from courses.models import Course, Lesson
from reviewers.models import LessonSubmission, Review, StudentImprovement


class Command(BaseCommand):
    help = "Создает тестовые работы студентов для проверки"

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=20, help="Количество работ для создания")

    def handle(self, *args, **options):
        count = options["count"]

        self.stdout.write(self.style.WARNING(f"Создаю {count} тестовых работ..."))

        # Получаем или создаем тестовых студентов
        students = self._get_or_create_students()

        # Получаем или создаем уроки
        lessons = list(Lesson.objects.all()[:10])
        if not lessons:
            self.stdout.write(self.style.WARNING("Создаю тестовые уроки..."))
            lessons = self._create_test_lessons()
            if not lessons:
                self.stdout.write(self.style.ERROR("Не удалось создать уроки!"))
                return

        # Получаем или создаем ревьюера
        reviewer = self._get_or_create_reviewer()

        created_count = 0

        for i in range(count):
            student = random.choice(students)
            lesson = random.choice(lessons)

            # Проверяем, нет ли уже такой работы
            if LessonSubmission.objects.filter(student=student.student, lesson=lesson).exists():
                continue

            # Создаем работу с разными статусами
            status_choice = random.choices(
                ["pending", "changes_requested", "approved"],
                weights=[40, 30, 30],  # 40% pending, остальные по 30%
            )[0]

            submission = LessonSubmission.objects.create(
                student=student.student,
                lesson=lesson,
                lesson_url=f"https://github.com/student{i}/project-{lesson.slug}",
                status=status_choice,
                submitted_at=timezone.now() - timedelta(days=random.randint(0, 7)),
            )

            # Для проверенных работ создаем Review
            if status_choice in ["changes_requested", "approved"]:
                review_status = "approved" if status_choice == "approved" else "needs_work"

                review = Review.objects.create(
                    lesson_submission=submission,
                    reviewer=reviewer,
                    status=review_status,
                    comments=self._generate_comment(review_status),
                    rating=(
                        random.randint(3, 5)
                        if review_status == "approved"
                        else random.randint(1, 3)
                    ),
                    time_spent=random.randint(10, 60),
                    reviewed_at=timezone.now() - timedelta(days=random.randint(0, 5)),
                )

                # Для needs_work добавляем улучшения
                if review_status == "needs_work":
                    improvements_count = random.randint(2, 5)
                    for j in range(improvements_count):
                        StudentImprovement.objects.create(
                            review=review,
                            improvement_number=j + 1,
                            improvement_text=self._generate_improvement(j),
                            priority=random.choice(["high", "medium", "low"]),
                        )

                submission.mentor = student.student  # Student profile
                submission.reviewed_at = review.reviewed_at
                submission.save()

            created_count += 1

        self.stdout.write(self.style.SUCCESS(f"✅ Создано {created_count} работ студентов"))

        # Статистика
        total = LessonSubmission.objects.count()
        pending = LessonSubmission.objects.filter(status="pending").count()
        changes = LessonSubmission.objects.filter(status="changes_requested").count()
        approved = LessonSubmission.objects.filter(status="approved").count()

        self.stdout.write(self.style.SUCCESS("\n📊 Статистика работ:"))
        self.stdout.write(f"  Всего: {total}")
        self.stdout.write(f"  Ожидают проверки: {pending}")
        self.stdout.write(f"  Требуют доработки: {changes}")
        self.stdout.write(f"  Одобрено: {approved}")

    def _get_or_create_students(self):
        """Получает или создает тестовых студентов"""
        students = []

        for i in range(1, 11):  # 10 студентов
            email = f"student{i}@test.com"
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "first_name": "Студент",
                    "last_name": f"{i}",
                },
            )
            if created:
                user.set_password("test123")
                user.save()
                self.stdout.write(f"  Создан студент: {email}")

            students.append(user)

        return students

    def _get_or_create_reviewer(self):
        """Получает или создает тестового ревьюера"""
        email = "reviewer@test.com"
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "first_name": "Ревьюер",
                "last_name": "Тестовый",
            },
        )
        if created:
            user.set_password("test123")
            user.save()

        # Создаем или получаем Reviewer profile
        reviewer, created = Reviewer.objects.get_or_create(
            user=user, defaults={"bio": "Тестовый ревьюер для проверки работ", "is_active": True}
        )

        if created:
            # Добавляем все курсы
            reviewer.courses.set(Course.objects.all())
            self.stdout.write(f"  Создан ревьюер: {email}")
        else:
            # Если ревьюер уже существует, но у него нет курсов - назначаем все
            if reviewer.courses.count() == 0:
                reviewer.courses.set(Course.objects.all())
                self.stdout.write(f"  Назначены курсы ревьюеру: {email}")

        return reviewer

    def _generate_comment(self, status):
        """Генерирует комментарий ревьюера"""
        if status == "approved":
            comments = [
                "Отличная работа! Все требования выполнены.",
                "Хорошо реализовано. Код чистый и понятный.",
                "Молодец! Работа выполнена качественно.",
                "Все отлично! Можно переходить к следующему уроку.",
                "Прекрасная работа! Видно старание.",
            ]
        else:
            comments = [
                "Есть несколько моментов, которые нужно доработать.",
                "Хорошее начало, но нужны улучшения.",
                "Работа требует доработки по следующим пунктам:",
                "Неплохо, но есть что улучшить.",
                "Пожалуйста, внесите указанные исправления.",
            ]

        return random.choice(comments)

    def _generate_improvement(self, index):
        """Генерирует текст улучшения"""
        improvements = [
            "Добавить обработку ошибок для некорректных входных данных",
            "Улучшить читаемость кода: добавить комментарии к сложным участкам",
            "Оптимизировать алгоритм - текущая реализация неэффективна",
            "Добавить валидацию пользовательского ввода",
            "Исправить логическую ошибку в условии на строке X",
            "Переименовать переменные - использовать более понятные названия",
            "Добавить docstring для функций",
            "Убрать дублирование кода - вынести в отдельную функцию",
            "Исправить форматирование согласно PEP 8",
            "Добавить тесты для критических участков кода",
        ]

        return improvements[index % len(improvements)]

    def _create_test_lessons(self):
        """Создает тестовые уроки для курсов"""
        lessons = []
        courses = Course.objects.all()[:5]

        if not courses:
            self.stdout.write(self.style.ERROR("Нет курсов! Сначала создайте курсы."))
            return []

        lesson_names = [
            "Введение и основы",
            "Переменные и типы данных",
            "Условные операторы",
            "Циклы и итерации",
            "Функции",
            "Работа с данными",
            "ООП: Классы и объекты",
            "Обработка ошибок",
            "Работа с файлами",
            "Финальный проект",
        ]

        for course in courses:
            for i, name in enumerate(lesson_names, 1):  # Все 10 уроков на курс
                lesson_slug = f"{course.slug}-lesson-{i}"
                # Проверяем, не существует ли уже
                if Lesson.objects.filter(slug=lesson_slug).exists():
                    lesson = Lesson.objects.get(slug=lesson_slug)
                else:
                    lesson = Lesson.objects.create(
                        course=course, name=name, slug=lesson_slug, lesson_number=i
                    )
                lessons.append(lesson)

        self.stdout.write(self.style.SUCCESS(f"  Создано {len(lessons)} уроков"))
        return lessons
