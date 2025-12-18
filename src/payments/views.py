from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from courses.models import Course


@login_required
def purchase_view(request: HttpRequest, course_slug: str) -> HttpResponse:
    """
    Представление для страницы покупки курса.

    Отображает детали выбранного курса и кнопку оплаты.
    После успешной оплаты перенаправляет пользователя на страницу курса.

    Args:
        request (HttpRequest): HTTP-запрос пользователя.
        course_slug (str): Slug курса.

    Returns:
        HttpResponse: Страница покупки курса или редирект на детали курса.
    """
    course = get_object_or_404(Course, slug=course_slug)
    if request.method == "POST":
        return redirect("courses:course_detail", course_slug=course.slug)
    return render(request, "payments/purchase.html", {"course": course})
