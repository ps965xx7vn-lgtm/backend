"""
Reviewers Views Module - Django views для панели ревьюера.

Современная архитектура на основе students/views.py:
- Чистые function-based views
- Декораторы из authentication + reviewers
- Полное кэширование
- Type hints
- Подробная документация

Автор: Pyland Team
Дата: 2025
"""

from __future__ import annotations

import logging
from uuid import UUID

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import models
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from authentication.decorators import require_any_role
from authentication.models import Reviewer
from reviewers.decorators import max_reviews_per_day_check
from reviewers.models import LessonSubmission, Review, StudentImprovement

from .cache_utils import get_reviewer_stats, invalidate_reviewer_cache
from .forms import ReviewerProfileForm

logger = logging.getLogger(__name__)


@login_required
@require_any_role(["reviewer", "mentor"], redirect_url="/")
def dashboard_view(request: HttpRequest) -> HttpResponse:
    """
    Главная страница ревьюера с статистикой и ожидающими работами.

    Args:
        request: HTTP запрос

    Returns:
        HttpResponse: Отрендеренная страница dashboard
    """
    reviewer = get_object_or_404(Reviewer, user=request.user)

    # Получаем статистику из кэша
    stats = get_reviewer_stats(reviewer.id)

    # Дополнительная статистика для dashboard
    reviews = Review.objects.filter(reviewer=reviewer)
    stats["approved_count"] = reviews.filter(status="approved").count()
    stats["needs_work_count"] = reviews.filter(status="needs_work").count()

    # Получаем последние 5 ожидающих работ для курсов ревьюера
    pending_submissions = (
        LessonSubmission.objects.filter(status="pending", lesson__course__in=reviewer.courses.all())
        .select_related("student", "lesson", "lesson__course")
        .order_by("submitted_at")[:5]
    )

    # Получаем последние проверки ревьюера
    recent_reviews = (
        Review.objects.filter(reviewer=reviewer)
        .select_related("lesson_submission__student__user", "lesson_submission__lesson__course")
        .order_by("-reviewed_at")[:7]
    )

    # Статистика активности за последние 7 дней
    from datetime import timedelta

    from django.db.models import Count
    from django.db.models.functions import TruncDate

    today = timezone.now().date()
    week_ago = today - timedelta(days=6)

    # Группируем проверки по дням
    daily_activity = (
        Review.objects.filter(reviewer=reviewer, reviewed_at__date__gte=week_ago)
        .annotate(date=TruncDate("reviewed_at"))
        .values("date")
        .annotate(
            total=Count("id"),
            approved=Count("id", filter=models.Q(status="approved")),
            needs_work=Count("id", filter=models.Q(status="needs_work")),
        )
        .order_by("date")
    )

    # Создаём полный список дней за неделю
    activity_by_day = []
    for i in range(7):
        day = week_ago + timedelta(days=i)
        day_data = next((item for item in daily_activity if item["date"] == day), None)
        activity_by_day.append(
            {
                "date": day,
                "day_name": day.strftime("%a"),  # Mon, Tue, etc
                "day_number": day.day,
                "total": day_data["total"] if day_data else 0,
                "approved": day_data["approved"] if day_data else 0,
                "needs_work": day_data["needs_work"] if day_data else 0,
                "is_today": day == today,
            }
        )

    # Добавляем pending_count для навигации
    pending_count = LessonSubmission.objects.filter(
        status="pending", lesson__course__in=reviewer.courses.all()
    ).count()

    logger.info(f"Reviewer {reviewer.user.email} accessed dashboard")

    return render(
        request,
        "reviewers/dashboard.html",
        {
            "reviewer": reviewer,
            "stats": stats,
            "pending_submissions": pending_submissions,
            "recent_reviews": recent_reviews,
            "pending_count": pending_count,
            "activity_by_day": activity_by_day,
        },
    )


