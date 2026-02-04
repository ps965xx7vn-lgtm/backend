"""
Courses Views Module - Django views для публичного каталога курсов.

Этот модуль содержит представления для просмотра курсов:

Публичные представления:
    - course_list_view: Каталог всех активных курсов
    - course_detail_view: Детальная страница курса с описанием и программой

Особенности:
    - Показываются только активные курсы (status='active')
    - Оптимизация запросов через select_related и prefetch_related
    - Публичный доступ без требования авторизации
    - Slug-based URL для SEO

Автор: Pyland Team
Дата: 2025
"""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from .models import Course


def course_list_view(request: HttpRequest) -> HttpResponse:
    """
    Представление для отображения списка всех активных курсов.

    Показывает публичный каталог курсов со статусом 'active'.
    Использует оптимизацию запросов через select_related.

    Args:
        request: HTTP-запрос пользователя

    Returns:
        HttpResponse: Отрендеренная страница courses/courses.html со списком курсов

    Template context:
        courses: List[Course] - список активных курсов
    """
    courses = list(Course.objects.filter(status="active").select_related())
    return render(request, "courses/courses.html", {"courses": courses})


def course_detail_view(request: HttpRequest, course_slug: str) -> HttpResponse:
    """
    Представление для отображения детальной информации о курсе.

    Показывает полное описание курса, список уроков с шагами,
    информацию о доступе пользователя и рекомендуемые курсы.
    Рассчитывает общее количество шагов и примерное время прохождения.

    Args:
        request: HTTP-запрос пользователя
        course_slug: Slug курса для идентификации

    Returns:
        HttpResponse: Отрендеренная страница course_detail.html с деталями курса

    Raises:
        Http404: Если курс с указанным slug не найден

    Template context:
        course: Course - объект курса
        lessons: QuerySet[Lesson] - уроки курса с prefetch шагов
        has_access: bool - имеет ли текущий пользователь доступ к курсу
        courses: QuerySet[Course] - другие активные курсы для рекомендаций (до 3)
        total_steps: int - общее количество шагов в курсе
        estimated_hours: float - примерное время прохождения (1 шаг = 0.5 часа)
    """
    course = get_object_or_404(Course, slug=course_slug)
    lessons = course.lessons.all().prefetch_related("steps")
    has_access = False

    if request.user.is_authenticated:
        try:
            has_access = course.student_enrollments.filter(user=request.user).exists()
        except Exception:
            has_access = False

    other_courses = Course.objects.filter(status="active").exclude(id=course.id)[:3]

    total_steps = sum(lesson.steps.count() for lesson in lessons)

    estimated_hours = total_steps * 0.5

    return render(
        request,
        "courses/course_detail.html",
        {
            "course": course,
            "lessons": lessons,
            "has_access": has_access,
            "courses": other_courses,
            "total_steps": total_steps,
            "estimated_hours": estimated_hours,
        },
    )
