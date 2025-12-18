"""
Management команда для исправления метаданных в LessonSubmission.

Проблема: Старые проверенные работы (до рефакторинга) имеют Review объект,
но у LessonSubmission не заполнены поля reviewed_at и mentor.

Решение: Восстанавливаем эти поля из связанного Review объекта.

Usage:
    python manage.py fix_submission_metadata
    python manage.py fix_submission_metadata --dry-run
"""

import logging

from django.core.management.base import BaseCommand
from django.utils import timezone

from reviewers.models import LessonSubmission

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Исправляет метаданные в LessonSubmission (reviewed_at, mentor) из связанных Review объектов"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Показать что будет изменено, но не применять изменения",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        if dry_run:
            self.stdout.write(
                self.style.WARNING("🔍 DRY RUN режим - изменения не будут применены\n")
            )

        # Проверенные работы без reviewed_at
        submissions_no_reviewed_at = LessonSubmission.objects.filter(
            status__in=["approved", "changes_requested"],
            reviewed_at__isnull=True,
            review__isnull=False,
        ).select_related("review")

        # Проверенные работы без mentor
        submissions_no_mentor = LessonSubmission.objects.filter(
            status__in=["approved", "changes_requested"], mentor__isnull=True, review__isnull=False
        ).select_related("review", "review__reviewer", "review__reviewer__user")

        self.stdout.write("📊 Найдено работ:")
        self.stdout.write(f"  - БЕЗ reviewed_at: {submissions_no_reviewed_at.count()}")
        self.stdout.write(f"  - БЕЗ mentor: {submissions_no_mentor.count()}\n")

        # Обновляем reviewed_at
        updated_at = 0
        for submission in submissions_no_reviewed_at:
            review = submission.review
            if review:
                new_reviewed_at = review.reviewed_at or timezone.now()

                if dry_run:
                    self.stdout.write(
                        f"  ℹ️  Submission {submission.id}: " f"reviewed_at = {new_reviewed_at}"
                    )
                else:
                    submission.reviewed_at = new_reviewed_at
                    submission.save(update_fields=["reviewed_at"])

                updated_at += 1

        if updated_at > 0:
            status = self.style.SUCCESS if not dry_run else self.style.WARNING
            action = "Обновлено" if not dry_run else "Будет обновлено"
            self.stdout.write(status(f"\n✅ {action} reviewed_at: {updated_at}"))

        # Обновляем mentor
        updated_mentor = 0
        skipped_mentor = 0

        for submission in submissions_no_mentor:
            review = submission.review
            if review and review.reviewer:
                reviewer = review.reviewer

                # Проверяем есть ли у reviewer профиль студента
                if hasattr(reviewer.user, "student"):
                    new_mentor = reviewer.user.student

                    if dry_run:
                        self.stdout.write(
                            f"  ℹ️  Submission {submission.id}: " f"mentor = {new_mentor.user.email}"
                        )
                    else:
                        submission.mentor = new_mentor
                        submission.save(update_fields=["mentor"])

                    updated_mentor += 1
                else:
                    skipped_mentor += 1
                    if dry_run:
                        self.stdout.write(
                            self.style.WARNING(
                                f"  ⚠️  Submission {submission.id}: "
                                f"Ревьюер {reviewer.user.email} не имеет профиля студента (пропущено)"
                            )
                        )

        if updated_mentor > 0:
            status = self.style.SUCCESS if not dry_run else self.style.WARNING
            action = "Обновлено" if not dry_run else "Будет обновлено"
            self.stdout.write(status(f"\n✅ {action} mentor: {updated_mentor}"))

        if skipped_mentor > 0:
            self.stdout.write(
                self.style.WARNING(f"⚠️  Пропущено (ревьюер без профиля студента): {skipped_mentor}")
            )

        if not dry_run:
            self.stdout.write(self.style.SUCCESS("\n🎉 Готово! Все метаданные исправлены."))
        else:
            self.stdout.write(
                self.style.WARNING("\n💡 Для применения изменений запустите без --dry-run")
            )

        logger.info(
            f"fix_submission_metadata: "
            f"reviewed_at={updated_at}, mentor={updated_mentor}, skipped={skipped_mentor}, "
            f"dry_run={dry_run}"
        )