@login_required
@require_any_role(["reviewer", "mentor"], redirect_url="/")
def submissions_list_view(request: HttpRequest) -> HttpResponse:
    """
    Список работ на проверку с фильтрами и пагинацией.

    Args:
        request: HTTP запрос

    Returns:
        HttpResponse: Отрендеренная страница со списком работ
    """
    reviewer = get_object_or_404(Reviewer, user=request.user)

    # Базовый queryset работ для курсов ревьюера
    submissions = LessonSubmission.objects.filter(
        lesson__course__in=reviewer.courses.all()
    ).select_related("student", "lesson", "lesson__course")

    # Получаем параметры фильтров
    status_filter = request.GET.get("status", "")
    course_filter = request.GET.get("course", "")

    # Применяем фильтры
    if status_filter:
        submissions = submissions.filter(status=status_filter)
    if course_filter:
        submissions = submissions.filter(lesson__course_id=course_filter)

    # Статистика для карточек
    all_submissions = LessonSubmission.objects.filter(lesson__course__in=reviewer.courses.all())
    pending_count = all_submissions.filter(status="pending").count()
    changes_requested_count = all_submissions.filter(status="changes_requested").count()
    approved_count = all_submissions.filter(status="approved").count()
    total_count = all_submissions.count()

    # Пагинация с сортировкой: сначала pending, потом остальные по дате
    from django.db.models import Case, IntegerField, When

    submissions_sorted = submissions.annotate(
        status_priority=Case(
            When(status="pending", then=0),
            When(status="changes_requested", then=1),
            When(status="approved", then=2),
            default=3,
            output_field=IntegerField(),
        )
    ).order_by("status_priority", "-submitted_at")

    paginator = Paginator(submissions_sorted, 20)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    # Добавляем расчёт времени ожидания для каждой работы
    now = timezone.now()
    for submission in page_obj:
        if submission.submitted_at:
            wait_delta = now - submission.submitted_at
            wait_minutes = int(wait_delta.total_seconds() / 60)

            if wait_minutes < 60:
                submission.wait_time_display = f"{wait_minutes} мин"
            elif wait_minutes < 1440:  # меньше суток
                hours = wait_minutes // 60
                submission.wait_time_display = f"{hours} ч"
            else:
                days = wait_minutes // 1440
                submission.wait_time_display = f"{days} дн"
        else:
            submission.wait_time_display = None

    logger.info(f"Ревьюер {reviewer.user.email} просматривает список работ")

    return render(
        request,
        "reviewers/submissions_list.html",
        {
            "reviewer": reviewer,
            "submissions": page_obj,
            "page_obj": page_obj,
            "is_paginated": page_obj.has_other_pages(),
            "available_courses": reviewer.courses.all(),
            "pending_count": pending_count,
            "changes_requested_count": changes_requested_count,
            "approved_count": approved_count,
            "total_count": total_count,
        },
    )


