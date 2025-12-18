from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from authentication.models import Student
from courses.models import Course, Lesson, Step
from reviewers.models import StepProgress

User = get_user_model()


class Command(BaseCommand):
    help = "Показывает статистику PyLand платформы"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("🎓 === СТАТИСТИКА PYLAND ПЛАТФОРМЫ ==="))

        # Общая статистика
        users_count = User.objects.count()
        students_count = Student.objects.count()
        courses_count = Course.objects.count()
        lessons_count = Lesson.objects.count()
        steps_count = Step.objects.count()
        progress_count = StepProgress.objects.count()

        self.stdout.write("\n📊 ОБЩАЯ СТАТИСТИКА:")
        self.stdout.write(f"   👥 Пользователей: {users_count}")
        self.stdout.write(f"   👤 Студентов: {students_count}")
        self.stdout.write(f"   📚 Курсов: {courses_count}")
        self.stdout.write(f"   📖 Уроков: {lessons_count}")
        self.stdout.write(f"   📝 Шагов: {steps_count}")
        self.stdout.write(f"   📈 Записей прогресса: {progress_count}")

        # Статистика по курсам
        self.stdout.write("\n📚 КУРСЫ И АКТИВНОСТЬ:")
        for course in Course.objects.all().order_by("name"):
            enrolled = course.students.count()
            lessons_count = course.lessons.count()
            steps_count = Step.objects.filter(lesson__course=course).count()
            completed_steps = StepProgress.objects.filter(
                step__lesson__course=course, is_completed=True
            ).count()
            completion_rate = (
                round((completed_steps / (steps_count * enrolled) * 100), 1)
                if steps_count > 0 and enrolled > 0
                else 0
            )

            self.stdout.write(f"\n   📘 {course.name}")
            self.stdout.write(f"      👥 Студентов: {enrolled}")
            self.stdout.write(f"      📖 Уроков: {lessons_count}")
            self.stdout.write(f"      📝 Шагов: {steps_count}")
            self.stdout.write(f"      ✅ Выполнено: {completed_steps}")
            self.stdout.write(f"      📊 Процент завершения: {completion_rate}%")

        # Топ активные студенты
        self.stdout.write("\n🏆 ТОП-5 АКТИВНЫХ СТУДЕНТОВ:")
        top_students = []
        for profile in Student.objects.filter(courses__isnull=False).distinct():
            completed = StepProgress.objects.filter(profile=profile, is_completed=True).count()
            if completed > 0:
                top_students.append((profile, completed))

        top_students.sort(key=lambda x: x[1], reverse=True)
        for i, (profile, completed) in enumerate(top_students[:5], 1):
            user = profile.user
            courses_count = profile.courses.count()
            self.stdout.write(
                f"   {i}. {user.first_name} {user.last_name}: "
                f"{completed} шагов в {courses_count} курсах"
            )

        # Последняя активность
        recent_progress = StepProgress.objects.filter(is_completed=True).order_by("-completed_at")[
            :5
        ]

        if recent_progress:
            self.stdout.write("\n⏰ ПОСЛЕДНЯЯ АКТИВНОСТЬ:")
            for progress in recent_progress:
                user = progress.profile.user
                step_name = progress.step.name
                completed_time = progress.completed_at.strftime("%d.%m.%Y %H:%M")
                self.stdout.write(
                    f"   • {user.first_name} {user.last_name} завершил: "
                    f'"{step_name}" ({completed_time})'
                )

        self.stdout.write(self.style.SUCCESS("\n✨ Система готова к использованию! ✨"))
