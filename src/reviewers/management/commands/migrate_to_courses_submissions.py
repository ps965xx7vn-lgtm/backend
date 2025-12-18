"""
Команда для переноса данных из reviewers.LessonSubmission в courses.LessonSubmission.

Использование:
    python manage.py migrate_to_courses_submissions
"""

from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = "Переносит данные из reviewers.LessonSubmission в courses.LessonSubmission"

    def handle(self, *args, **options):
        """Переносит данные между моделями"""

        self.stdout.write(self.style.HTTP_INFO("=== ПЕРЕНОС ДАННЫХ ===\n"))

        # Импортируем модели
        from courses.models import LessonSubmission as CourseSubmission
        from reviewers.models import LessonSubmission as ReviewerSubmission

        reviewer_submissions = ReviewerSubmission.objects.all()
        total = reviewer_submissions.count()

        if total == 0:
            self.stdout.write(self.style.WARNING("Нет данных для переноса"))
            return

        self.stdout.write(f"Найдено работ в reviewers: {total}")
        self.stdout.write("")

        migrated = 0
        skipped = 0
        errors = 0

        with transaction.atomic():
            for rev_sub in reviewer_submissions:
                try:
                    # Проверяем, есть ли уже такая работа
                    existing = CourseSubmission.objects.filter(
                        student=rev_sub.student, lesson=rev_sub.lesson
                    ).first()

                    if existing:
                        self.stdout.write(
                            self.style.WARNING(
                                f"⚠ Пропущена (уже существует): {rev_sub.student.user.email} → {rev_sub.lesson.name}"
                            )
                        )
                        skipped += 1
                        continue

                    # Маппинг статусов
                    status_map = {
                        "pending": "pending",
                        "accepted": "approved",
                        "rejected": "changes_requested",
                    }

                    # Создаем новую запись в courses
                    CourseSubmission.objects.create(
                        student=rev_sub.student,
                        lesson=rev_sub.lesson,
                        lesson_url=rev_sub.lesson_url,
                        status=status_map.get(rev_sub.status, "pending"),
                        submitted_at=rev_sub.submitted_at,
                    )

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✓ Перенесена: {rev_sub.student.user.email} → {rev_sub.lesson.name}"
                        )
                    )
                    migrated += 1

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f"✗ Ошибка: {rev_sub.student.user.email} → {rev_sub.lesson.name}: {e}"
                        )
                    )
                    errors += 1

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"Перенесено: {migrated}"))
        self.stdout.write(self.style.WARNING(f"Пропущено: {skipped}"))
        if errors > 0:
            self.stdout.write(self.style.ERROR(f"Ошибок: {errors}"))

        self.stdout.write("")
        self.stdout.write(
            self.style.NOTICE("Теперь можно удалить старую модель reviewers.LessonSubmission")
        )