@login_required
@require_any_role(["reviewer", "mentor"], redirect_url="/")
@max_reviews_per_day_check
def submission_review_view(request: HttpRequest, submission_id: UUID) -> HttpResponse:
    """
    Проверка конкретной работы студента.

    Args:
        request: HTTP запрос
        submission_id: UUID работы для проверки

    Returns:
        HttpResponse: Форма проверки (GET) или редирект после сохранения (POST)
    """
    reviewer = get_object_or_404(Reviewer, user=request.user)
    submission = get_object_or_404(
        LessonSubmission.objects.select_related("student", "lesson", "lesson__course"),
        id=submission_id,
        lesson__course__in=reviewer.courses.all(),
    )

    # Получаем статистику для отображения лимита
    from reviewers.cache_utils import get_reviewer_stats

    stats = get_reviewer_stats(reviewer.id)

    if request.method == "POST":
        try:
            # Получаем данные из формы
            status = request.POST.get("status")
            comments = request.POST.get("comments", "").strip()

            # Валидация
            if not status:
                messages.error(request, _("Необходимо выбрать статус проверки"))
                return render(
                    request,
                    "reviewers/submission_review.html",
                    {
                        "reviewer": reviewer,
                        "submission": submission,
                        "form_errors": _("Необходимо выбрать статус проверки"),
                        "stats": stats,
                        "reviews_today": stats.get("reviews_today", 0),
                        "max_reviews": reviewer.max_reviews_per_day,
                        "reviews_remaining": reviewer.max_reviews_per_day
                        - stats.get("reviews_today", 0),
                        "limit_reached": stats.get("reviews_today", 0)
                        >= reviewer.max_reviews_per_day,
                        "progress_percentage": (
                            int(
                                stats.get("reviews_today", 0) / reviewer.max_reviews_per_day * 100
                            )
                            if reviewer.max_reviews_per_day > 0
                            else 0
                        ),
                    },
                )

            if len(comments) < 20:
                messages.error(request, _("Комментарии должны содержать минимум 20 символов"))
                return render(
                    request,
                    "reviewers/submission_review.html",
                    {
                        "reviewer": reviewer,
                        "submission": submission,
                        "form_errors": _("Комментарии должны содержать минимум 20 символов"),
                        "stats": stats,
                        "reviews_today": stats.get("reviews_today", 0),
                        "max_reviews": reviewer.max_reviews_per_day,
                        "reviews_remaining": reviewer.max_reviews_per_day
                        - stats.get("reviews_today", 0),
                        "limit_reached": stats.get("reviews_today", 0)
                        >= reviewer.max_reviews_per_day,
                        "progress_percentage": (
                            int(
                                stats.get("reviews_today", 0) / reviewer.max_reviews_per_day * 100
                            )
                            if reviewer.max_reviews_per_day > 0
                            else 0
                        ),
                    },
                )

            # Маппинг статусов: changes_requested -> needs_work, approved -> approved
            status_mapping = {
                "changes_requested": "needs_work",
                "approved": "approved",
            }
            review_status = status_mapping.get(status, "needs_work")

            # Создаем или обновляем рецензию
            review, created = Review.objects.update_or_create(
                lesson_submission=submission,
                defaults={
                    "reviewer": reviewer,
                    "status": review_status,
                    "comments": comments,
                    "time_spent": 1,  # Минимальное время по умолчанию
                },
            )

            # Вычисляем реальное время проверки (от открытия страницы до отправки формы)
            review_start_time = request.POST.get("review_start_time")
            if review_start_time:
                try:
                    start_timestamp = int(review_start_time)
                    current_timestamp = int(timezone.now().timestamp())
                    time_spent_seconds = current_timestamp - start_timestamp
                    time_spent = max(1, int(time_spent_seconds / 60))  # минимум 1 минута
                    review.time_spent = time_spent
                except (ValueError, TypeError):
                    review.time_spent = 1

            review.reviewed_at = timezone.now()
            review.save()

            # Собираем улучшения если есть (поддерживаем оба формата: старый и новый)
            improvements = []

            for key, value in request.POST.items():
                if key.startswith("improvement_text_") and value.strip():
                    # Новый формат: improvement_text_1, improvement_text_2, etc
                    improvement_num = key.replace("improvement_text_", "")
                    title_key = f"improvement_title_{improvement_num}"
                    title = request.POST.get(title_key, "").strip()
                    improvements.append({"title": title, "text": value.strip()})
                elif (
                    key.startswith("improvement_")
                    and not key.startswith("improvement_text_")
                    and not key.startswith("improvement_title_")
                    and value.strip()
                ):
                    # Старый формат: improvement_1, improvement_2, etc (без названия)
                    improvements.append({"title": "", "text": value.strip()})

            # Создаем улучшения если статус changes_requested
            if status == "changes_requested" and improvements:
                # Получаем последний номер улучшения для продолжения нумерации
                # Теперь смотрим на все улучшения submission (не только текущего review)
                last_improvement = (
                    StudentImprovement.objects.filter(lesson_submission=submission)
                    .order_by("-improvement_number")
                    .first()
                )
                start_number = (last_improvement.improvement_number + 1) if last_improvement else 1

                # Добавляем новые улучшения (сохраняем историю всех улучшений)
                for idx, improvement_data in enumerate(improvements, start_number):
                    StudentImprovement.objects.create(
                        lesson_submission=submission,  # Связываем с submission
                        review=review,  # Также связываем с текущим review
                        improvement_number=idx,
                        title=improvement_data["title"],
                        improvement_text=improvement_data["text"],
                        priority="medium",
                    )

            # Обновляем статус работы и метаданные
            submission.status = status
            submission.reviewed_at = timezone.now()
            submission.mentor = reviewer.user.student if hasattr(reviewer.user, "student") else None
            submission.mentor_comment = comments
            submission.save(update_fields=["status", "reviewed_at", "mentor", "mentor_comment"])

            # Инвалидируем кэш ревьюера
            invalidate_reviewer_cache(reviewer.id)

            messages.success(request, _("Проверка успешно сохранена"))
            logger.info(
                f"Ревьюер {reviewer.user.email} проверил работу {submission_id} со статусом {status}"
            )

            return redirect("reviewers:submissions")

        except Exception as e:
            logger.error(f"Error saving review: {e}")
            messages.error(request, _("Ошибка при сохранении проверки"))
            return render(
                request,
                "reviewers/submission_review.html",
                {
                    "reviewer": reviewer,
                    "submission": submission,
                    "form_errors": str(e),
                    "stats": stats,
                    "reviews_today": stats.get("reviews_today", 0),
                    "max_reviews": reviewer.max_reviews_per_day,
                    "reviews_remaining": reviewer.max_reviews_per_day
                    - stats.get("reviews_today", 0),
                    "limit_reached": stats.get("reviews_today", 0) >= reviewer.max_reviews_per_day,
                    "progress_percentage": (
                        int(stats.get("reviews_today", 0) / reviewer.max_reviews_per_day * 100)
                        if reviewer.max_reviews_per_day > 0
                        else 0
                    ),
                },
            )

    return render(
        request,
        "reviewers/submission_review.html",
        {
            "reviewer": reviewer,
            "submission": submission,
            "now": timezone.now(),
            "stats": stats,
            "reviews_today": stats.get("reviews_today", 0),
            "max_reviews": reviewer.max_reviews_per_day,
            "reviews_remaining": reviewer.max_reviews_per_day - stats.get("reviews_today", 0),
            "limit_reached": stats.get("reviews_today", 0) >= reviewer.max_reviews_per_day,
            "progress_percentage": (
                int(stats.get("reviews_today", 0) / reviewer.max_reviews_per_day * 100)
                if reviewer.max_reviews_per_day > 0
                else 0
            ),
        },
    )


