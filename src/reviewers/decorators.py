"""
Reviewers Decorators - Современные декораторы для проверки прав доступа ревьюеров.

Все декораторы используют централизованную систему из authentication.decorators.
Специфичные для ревьюеров проверки вынесены отдельно.

Автор: Pyland Team
Дата: 2025
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from functools import wraps
from typing import Any

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404

from authentication.models import Reviewer
from courses.models import Course

logger = logging.getLogger(__name__)


def active_reviewer_required(view_func: Callable) -> Callable:
    """
    Декоратор проверяет что ревьюер активен (is_active=True).

    Использовать ПОСЛЕ @require_any_role(['reviewer', 'mentor']).

    Args:
        view_func: Функция представления

    Returns:
        Обернутая функция с проверкой активности

    Example:
        @login_required
        @require_any_role(['reviewer', 'mentor'])
        @active_reviewer_required
        def take_submission(request, submission_id):
            ...
    """

    @wraps(view_func)
    def wrapper(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        try:
            reviewer = Reviewer.objects.get(user=request.user)

            if not reviewer.is_active:
                messages.warning(
                    request, "Ваш профиль ревьюера неактивен. Обратитесь к администратору."
                )
                logger.warning(
                    f"Inactive reviewer {request.user.email} tried to access {view_func.__name__}"
                )
                raise PermissionDenied("Reviewer is not active")

        except Reviewer.DoesNotExist as e:
            messages.error(request, "Профиль ревьюера не найден.")
            logger.error(f"Reviewer profile missing for {request.user.email}")
            raise PermissionDenied("Reviewer profile does not exist") from e

        return view_func(request, *args, **kwargs)

    return wrapper


def can_review_course(view_func: Callable) -> Callable:
    """
    Декоратор проверяет право ревьюера проверять работы по конкретному курсу.

    Ожидает параметр course_slug или course_id в kwargs view.
    Проверяет что курс есть в reviewer.courses.

    Использовать ПОСЛЕ @require_any_role(['reviewer', 'mentor']).

    Args:
        view_func: Функция представления

    Returns:
        Обернутая функция с проверкой доступа к курсу

    Example:
        @login_required
        @require_any_role(['reviewer', 'mentor'])
        @can_review_course
        def review_course_submissions(request, course_slug):
            ...
    """

    @wraps(view_func)
    def wrapper(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        # Получаем course_slug или course_id из kwargs
        course_slug = kwargs.get("course_slug")
        course_id = kwargs.get("course_id")

        if not course_slug and not course_id:
            logger.error("can_review_course decorator: no course_slug or course_id in kwargs")
            raise ValueError("can_review_course requires course_slug or course_id in view kwargs")

        # Получаем курс
        if course_slug:
            course = get_object_or_404(Course, slug=course_slug)
        else:
            course = get_object_or_404(Course, id=course_id)

        # Получаем ревьюера
        try:
            reviewer = Reviewer.objects.get(user=request.user)
        except Reviewer.DoesNotExist as e:
            messages.error(request, "Профиль ревьюера не найден.")
            logger.error(f"Reviewer profile missing for {request.user.email}")
            raise PermissionDenied("Reviewer profile does not exist") from e

        # Проверяем доступ к курсу
        if course not in reviewer.courses.all():
            messages.error(request, f'У вас нет прав для проверки работ по курсу "{course.title}".')
            logger.warning(
                f"Reviewer {request.user.email} tried to access course {course.slug} without permission"
            )
            raise PermissionDenied(f"Reviewer cannot review course {course.slug}")

        return view_func(request, *args, **kwargs)

    return wrapper


def max_reviews_per_day_check(view_func: Callable) -> Callable:
    """
    Декоратор проверяет лимит проверок ревьюера в день.

    Проверяет reviewer.max_reviews_per_day и количество проверок за сегодня.
    Если лимит превышен - отказывает в доступе.

    Использовать ПОСЛЕ @require_any_role(['reviewer', 'mentor']).

    Args:
        view_func: Функция представления

    Returns:
        Обернутая функция с проверкой лимита

    Example:
        @login_required
        @require_any_role(['reviewer', 'mentor'])
        @max_reviews_per_day_check
        def submit_review(request, submission_id):
            ...
    """

    @wraps(view_func)
    def wrapper(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        from django.utils import timezone

        from reviewers.models import Review

        try:
            reviewer = Reviewer.objects.get(user=request.user)

            # Получаем количество проверок за сегодня
            today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_reviews_count = Review.objects.filter(
                reviewer=reviewer, reviewed_at__gte=today_start
            ).count()

            # Проверяем лимит (если установлен)
            max_reviews = getattr(reviewer, "max_reviews_per_day", None)

            # Для POST запросов (создание review) блокируем если достигнут лимит
            # Для GET запросов (просмотр формы) показываем предупреждение
            if max_reviews:
                if request.method == "POST" and today_reviews_count >= max_reviews:
                    # Блокируем создание новой проверки
                    messages.error(
                        request,
                        f"Вы достигли дневного лимита проверок ({max_reviews}). Попробуйте завтра.",
                    )
                    logger.warning(
                        f"Reviewer {request.user.email} tried to exceed daily limit: {today_reviews_count}/{max_reviews}"
                    )
                    # Редиректим на dashboard вместо PermissionDenied
                    from django.shortcuts import redirect

                    return redirect("reviewers:dashboard")
                elif request.method == "GET" and today_reviews_count >= max_reviews:
                    # Показываем предупреждение, но разрешаем просмотр
                    messages.warning(
                        request,
                        f"Вы достигли дневного лимита проверок ({max_reviews}). Новые проверки будут заблокированы.",
                    )
                    logger.info(
                        f"Reviewer {request.user.email} at daily limit: {today_reviews_count}/{max_reviews}"
                    )

        except Reviewer.DoesNotExist as e:
            messages.error(request, "Профиль ревьюера не найден.")
            raise PermissionDenied("Reviewer profile does not exist") from e

        return view_func(request, *args, **kwargs)

    return wrapper
