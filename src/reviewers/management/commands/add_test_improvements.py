"""
Management command для добавления тестовых улучшений к существующему review.
"""

import uuid

from django.core.management.base import BaseCommand

from reviewers.models import LessonSubmission, StudentImprovement


class Command(BaseCommand):
    help = "Добавляет тестовые улучшения к указанному submission"

    def add_arguments(self, parser):
        parser.add_argument(
            "submission_id", type=str, help="UUID submission для добавления improvements"
        )

    def handle(self, *args, **options):
        submission_id = options["submission_id"]

        try:
            submission_uuid = uuid.UUID(submission_id)
            submission = LessonSubmission.objects.select_related("review").get(id=submission_uuid)

            if not hasattr(submission, "review"):
                self.stdout.write(self.style.ERROR(f"У submission {submission_id} нет review"))
                return

            review = submission.review

            # Удаляем старые improvements если есть
            submission.improvements.all().delete()

            # Создаем новые improvements с привязкой к submission и review
            improvements_data = [
                {
                    "improvement_number": 1,
                    "improvement_text": "Необходимо добавить больше комментариев к коду для лучшего понимания логики работы",
                    "priority": "high",
                },
                {
                    "improvement_number": 2,
                    "improvement_text": "Рекомендуется использовать более описательные названия переменных вместо однобуквенных",
                    "priority": "medium",
                },
                {
                    "improvement_number": 3,
                    "improvement_text": "Стоит добавить обработку исключений для повышения надежности кода",
                    "priority": "medium",
                },
                {
                    "improvement_number": 4,
                    "improvement_text": "Следует разбить большую функцию на несколько маленьких для улучшения читаемости",
                    "priority": "low",
                },
            ]

            for data in improvements_data:
                StudentImprovement.objects.create(
                    lesson_submission=submission, review=review, **data
                )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Успешно создано {len(improvements_data)} improvements для submission {submission_id}"
                )
            )

            self.stdout.write("\nСозданные improvements:")
            for imp in submission.improvements.all():
                self.stdout.write(
                    f"  {imp.improvement_number}. [{imp.priority}] {imp.improvement_text}"
                )

        except ValueError:
            self.stdout.write(self.style.ERROR(f"Неверный формат UUID: {submission_id}"))
        except LessonSubmission.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Submission с ID {submission_id} не найден"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка: {str(e)}"))