@login_required
@require_any_role(["reviewer", "mentor"], redirect_url="/")
def settings_view(request: HttpRequest) -> HttpResponse:
    """
    Настройки профиля ревьюера.

    Args:
        request: HTTP запрос

    Returns:
        HttpResponse: Форма настроек (GET) или редирект после сохранения (POST)
    """
    reviewer = get_object_or_404(Reviewer, user=request.user)
    stats = get_reviewer_stats(reviewer.id)

    if request.method == "POST":
        # Проверяем какая форма отправлена
        if "notifications_submit" in request.POST:
            # Обновляем настройки уведомлений ревьюера
            reviewer.notify_new_submissions = "reviewer_new_submissions" in request.POST
            reviewer.save()

            invalidate_reviewer_cache(reviewer.id)
            messages.success(request, _("Настройки уведомлений обновлены"))
            logger.info(f"Ревьюер {reviewer.user.email} обновил настройки уведомлений")
            return redirect("reviewers:settings")
        else:
            # Обновляем данные профиля
            request.user.first_name = request.POST.get("first_name", "")
            request.user.last_name = request.POST.get("last_name", "")

            # Обработка аватара если есть
            if "avatar" in request.FILES:
                if hasattr(request.user, "student"):
                    request.user.student.avatar = request.FILES["avatar"]
                    request.user.student.save()

            request.user.save()

            # Обновляем bio ревьюера
            reviewer.bio = request.POST.get("bio", "")
            reviewer.save()

            invalidate_reviewer_cache(reviewer.id)
            messages.success(request, _("Настройки успешно обновлены"))
            logger.info(f"Reviewer {reviewer.user.email} updated settings")
            return redirect("reviewers:settings")
    else:
        form = ReviewerProfileForm(instance=reviewer)

    return render(
        request,
        "reviewers/settings.html",
        {
            "reviewer": reviewer,
            "stats": stats,
            "form": form,
        },
    )


