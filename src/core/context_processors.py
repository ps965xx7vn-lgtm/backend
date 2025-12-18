"""
Core Context Processors

Контекст-процессоры для добавления глобальных данных в шаблоны:
- footer_data: статистика и популярные курсы для футера

Подключается в settings.py -> TEMPLATES -> OPTIONS -> context_processors
"""

from typing import Any

from django.http import HttpRequest


def footer_data(request: HttpRequest) -> dict[str, Any]:
    """
    Добавляет в контекст данные для футера: только существующие курсы из БД.
    Этот контекст-процессор подключается в TEMPLATES -> OPTIONS -> context_processors
    """
    try:
        from authentication.models import Student
        from courses.models import Course, Lesson

        # Берем только существующие курсы, максимум 6 штук
        popular_courses = (
            Course.objects.filter(name__isnull=False)
            .exclude(name="")
            .prefetch_related("students")
            .order_by("-created_at")[:6]
        )

        total_courses = Course.objects.count()
        total_students = Student.objects.count()
        total_mentors = Student.objects.filter(role__name__iexact="mentor").count()
        total_lessons = Lesson.objects.count()

        footer_stats = {
            "total_courses": total_courses,
            "total_students": total_students,
            "total_mentors": total_mentors,
            "total_lessons": total_lessons,
            "total_courses_display": f"{total_courses}+" if total_courses > 0 else "—",
            "total_students_display": f"{total_students}+" if total_students > 0 else "—",
            "total_mentors_display": f"{total_mentors}+" if total_mentors > 0 else "—",
            "total_lessons_display": f"{total_lessons}+" if total_lessons > 0 else "—",
        }

        return {
            "footer_popular_courses": popular_courses,
            "footer_stats": footer_stats,
        }
    except Exception:
        # Если что-то пойдет не так (миграции/импорт), возвращаем безопасные значения
        return {
            "footer_popular_courses": [],
            "footer_stats": {
                "total_courses": 0,
                "total_students": 0,
                "total_mentors": 0,
                "total_lessons": 0,
                "total_courses_display": "—",
                "total_students_display": "—",
                "total_mentors_display": "—",
                "total_lessons_display": "—",
            },
        }


def header_courses(request: HttpRequest) -> dict[str, Any]:
    """
    Добавляет в контекст курсы для выпадающего меню в header.
    Берет все опубликованные курсы из БД, упорядоченные по категориям.
    """
    try:
        from courses.models import Course

        # Получаем все курсы, сортируя по категории и дате создания
        header_courses_list = (
            Course.objects.filter(name__isnull=False)
            .exclude(name="")
            .order_by("category", "-created_at")
        )

        return {
            "header_courses": header_courses_list,
        }
    except Exception:
        # Если что-то пойдет не так, возвращаем пустой список
        return {
            "header_courses": [],
        }
