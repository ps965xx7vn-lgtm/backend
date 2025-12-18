"""
Management команда для управления кэшем прогресса обучения.
Позволяет очищать, разогревать и получать статистику кэша.
"""

import time

from django.core.cache import cache
from django.core.management.base import BaseCommand

from authentication.models import Student
from students.cache_utils import ProgressCacheManager


class Command(BaseCommand):
    help = "Управление кэшем прогресса обучения"

    def add_arguments(self, parser):
        parser.add_argument(
            "action",
            choices=["clear", "warmup", "stats", "clear_all"],
            help="Действие: clear (очистить), warmup (разогреть), stats (статистика), clear_all (очистить весь кэш)",
        )

        parser.add_argument(
            "--student-id", type=str, help="ID студента для операций (необязательно для clear_all)"
        )

        parser.add_argument("--course-id", type=str, help="ID курса для частичной очистки кэша")

        parser.add_argument("--lesson-id", type=str, help="ID урока для частичной очистки кэша")

    def handle(self, *args, **options):
        action = options["action"]
        student_id = options.get("student_id")
        course_id = options.get("course_id")
        lesson_id = options.get("lesson_id")

        if action == "clear_all":
            self.clear_all_cache()
        elif action in ["clear", "warmup", "stats"]:
            if not student_id:
                self.stdout.write(self.style.ERROR("Для этого действия требуется --student-id"))
                return

            if action == "clear":
                self.clear_cache(student_id, course_id, lesson_id)
            elif action == "warmup":
                self.warmup_cache(student_id)
            elif action == "stats":
                self.show_stats(student_id)

    def clear_all_cache(self):
        """Очистить весь кэш"""
        cache.clear()
        self.stdout.write(self.style.SUCCESS("Весь кэш очищен"))

    def clear_cache(self, student_id, course_id=None, lesson_id=None):
        """Очистить кэш для конкретного студента"""
        try:
            ProgressCacheManager.invalidate_user_cache(student_id, course_id, lesson_id)

            scope = "студента"
            if course_id:
                scope += f" и курса {course_id}"
            if lesson_id:
                scope += f" и урока {lesson_id}"

            self.stdout.write(self.style.SUCCESS(f"Кэш {scope} {student_id} очищен"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка при очистке кэша: {e}"))

    def warmup_cache(self, student_id):
        """Разогреть кэш для студента"""
        try:
            student = Student.objects.get(id=student_id)
            start_time = time.time()

            ProgressCacheManager.warm_up_cache(student)

            elapsed = time.time() - start_time
            self.stdout.write(
                self.style.SUCCESS(f"Кэш для студента {student_id} разогрет за {elapsed:.2f} сек")
            )
        except Student.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Студент {student_id} не найден"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка при разогреве кэша: {e}"))

    def show_stats(self, student_id):
        """Показать статистику кэша для студента"""
        try:
            stats = ProgressCacheManager.get_cache_stats(student_id)

            self.stdout.write(self.style.SUCCESS(f"Статистика кэша для студента {student_id}:"))

            total_size = 0
            cached_count = 0

            for key, stat in stats.items():
                status = "✓" if stat["exists"] else "✗"
                size = stat["size"]
                total_size += size
                if stat["exists"]:
                    cached_count += 1

                self.stdout.write(f"  {status} {key}: {size} байт")

            self.stdout.write(f"\nИтого: {cached_count}/{len(stats)} записей, {total_size} байт")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка при получении статистики: {e}"))