@login_required
@require_any_role(["reviewer", "mentor"], redirect_url="/")
def api_pending_count(request: HttpRequest) -> JsonResponse:
    """
    API endpoint для получения количества ожидающих работ.

    Args:
        request: HTTP запрос

    Returns:
        JsonResponse: JSON с количеством работ
    """
    try:
        reviewer = get_object_or_404(Reviewer, user=request.user)
        count = LessonSubmission.objects.filter(
            status="pending", lesson__course__in=reviewer.courses.all()
        ).count()

        return JsonResponse({"count": count})
    except Exception as e:
        logger.error(f"Error fetching pending count: {e}")
        return JsonResponse({"count": 0, "error": str(e)}, status=500)


@login_required
@require_any_role(["reviewer", "mentor"], redirect_url="/")
def history_view(request: HttpRequest) -> HttpResponse:
    """
    История проверок ревьюера.

    Args:
        request: HTTP запрос

    Returns:
        HttpResponse: Отрендеренная страница истории
    """
    reviewer = get_object_or_404(Reviewer, user=request.user)

    # Получаем историю проверок с prefetch улучшений
    reviews = (
        Review.objects.filter(reviewer=reviewer)
        .select_related("lesson_submission__student__user", "lesson_submission__lesson__course")
        .prefetch_related("improvements")
        .order_by("-reviewed_at")
    )

    # Пагинация
    paginator = Paginator(reviews, 20)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    # Добавляем расчет времени ожидания для каждой проверки
    now = timezone.now()
    for review in page_obj:
        # Время ожидания до проверки (для истории)
        # Используем reviewed_at как базу, т.к. submitted_at может обновляться при переотправках
        if review.reviewed_at:
            # Время с момента проверки (для отображения "X мин назад")
            time_since_review = now - review.reviewed_at
            review_minutes_ago = int(time_since_review.total_seconds() / 60)

            if review_minutes_ago < 60:
                review.time_ago_display = f"{review_minutes_ago} мин"
            elif review_minutes_ago < 1440:
                hours = review_minutes_ago // 60
                review.time_ago_display = f"{hours} ч"
            else:
                days = review_minutes_ago // 1440
                review.time_ago_display = f"{days} дн"

            # Время ожидания до проверки (от отправки до проверки)
            if review.lesson_submission.submitted_at:
                wait_delta = review.reviewed_at - review.lesson_submission.submitted_at
                wait_minutes = int(wait_delta.total_seconds() / 60)

                # Только если время положительное
                if wait_minutes > 0:
                    if wait_minutes < 60:
                        review.wait_time_display = f"{wait_minutes} мин"
                    elif wait_minutes < 1440:
                        hours = wait_minutes // 60
                        review.wait_time_display = f"{hours} ч"
                    else:
                        days = wait_minutes // 1440
                        review.wait_time_display = f"{days} дн"
                else:
                    review.wait_time_display = None
            else:
                review.wait_time_display = None
        else:
            review.time_ago_display = None
            review.wait_time_display = None

    logger.info(f"Reviewer {reviewer.user.email} accessed history")

    return render(
        request,
        "reviewers/history.html",
        {
            "reviewer": reviewer,
            "reviews": page_obj,
            "page_obj": page_obj,
        },
    )


