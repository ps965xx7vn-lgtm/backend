"""
Management команда для создания тестовых работ студентов для ревьюеров.

Использование:
    python manage.py create_test_submissions
    python manage.py create_test_submissions --count 10
"""

import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from authentication.models import Reviewer as ReviewerProfile
from authentication.models import Role, Student
from courses.models import Lesson
from reviewers.models import LessonSubmission


class Command(BaseCommand):
    help = "Создает тестовые работы студентов для проверки"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=5,
            help="Количество работ для создания (по умолчанию 5)",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Удалить существующие работы перед созданием",
        )

    def handle(self, *args, **options):
        """Создает тестовые работы студентов"""

        if options["clear"]:
            self.stdout.write(self.style.WARNING("Очистка существующих работ..."))
            LessonSubmission.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("✓ Данные очищены\n"))

        self.stdout.write(self.style.HTTP_INFO("=== СОЗДАНИЕ ТЕСТОВЫХ РАБОТ ===\n"))

        # Получаем или создаем студента
        student_role, _ = Role.objects.get_or_create(name="student")
        student, created = Student.objects.get_or_create(
            user__email="student@test.com", defaults={"user": None}
        )

        if created or not student.user:
            from django.contrib.auth import get_user_model

            User = get_user_model()
            user, user_created = User.objects.get_or_create(
                email="student@test.com",
                defaults={
                    "first_name": "Тестовый",
                    "last_name": "Студент",
                    "is_active": True,
                },
            )
            if user_created:
                user.set_password("test123")
                user.save()
            user.role = student_role
            user.save(update_fields=["role"])
            student.user = user
            student.save()
            self.stdout.write(self.style.SUCCESS(f"✓ Создан студент: {user.email}"))
        else:
            self.stdout.write(f"↻ Студент уже существует: {student.user.email}")

        # Получаем уроки
        lessons = list(Lesson.objects.select_related("course").all()[:10])

        if not lessons:
            self.stdout.write(
                self.style.ERROR("❌ Уроки не найдены! Сначала запустите populate_lessons_data")
            )
            return

        # Получаем ревьюера
        reviewer_profiles = ReviewerProfile.objects.all()
        if reviewer_profiles.exists():
            reviewer = reviewer_profiles.first()
            # Добавляем курсы ревьюеру
            for lesson in lessons:
                if lesson.course not in reviewer.courses.all():
                    reviewer.courses.add(lesson.course)
            self.stdout.write(f"✓ Назначены курсы ревьюеру: {reviewer.user.email}\n")

        # Добавляем студента на все курсы из уроков
        for lesson in lessons:
            if lesson.course not in student.courses.all():
                student.courses.add(lesson.course)
        self.stdout.write(f"✓ Студент записан на {len(lessons)} курсов\n")

        count = options["count"]
        created_count = 0
        statuses = [
            "pending",
            "pending",
            "pending",
            "approved",
            "changes_requested",
        ]  # Больше pending

        test_urls = [
            "https://github.com/student/homework-1",
            "https://github.com/student/homework-2",
            "https://github.com/student/project-python",
            "https://replit.com/@student/lesson-task",
            "https://codesandbox.io/s/student-work",
        ]

        for i in range(count):
            lesson = random.choice(lessons)
            status = random.choice(statuses)
            url = random.choice(test_urls)

            # Создаем дату в пределах последних 7 дней
            days_ago = random.randint(0, 7)
            hours_ago = random.randint(0, 23)
            submitted_at = timezone.now() - timedelta(days=days_ago, hours=hours_ago)

            # Используем get_or_create чтобы избежать дублей
            submission, created = LessonSubmission.objects.get_or_create(
                student=student,
                lesson=lesson,
                defaults={
                    "lesson_url": f"{url}-{i+1}",
                    "status": status,
                },
            )

            if created:
                # Устанавливаем время вручную
                submission.submitted_at = submitted_at
                submission.save(update_fields=["submitted_at"])

                created_count += 1
                status_icon = "⏳" if status == "pending" else "✅" if status == "approved" else "✏️"
                self.stdout.write(
                    self.style.SUCCESS(
                        f"{status_icon} Работа {i+1}: {lesson.course.name} → {lesson.name} ({status})"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"⚠ Работа {i+1}: уже существует для {lesson.name}")
                )

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"Создано работ: {created_count}"))
        self.stdout.write(self.style.SUCCESS("✓ Тестовые работы успешно созданы!"))
        self.stdout.write("")
        self.stdout.write(self.style.NOTICE("Теперь вы можете:"))
        self.stdout.write("  • Зайти на страницу /reviewers/ под аккаунтом ревьюера")
        self.stdout.write("  • Просмотреть работы на проверке")
        self.stdout.write("  • Проверить работы студентов")
