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
    Представление для отображения списка всех курсов.

    GET:
        - Показывает все доступные курсы.

    Args:
        request (HttpRequest): HTTP-запрос пользователя.

    Returns:
        HttpResponse: Страница со списком курсов.
    """
    # Показываем только активные курсы
    courses = list(
        Course.objects.filter(status="active").select_related().prefetch_related("students")
    )
    return render(request, "courses/courses.html", {"courses": courses})


def course_detail_view(request: HttpRequest, course_slug: str) -> HttpResponse:
    """
    Представление для отображения деталей курса и его уроков.

    GET:
        - Показывает детали курса и список уроков.
        - Доступно для всех пользователей (не требует авторизации для просмотра)

    Args:
        request (HttpRequest): HTTP-запрос пользователя.
        course_slug (str): Slug курса.

    Returns:
        HttpResponse: Страница с деталями курса.
    """
    course = get_object_or_404(Course, slug=course_slug)
    lessons = course.lessons.all().prefetch_related("steps")
    has_access = False

    if request.user.is_authenticated:
        try:
            has_access = course.students.filter(user=request.user).exists()
        except Exception:
            has_access = False

    # Получаем другие активные курсы для рекомендаций
    other_courses = Course.objects.filter(status="active").exclude(id=course.id)[:3]

    # Подсчитываем общее количество шагов (заданий) в курсе
    total_steps = sum(lesson.steps.count() for lesson in lessons)

    # Рассчитываем примерное время прохождения (1 шаг = 0.5 часа)
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