@login_required
@require_any_role(["reviewer", "mentor"], redirect_url="/")
def statistics_view(request: HttpRequest) -> HttpResponse:
    """
    Статистика работы ревьюера.

    Args:
        request: HTTP запрос

    Returns:
        HttpResponse: Отрендеренная страница статистики
    """
    from datetime import timedelta

    from django.db.models import Avg
    from django.utils import timezone

    reviewer = get_object_or_404(Reviewer, user=request.user)
    stats = get_reviewer_stats(reviewer.id)

    # Дополнительная статистика для страницы статистики
    reviews = Review.objects.filter(reviewer=reviewer)

    # Процент одобрений
    total_reviews = reviews.count()
    approved_count = reviews.filter(status="approved").count()
    needs_work_count = reviews.filter(status="needs_work").count()

    # Ожидающие работы (не reviews, а submissions)
    pending_count = LessonSubmission.objects.filter(
        status="pending", lesson__course__in=reviewer.courses.all()
    ).count()

    approval_rate = (approved_count / total_reviews * 100) if total_reviews > 0 else 0

    # Среднее время проверки (в минутах)
    avg_time = reviews.filter(time_spent__isnull=False).aggregate(avg=Avg("time_spent"))["avg"] or 0

    # Проверки за последний месяц
    month_ago = timezone.now() - timedelta(days=30)
    month_reviews = reviews.filter(reviewed_at__gte=month_ago).count()

    # Проверки за сегодня
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    reviewed_today = reviews.filter(reviewed_at__gte=today_start).count()

    # Статистика по курсам
    course_stats = []
    for course in reviewer.courses.all()[:5]:  # Топ 5 курсов
        course_reviews = reviews.filter(lesson_submission__lesson__course=course).count()

        if total_reviews > 0:
            percentage = round((course_reviews / total_reviews * 100), 1)
        else:
            percentage = 0

        course_stats.append(
            {
                "course_name": course.name,
                "count": course_reviews,
                "percentage": percentage,
            }
        )

    # Активность по месяцам (последние 6 месяцев)
    import calendar
    from collections import defaultdict

    from django.db.models import Count
    from django.db.models.functions import TruncMonth

    # Получить данные за последние 6 месяцев
    six_months_ago = timezone.now() - timedelta(days=180)
    monthly_data = (
        reviews.filter(reviewed_at__gte=six_months_ago)
        .annotate(month=TruncMonth("reviewed_at"))
        .values("month", "status")
        .annotate(count=Count("id"))
        .order_by("month")
    )

    # Организовать данные по месяцам
    monthly_dict = defaultdict(lambda: {"approved": 0, "needs_work": 0})
    for item in monthly_data:
        month_key = item["month"].strftime("%Y-%m")
        monthly_dict[month_key][item["status"]] = item["count"]

    # Создать список последних 6 месяцев
    monthly_activity = []
    current_date = timezone.now()
    for i in range(5, -1, -1):  # От 5 до 0, чтобы идти от старого к новому
        target_date = current_date - timedelta(days=30 * i)
        month_key = target_date.strftime("%Y-%m")
        month_name = calendar.month_name[target_date.month][:3]  # Jan, Feb, etc

        data = monthly_dict.get(month_key, {"approved": 0, "needs_work": 0})

        # Ожидающие работы за этот месяц
        month_start = target_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
        pending_for_month = LessonSubmission.objects.filter(
            status="pending",
            lesson__course__in=reviewer.courses.all(),
            submitted_at__gte=month_start,
            submitted_at__lte=month_end,
        ).count()

        monthly_activity.append(
            {
                "month": month_name,
                "approved": data["approved"],
                "needs_work": data["needs_work"],
                "pending": pending_for_month,
                "total": data["approved"] + data["needs_work"] + pending_for_month,
            }
        )

    # Скорость проверки по последним 4 неделям
    from django.db.models.functions import TruncWeek

    # Последние 28 дней (4 недели)
    now = timezone.now()
    four_weeks_ago = now - timedelta(days=28)
    recent_reviews = reviews.filter(reviewed_at__gte=four_weeks_ago)

    weekly_data = (
        recent_reviews.annotate(week_start=TruncWeek("reviewed_at"))
        .values("week_start")
        .annotate(count=Count("id"), avg_time=Avg("time_spent"))
        .order_by("week_start")
    )

    weekly_speed = []
    for item in weekly_data:
        week_start = item["week_start"]
        week_end = week_start + timedelta(days=6)

        # Форматируем диапазон недели
        if week_start.month == week_end.month:
            week_label = f"{week_start.day}-{week_end.day} {['янв', 'фев', 'мар', 'апр', 'май', 'июн', 'июл', 'авг', 'сен', 'окт', 'ноя', 'дек'][week_start.month-1]}"
        else:
            week_label = f"{week_start.day} {['янв', 'фев', 'мар', 'апр', 'май', 'июн', 'июл', 'авг', 'сен', 'окт', 'ноя', 'дек'][week_start.month-1]} - {week_end.day} {['янв', 'фев', 'мар', 'апр', 'май', 'июн', 'июл', 'авг', 'сен', 'окт', 'ноя', 'дек'][week_end.month-1]}"

        weekly_speed.append(
            {
                "week": week_label,
                "count": item["count"],
                "avg_time": round(float(item["avg_time"]) if item["avg_time"] else 0, 1),
            }
        )

    # Обновляем stats
    stats.update(
        {
            "approval_rate": round(approval_rate, 1),
            "avg_time": round(float(avg_time), 0) if avg_time else 0,
            "month_reviews": month_reviews,
            "reviewed_today": reviewed_today,
            "approved_count": approved_count,
            "needs_work_count": needs_work_count,
            "pending_count": pending_count,
        }
    )

    logger.info(f"Ревьюер {reviewer.user.email} открыл статистику")

    return render(
        request,
        "reviewers/statistics.html",
        {
            "reviewer": reviewer,
            "stats": stats,
            "course_stats": course_stats,
            "monthly_activity": monthly_activity,
            "weekly_speed": weekly_speed,
        },
    )


@login_required
@require_any_role(["reviewer", "mentor"], redirect_url="/")
def submission_detail_view(request: HttpRequest, submission_id: UUID) -> HttpResponse:
    """
    Детальная информация о работе студента.

    Args:
        request: HTTP запрос
        submission_id: UUID работы

    Returns:
        HttpResponse: Отрендеренная страница деталей работы
    """
    reviewer = get_object_or_404(Reviewer, user=request.user)
    submission = get_object_or_404(
        LessonSubmission.objects.select_related(
            "student",
            "lesson",
            "lesson__course",
            "review",
            "review__reviewer",
            "review__reviewer__user",
        ).prefetch_related("review__improvements"),
        id=submission_id,
        lesson__course__in=reviewer.courses.all(),
    )

    # Статистика студента
    student_submissions = LessonSubmission.objects.filter(student=submission.student)
    student_stats = {
        "total_submissions": student_submissions.count(),
        "accepted": student_submissions.filter(status="approved").count(),
        "changes_requested": student_submissions.filter(status="changes_requested").count(),
        "pending": student_submissions.filter(status="pending").count(),
    }

    # Предыдущие попытки этого урока
    previous_submissions = (
        LessonSubmission.objects.filter(student=submission.student, lesson=submission.lesson)
        .exclude(id=submission_id)
        .order_by("-submitted_at")[:5]
    )

    logger.info(f"Ревьюер {reviewer.user.email} просматривает детали работы {submission_id}")

    return render(
        request,
        "reviewers/submission_detail.html",
        {
            "reviewer": reviewer,
            "submission": submission,
            "student_stats": student_stats,
            "previous_submissions": previous_submissions,
        },
    )
