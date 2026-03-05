"""
Students Views Module - Django views для личного кабинета студента и курсов.

Этот модуль содержит представления для работы студентов с обучением:

Личный кабинет:
    - account_dashboard_view: Главная страница с прогрессом обучения
    - account_settings_view: Настройки профиля (GET/POST)
    - export_user_data: Экспорт данных пользователя (JSON)
    - delete_account: Удаление аккаунта пользователя

Курсы и уроки:
    - account_courses_view: Список курсов с прогрессом
    - account_course_detail_view: Детали курса с модулями и уроками
    - account_lesson_detail_view: Урок с шагами и прогрессом (GET/POST)
    - account_lesson_submit_view: AJAX отправка работы на проверку
    - toggle_step_progress: AJAX переключение статуса шага

Используется кэширование через cache_utils для оптимизации производительности.
Все представления требующие аутентификации декорированы @login_required.

Автор: Pyland Team
Дата: 2025
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from authentication.models import Student
from blog.models import Bookmark
from courses.constants import MINUTES_PER_STEP
from courses.models import Course, Lesson, Step
from reviewers.models import LessonSubmission, StepProgress

from .cache_utils import safe_cache_delete, safe_cache_get, safe_cache_set
from .forms import LessonSubmissionForm

User = get_user_model()
logger = logging.getLogger(__name__)


@login_required
def dashboard_view(request: HttpRequest, user_uuid: uuid.UUID) -> HttpResponse:
    """
    Улучшенный дашборд студента с детальной аналитикой прогресса обучения.

    Отображает полную статистику обучения студента включая:
    - Детальный прогресс по каждому курсу и уроку
    - Бейджи достижений (первые шаги, настойчивость, мастер Python)
    - Персонализированные рекомендации для продолжения обучения
    - График активности за последние 7 дней
    - Статус отправленных работ (pending, changes_requested, approved)
    - Избранные статьи из блога

    Args:
        request: HTTP запрос от студента
        user_uuid: UUID профиля студента для просмотра

    Returns:
        HttpResponse: Отрендеренная страница students/dashboard/dashboard.html

    Template Context:
        profile: Student - профиль студента
        courses: QuerySet[Course] - все курсы студента
        course_stats: List[dict] - топ-4 активных курса для карточек
        all_course_stats: List[dict] - полный список курсов, отсортированный по активности
        is_public: bool - просмотр чужого профиля (True) или своего (False)
        overall_stats: dict - общая статистика (курсы, шаги, процент завершения)
        recent_progress: QuerySet[StepProgress] - последние 10 завершенных шагов за 7 дней
        daily_activity: List[dict] - активность по дням (date, completed_steps)
        achievements: List[dict] - разблокированные бейджи достижений
        recommendations: List[dict] - персонализированные рекомендации (до 5)
        submissions_by_status: dict - работы сгруппированные по статусу
        submissions_count: dict - количество работ по статусам
        bookmarked_articles: QuerySet[Bookmark] - избранные статьи (до 10)
        dashboard_data_json: dict - данные для JS (графики и прогресс-бары)

    Cache Strategy:
        - dashboard_stats: кэш на 5 минут
        - Инвалидируется при обновлении прогресса через StepProgress
        - Ключ кэша: f"dashboard_stats_{profile.id}"

    Achievements Logic:
        - "Первые шаги": ≥ 1 завершенного шага
        - "Настойчивость": ≥ 10 завершенных шагов
        - "Мастер Python": ≥ 50 завершенных шагов
        - "Завершение курса": ≥ 1 полностью завершенного курса

    Example:
        GET /account/dashboard/{uuid}/
        → Показывает полный дашборд с аналитикой и рекомендациями
    """
    profile = get_object_or_404(Student, id=user_uuid)
    is_public = profile.user != request.user

    courses = profile.courses.all()

    dashboard_cache_key = f"dashboard_stats_{profile.id}"
    cached_dashboard = safe_cache_get(dashboard_cache_key)

    if cached_dashboard:
        course_stats = cached_dashboard["course_stats"]
        total_steps_completed = cached_dashboard["total_steps_completed"]
        total_steps_available = cached_dashboard["total_steps_available"]
    else:
        course_stats = []
        total_steps_completed = 0
        total_steps_available = 0

        courses_with_prefetch = courses.prefetch_related(
            "lessons__steps", "lessons__steps__progress"
        )

        for course in courses_with_prefetch:
            course_progress = course.get_progress_for_profile(profile)

            lesson_stats = []
            for lesson in course.lessons.all():
                lesson_progress = lesson.get_progress_for_profile(profile)

                last_activity = (
                    StepProgress.objects.filter(
                        profile=profile, step__lesson=lesson, is_completed=True
                    )
                    .order_by("-completed_at")
                    .first()
                )

                lesson_stats.append(
                    {
                        "lesson": lesson,
                        "total_steps": lesson_progress["total_steps"],
                        "completed_steps": lesson_progress["completed_steps"],
                        "completion_percentage": lesson_progress["completion_percentage"],
                        "is_completed": lesson_progress["is_completed"],
                        "last_activity": last_activity,
                    }
                )

            course_stats.append(
                {
                    "course": course,
                    "lessons": lesson_stats,
                    "total_lessons": course_progress["total_lessons"],
                    "completed_lessons": course_progress["completed_lessons"],
                    "total_steps": course_progress["total_steps"],
                    "completed_steps": course_progress["completed_steps"],
                    "completion_percentage": course_progress["completion_percentage"],
                    "is_completed": course_progress["completion_percentage"] == 100,
                }
            )

            total_steps_completed += course_progress["completed_steps"]
            total_steps_available += course_progress["total_steps"]

        dashboard_cache_data = {
            "course_stats": course_stats,
            "total_steps_completed": total_steps_completed,
            "total_steps_available": total_steps_available,
        }
        safe_cache_set(dashboard_cache_key, dashboard_cache_data, 60 * 5)

    overall_completion = (
        (total_steps_completed / total_steps_available * 100) if total_steps_available > 0 else 0
    )

    seven_days_ago = timezone.now() - timedelta(days=7)
    recent_progress = StepProgress.objects.filter(
        profile=profile, completed_at__gte=seven_days_ago, is_completed=True
    ).order_by("-completed_at")[:10]

    daily_activity = []
    for i in range(7):
        day = timezone.now() - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)

        completed_today = StepProgress.objects.filter(
            profile=profile,
            completed_at__gte=day_start,
            completed_at__lt=day_end,
            is_completed=True,
        ).count()

        daily_activity.append({"date": day_start.isoformat(), "completed_steps": completed_today})

    daily_activity.reverse()

    achievements = []

    if total_steps_completed >= 1:
        achievements.append(
            {
                "title": "Первые шаги",
                "description": "Завершили первый шаг в обучении",
                "icon": "fas fa-baby",
                "color": "success",
            }
        )

    if total_steps_completed >= 10:
        achievements.append(
            {
                "title": "Настойчивость",
                "description": "Завершили 10 шагов",
                "icon": "fas fa-medal",
                "color": "primary",
            }
        )

    if total_steps_completed >= 50:
        achievements.append(
            {
                "title": "Мастер Python",
                "description": "Завершили 50 шагов",
                "icon": "fas fa-crown",
                "color": "warning",
            }
        )

    completed_courses = len([course for course in course_stats if course["is_completed"]])
    if completed_courses >= 1:
        achievements.append(
            {
                "title": "Завершение курса",
                "description": f"Завершили {completed_courses} курс(ов)",
                "icon": "fas fa-trophy",
                "color": "danger",
            }
        )

    recommendations = []

    for course_stat in course_stats:
        for lesson_stat in course_stat["lessons"]:
            if not lesson_stat["is_completed"] and lesson_stat["completion_percentage"] > 0:
                recommendations.append(
                    {
                        "type": "continue",
                        "title": f'Продолжить "{lesson_stat["lesson"].name}"',
                        "description": f"Прогресс: {lesson_stat['completion_percentage']}%",
                        "url": f"/account/courses/{course_stat['course'].slug}/lessons/{lesson_stat['lesson'].slug}/",
                        "priority": "high",
                    }
                )

    for course_stat in course_stats:
        for lesson_stat in course_stat["lessons"]:
            if lesson_stat["completion_percentage"] == 0 and len(recommendations) < 3:
                recommendations.append(
                    {
                        "type": "start",
                        "title": f'Начать "{lesson_stat["lesson"].name}"',
                        "description": f"Курс: {course_stat['course'].name}",
                        "url": f"/account/courses/{course_stat['course'].slug}/lessons/{lesson_stat['lesson'].slug}/",
                        "priority": "medium",
                    }
                )
                break

    courses_activity = []
    for course in courses:
        last_activity = (
            StepProgress.objects.filter(
                profile=profile, step__lesson__course=course, is_completed=True
            )
            .order_by("-completed_at")
            .first()
        )

        if last_activity:
            course_stat = next((cs for cs in course_stats if cs["course"].id == course.id), None)
            if course_stat:
                courses_activity.append(
                    {
                        "name": course.name,
                        "completion_percentage": course_stat["completion_percentage"],
                        "last_activity": last_activity.completed_at,
                        "course_stat": course_stat,
                    }
                )
                logger.info(
                    f"Course activity: {course.name}, last_activity: {last_activity.completed_at}"
                )

    courses_activity.sort(key=lambda x: x["last_activity"], reverse=True)

    top_4_courses = courses_activity[:4]

    course_labels = [c["name"] for c in top_4_courses]
    course_progress_data = [c["completion_percentage"] for c in top_4_courses]
    top_4_course_stats = [c["course_stat"] for c in top_4_courses]

    all_courses_sorted = []
    for course_stat in course_stats:
        last_activity = (
            StepProgress.objects.filter(
                profile=profile, step__lesson__course=course_stat["course"], is_completed=True
            )
            .order_by("-completed_at")
            .first()
        )

        all_courses_sorted.append(
            {
                "course_stat": course_stat,
                "last_activity": last_activity.completed_at if last_activity else None,
                "completion_percentage": course_stat["completion_percentage"],
            }
        )

    all_courses_sorted.sort(
        key=lambda x: (
            x["last_activity"] is None,
            -(x["last_activity"].timestamp() if x["last_activity"] else 0),
            -x["completion_percentage"],
        )
    )

    all_course_stats_sorted = [c["course_stat"] for c in all_courses_sorted]

    weekly_labels = [day["date"] for day in daily_activity]
    weekly_data = [day["completed_steps"] for day in daily_activity]

    recommendations = recommendations[:5]

    submissions = (
        LessonSubmission.objects.filter(student=profile)
        .select_related("lesson", "lesson__course", "mentor", "mentor__user")
        .order_by("-submitted_at")
    )

    submissions_by_status = {
        "pending": submissions.filter(status="pending"),
        "changes_requested": submissions.filter(status="changes_requested"),
        "approved": submissions.filter(status="approved"),
    }

    submissions_count = {
        "total": submissions.count(),
        "pending": submissions_by_status["pending"].count(),
        "changes_requested": submissions_by_status["changes_requested"].count(),
        "approved": submissions_by_status["approved"].count(),
    }

    bookmarked_articles = (
        Bookmark.objects.filter(user=profile.user)
        .select_related("article", "article__author")
        .order_by("-created_at")[:10]
    )

    context = {
        "profile": profile,
        "courses": courses,
        "course_stats": top_4_course_stats,  # Передаем топ-4 активных курса для карточек
        "all_course_stats": all_course_stats_sorted,  # Полный список, отсортированный по активности и проценту
        "is_public": is_public,
        "overall_stats": {
            "total_courses": courses.count(),
            "completed_courses": completed_courses,
            "total_steps": total_steps_available,
            "completed_steps": total_steps_completed,
            "completion_percentage": round(overall_completion, 1),
        },
        "recent_progress": recent_progress,
        "daily_activity": daily_activity,
        "weekly_labels": weekly_labels,
        "weekly_data": weekly_data,
        "course_labels": course_labels,
        "course_progress_data": course_progress_data,
        "achievements": achievements,
        "recommendations": recommendations,
        "submissions_by_status": submissions_by_status,
        "submissions_count": submissions_count,
        "bookmarked_articles": bookmarked_articles,
        "dashboard_data_json": {
            "profile": {"id": str(profile.id), "email": profile.user.email},
            "stats": {
                "total_courses": courses.count(),
                "completed_steps": total_steps_completed,
                "completion_percentage": round(overall_completion, 1),
                "submissions_total": submissions.count(),
                "submissions_pending": submissions_by_status["pending"].count(),
                "submissions_changes_requested": submissions_by_status["changes_requested"].count(),
                "submissions_approved": submissions_by_status["approved"].count(),
            },
            "dailyActivity": [
                {"date": day["date"], "completed_steps": day["completed_steps"]}
                for day in daily_activity
            ],
            "courseProgress": [
                {
                    "name": c["course"].name,
                    "progress": c["completion_percentage"],
                    "color": ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899"][
                        idx % 6
                    ],
                }
                for idx, c in enumerate(top_4_course_stats)
            ],
        },
    }

    return render(request, "students/dashboard/dashboard.html", context)


@login_required
def settings_view(request: HttpRequest, user_uuid: uuid.UUID) -> HttpResponse:
    """
    Отображает страницу настроек профиля студента.

    Поддерживает 4 типа настроек:
    1. Profile Settings (profile_submit): личные данные, аватар, телефон
    2. Notification Settings (notification_submit): настройки уведомлений
    3. Privacy Settings (privacy_submit): видимость профиля, прогресса
    4. Password Change (password_submit): смена пароля

    Args:
        request: HTTP запрос (студент GET или POST с изменениями)
        user_uuid: UUID профиля студента

    Returns:
        HttpResponse: Отрендеренная страница students/dashboard/settings.html

    POST Handlers:
        - profile_submit: Обновляет first_name, last_name, email, bio, phone, birthday, gender,
                         country, city, address, avatar
        - notification_submit: Обновляет email_notifications, course_updates, lesson_reminders,
                              achievement_alerts, weekly_summary, marketing_emails
        - privacy_submit: Обновляет profile_visibility, show_progress, show_achievements,
                         allow_messages
        - password_submit: Изменяет пароль с проверкой текущего

    Validation:
        - Email: проверка уникальности
        - Phone: валидация через phonenumbers.parse() и is_valid_number()
        - Password: проверка текущего и совпадение новых

    Template Context:
        profile: Student - профиль студента
        user: User - объект пользователя

    Example:
        POST /account/settings/{uuid}/ (profile_submit)
        {"first_name": "Ivan", "last_name": "Petrov", "phone": "+79991234567"}
        → Обновляет профиль, redirect на settings с success message
    """
    profile = get_object_or_404(Student, id=user_uuid)

    if request.method == "POST":
        if "profile_submit" in request.POST:
            first_name = request.POST.get("first_name", "").strip()
            last_name = request.POST.get("last_name", "").strip()
            email = request.POST.get("email", "").strip()
            bio = request.POST.get("bio")
            phone = request.POST.get("phone")
            birthday = request.POST.get("birthday")
            gender = request.POST.get("gender")
            country = request.POST.get("country")
            city = request.POST.get("city")
            address = request.POST.get("address")
            avatar = request.FILES.get("avatar")

            if first_name:
                request.user.first_name = first_name
            if last_name:
                request.user.last_name = last_name
            if email and email != request.user.email:
                if not User.objects.filter(email=email).exclude(pk=request.user.pk).exists():
                    request.user.email = email
                else:
                    messages.error(request, _("Этот email уже используется"))
                    return redirect("students:settings", user_uuid=profile.id)
            request.user.save()

            profile.bio = bio
            if phone:
                try:
                    from phonenumbers import is_valid_number, parse

                    # Парсим и валидируем номер телефона
                    parsed_phone = parse(phone, None)
                    if not is_valid_number(parsed_phone):
                        messages.error(
                            request,
                            _(
                                "Неверный формат номера телефона. Пожалуйста, введите корректный номер."
                            ),
                        )
                        return redirect("students:settings", user_uuid=profile.id)
                    profile.phone = phone
                except Exception:
                    messages.error(
                        request,
                        _(
                            "Неверный формат номера телефона. Используйте международный формат, например: +79991234567"
                        ),
                    )
                    return redirect("students:settings", user_uuid=profile.id)
            if birthday:
                profile.birthday = birthday
            if gender:
                profile.gender = gender
            if country:
                profile.country = country
            if city:
                profile.city = city
            if address:
                profile.address = address
            if avatar:
                profile.avatar = avatar

            profile.save()
            messages.success(request, _(" Профиль успешно обновлен"))

        elif "notification_submit" in request.POST:
            profile.email_notifications = request.POST.get("email_notifications") == "on"
            profile.course_updates = request.POST.get("course_updates") == "on"
            profile.lesson_reminders = request.POST.get("lesson_reminders") == "on"
            profile.achievement_alerts = request.POST.get("achievement_alerts") == "on"
            profile.weekly_summary = request.POST.get("weekly_summary") == "on"
            profile.marketing_emails = request.POST.get("marketing_emails") == "on"
            profile.save()
            messages.success(request, _("Настройки уведомлений обновлены"))

        elif "privacy_submit" in request.POST:
            profile.profile_visibility = request.POST.get("profile_visibility", "students")
            profile.show_progress = request.POST.get("show_progress") == "on"
            profile.show_achievements = request.POST.get("show_achievements") == "on"
            profile.allow_messages = request.POST.get("allow_messages") == "on"
            profile.save()
            messages.success(request, _("Настройки приватности обновлены"))

        elif "password_submit" in request.POST:
            current_password = request.POST.get("current_password")
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")

            if current_password and new_password and confirm_password:
                if request.user.check_password(current_password):
                    if new_password == confirm_password:
                        request.user.set_password(new_password)
                        request.user.save()
                        messages.success(request, _("Пароль успешно изменен"))
                        login(request, request.user)
                    else:
                        messages.error(request, _("Новые пароли не совпадают"))
                else:
                    messages.error(request, _("Текущий пароль неверен"))

        return redirect("students:settings", user_uuid=profile.id)

    context = {
        "profile": profile,
        "user": request.user,
    }

    return render(request, "students/dashboard/settings.html", context)


@login_required
@require_http_methods(["POST"])
def delete_avatar_view(request: HttpRequest) -> JsonResponse:
    """
    AJAX endpoint для удаления аватара студента.

    Удаляет файл аватара из хранилища и очищает поле avatar в профиле.

    Args:
        request: HTTP POST запрос от аутентифицированного студента

    Returns:
        JsonResponse:
            - Success: {"success": true, "message": "Аватар успешно удален"}
            - Not Found: {"success": false, "message": "Аватар не найден"}, status=404
            - Error: {"success": false, "message": "Ошибка..."}, status=500

    Example:
        POST /account/delete-avatar/ (AJAX)
        → {"success": true, "message": "Аватар успешно удален"}
    """
    try:
        profile = request.user.student
        if profile.avatar:
            profile.avatar.delete(save=True)
            return JsonResponse({"success": True, "message": _("Аватар успешно удален")})
        else:
            return JsonResponse({"success": False, "message": _("Аватар не найден")}, status=404)
    except Exception as e:
        logger.error(f"Ошибка при удалении аватара: {e}")
        return JsonResponse(
            {"success": False, "message": _("Ошибка при удалении аватара")}, status=500
        )


@login_required
def export_user_data(request: HttpRequest) -> HttpResponse:
    """
    Экспортирует все данные пользователя в JSON формате (GDPR compliance).

    Включает:
    - Личную информацию (email, имя, дата регистрации)
    - Данные профиля (телефон, дата рождения, страна, город, bio)
    - Настройки уведомлений и приватности
    - Список курсов и прогресс по шагам

    Args:
        request: HTTP GET запрос от аутентифицированного пользователя

    Returns:
        HttpResponse: JSON файл с Content-Disposition для скачивания
            Filename: pyland_data_{email}_{YYYYMMDD_HHMMSS}.json

    Data Structure:
        {
            "export_date": ISO datetime,
            "user_info": {...},
            "profile": {...},
            "notification_settings": {...},
            "privacy_settings": {...},
            "roles": [...],
            "courses": [{"name", "slug", "description", "enrolled_date"}, ...],
            "progress": [{"course", "lesson", "step", "is_completed", "completed_at"}, ...]
        }

    Example:
        GET /account/export-data/
        → Скачивает pyland_data_user@email.com_20250204_153045.json
    """
    from datetime import datetime

    profile = get_object_or_404(Student, user=request.user)

    user_data = {
        "export_date": datetime.now().isoformat(),
        "user_info": {
            "email": request.user.email,
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "username": (
                request.user.username if hasattr(request.user, "username") else request.user.email
            ),
            "is_active": request.user.is_active,
            "email_verified": request.user.email_is_verified,
            "date_joined": (
                request.user.date_joined.isoformat()
                if hasattr(request.user, "date_joined")
                else None
            ),
        },
        "profile": {
            "phone": str(profile.phone) if profile.phone else None,
            "birthday": profile.birthday.isoformat() if profile.birthday else None,
            "gender": profile.gender,
            "country": str(profile.country) if profile.country else None,
            "city": profile.city,
            "address": profile.address,
            "bio": profile.bio,
            "created_at": profile.created_at.isoformat(),
            "updated_at": profile.updated_at.isoformat(),
        },
        "notification_settings": {
            "email_notifications": profile.email_notifications,
            "course_updates": profile.course_updates,
            "lesson_reminders": profile.lesson_reminders,
            "achievement_alerts": profile.achievement_alerts,
            "weekly_summary": profile.weekly_summary,
            "marketing_emails": profile.marketing_emails,
        },
        "privacy_settings": {
            "profile_visibility": profile.profile_visibility,
            "show_progress": profile.show_progress,
            "show_achievements": profile.show_achievements,
            "allow_messages": profile.allow_messages,
        },
        "roles": [profile.role.name] if profile.role else [],
        "courses": [],
        "progress": [],
    }

    for course in profile.courses.all():
        course_data = {
            "name": course.name,
            "slug": course.slug,
            "description": course.description,
            "enrolled_date": None,  # Можно добавить если есть поле
        }
        user_data["courses"].append(course_data)

    try:
        progress_records = StepProgress.objects.filter(profile=profile).select_related(
            "step", "step__lesson", "step__lesson__course"
        )
        for progress in progress_records:
            progress_data = {
                "course": progress.step.lesson.course.name,
                "lesson": progress.step.lesson.title,
                "step": progress.step.title,
                "is_completed": progress.is_completed,
                "completed_at": (
                    progress.completed_at.isoformat() if progress.completed_at else None
                ),
                "started_at": progress.started_at.isoformat() if progress.started_at else None,
            }
            user_data["progress"].append(progress_data)
    except (ImportError, AttributeError):
        pass

    response = HttpResponse(
        json.dumps(user_data, ensure_ascii=False, indent=2),
        content_type="application/json; charset=utf-8",
    )
    response["Content-Disposition"] = (
        f'attachment; filename="pyland_data_{request.user.email}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"'
    )

    messages.success(request, _("Данные успешно экспортированы"))
    return response


@login_required
def delete_account(request: HttpRequest) -> HttpResponse:
    """
    Удаляет аккаунт пользователя после двойного подтверждения.

    Требует два подтверждения:
    1. Ввод строки "УДАЛИТЬ" (точное совпадение)
    2. Ввод текущего пароля

    При успешном удалении каскадно удаляются:
    - User объект
    - Student профиль (on_delete=CASCADE)
    - Все связанные данные (прогресс, работы, комментарии)

    Args:
        request: HTTP POST запрос с confirmation и password полями

    Returns:
        HttpResponse:
            - POST успешно: Redirect на core:home с success message
            - POST ошибка: Redirect на students:settings с error message
            - GET: Redirect на students:settings

    Security:
        - Требуется аутентификация (@login_required)
        - Проверка текущего пароля через user.check_password()
        - Выход из системы перед удалением (logout)

    Example:
        POST /account/delete/
        {"confirmation": "УДАЛИТЬ", "password": "current_password"}
        → Удаляет аккаунт, logout, redirect на home
    """
    if request.method == "POST":
        confirmation = request.POST.get("confirmation", "").strip()
        password = request.POST.get("password", "")

        if confirmation != "УДАЛИТЬ":
            messages.error(
                request, _("Неверное подтверждение. Введите 'УДАЛИТЬ' для подтверждения.")
            )
            return redirect("students:settings", user_uuid=request.user.student.id)

        if not request.user.check_password(password):
            messages.error(request, _("Неверный пароль. Удаление отменено."))
            return redirect("students:settings", user_uuid=request.user.student.id)

        user_email = request.user.email

        try:
            user = request.user
            logout(request)
            user.delete()

            messages.success(
                request, _(f"Аккаунт {user_email} был успешно удален. Мы сожалеем, что вы уходите.")
            )
            return redirect("core:home")
        except Exception as e:
            messages.error(request, _(f"Ошибка при удалении аккаунта: {str(e)}"))
            return redirect("students:settings", user_uuid=request.user.student.id)

    return redirect("students:settings", user_uuid=request.user.student.id)


@login_required
def courses_view(request: HttpRequest, user_uuid: uuid.UUID) -> HttpResponse:
    """
    Отображает страницу со списком всех курсов студента с детальной статистикой.

    Показывает прогресс по каждому курсу, статистику завершенных уроков и шагов,
    дату последней активности. Использует агрессивное кэширование (10 минут)
    для оптимизации производительности.

    Args:
        request: HTTP запрос от аутентифицированного студента
        user_uuid: UUID профиля студента (игнорируется, используется request.user)

    Returns:
        HttpResponse: Отрендеренная страница students/dashboard/course-list.html

    Template Context:
        profile: Student - профиль студента
        courses: List[dict] - список курсов с детальной статистикой
        overall_progress: float - общий процент завершения всех курсов
        total_courses: int - количество курсов студента
        total_completed_steps: int - всего завершенных шагов
        total_steps: int - всего шагов в курсах
        completed_courses_count: int - количество завершенных курсов (100%)
        in_progress_courses_count: int - количество курсов в процессе (0-100%)
        not_started_courses_count: int - количество не начатых курсов (0%)
        total_study_time: int - общее время обучения (пока 0)
        average_score: float - средний балл (пока 0)

    Cache Strategy:
        - Ключ: f"user_courses_stats_{profile.id}"
        - TTL: 10 минут
        - Инвалидируется при обновлении прогресса

    Course Stats Structure:
        {
            "course": Course объект,
            "completion_percentage": float,
            "completed_steps": int,
            "total_steps": int,
            "completed_lessons": int,
            "total_lessons": int,
            "last_activity": datetime или None
        }

    Example:
        GET /account/courses/{uuid}/
        → Показывает список всех курсов с прогресс-барами и статистикой
    """
    profile = get_object_or_404(Student, user=request.user)

    cache_key = f"user_courses_stats_{profile.id}"
    cached_data = safe_cache_get(cache_key)

    if cached_data:
        courses_with_stats = cached_data["courses_with_stats"]
        overall_completed_steps = cached_data["overall_completed_steps"]
        overall_total_steps = cached_data["overall_total_steps"]
    else:
        courses = profile.courses.prefetch_related(
            "lessons__steps", "lessons__steps__progress"
        ).all()

        courses_with_stats = []
        overall_completed_steps = 0
        overall_total_steps = 0

        for course in courses:
            progress_data = course.get_progress_for_profile(profile)

            courses_with_stats.append(
                {
                    "course": course,
                    "completion_percentage": progress_data["completion_percentage"],
                    "completed_steps": progress_data["completed_steps"],
                    "total_steps": progress_data["total_steps"],
                    "completed_lessons": progress_data["completed_lessons"],
                    "total_lessons": progress_data["total_lessons"],
                    "last_activity": progress_data["last_activity"],
                }
            )

            overall_completed_steps += progress_data["completed_steps"]
            overall_total_steps += progress_data["total_steps"]

        cache_data = {
            "courses_with_stats": courses_with_stats,
            "overall_completed_steps": overall_completed_steps,
            "overall_total_steps": overall_total_steps,
        }
        safe_cache_set(cache_key, cache_data, 60 * 10)

    overall_progress = (
        (overall_completed_steps / overall_total_steps * 100) if overall_total_steps > 0 else 0
    )

    context = {
        "profile": profile,
        "courses": courses_with_stats,
        "overall_progress": round(overall_progress, 1),
        "total_courses": len(courses_with_stats),
        "total_courses_count": len(courses_with_stats),
        "total_completed_steps": overall_completed_steps,
        "total_steps": overall_total_steps,
        "completed_courses_count": len(
            [c for c in courses_with_stats if c["completion_percentage"] == 100]
        ),
        "in_progress_courses_count": len(
            [c for c in courses_with_stats if 0 < c["completion_percentage"] < 100]
        ),
        "not_started_courses_count": len(
            [c for c in courses_with_stats if c["completion_percentage"] == 0]
        ),
        "total_study_time": 0,
        "average_score": 0,
    }

    return render(
        request,
        "students/dashboard/course-list.html",
        context,
    )


@login_required
def course_detail_view(
    request: HttpRequest, user_uuid: uuid.UUID, course_slug: str
) -> HttpResponse:
    """
    Отображает детальную страницу курса для текущего пользователя.

    Показывает описание курса, изображение и список уроков, если курс связан с аккаунтом пользователя.
    """
    profile = get_object_or_404(Student, user=request.user)

    try:
        course = profile.courses.get(slug=course_slug)
    except Course.DoesNotExist:
        course = get_object_or_404(Course, slug=course_slug)
        profile.courses.add(course)
        logger.info(f"Student {profile.user.email} auto-enrolled to course {course.name}")

    course_progress = course.get_progress_for_profile(profile)

    lesson_stats = []
    previous_lesson_approved = True  # Первый урок всегда разблокирован

    for lesson in course.lessons.all():
        lprog = lesson.get_progress_for_profile(profile)

        all_steps = []
        incomplete_steps = []
        for step in lesson.steps.all():
            sp = StepProgress.objects.filter(profile=profile, step=step).first()
            step_data = {
                "step": step,
                "is_completed": bool(sp.is_completed) if sp else False,
            }
            all_steps.append(step_data)
            if not step_data["is_completed"]:
                incomplete_steps.append(step_data)

        if incomplete_steps:
            steps_preview = incomplete_steps[:3]
        else:
            steps_preview = all_steps[-3:] if len(all_steps) > 3 else all_steps

        total_steps_count = len(all_steps)

        last_activity = (
            StepProgress.objects.filter(profile=profile, step__lesson=lesson, is_completed=True)
            .order_by("-completed_at")
            .first()
        )

        submission = (
            LessonSubmission.objects.filter(student=profile, lesson=lesson)
            .select_related("mentor", "mentor__user")
            .first()
        )

        is_locked = not previous_lesson_approved

        lesson_stats.append(
            {
                "lesson": lesson,
                "total_steps": lprog["total_steps"],
                "completed_steps": lprog["completed_steps"],
                "completion_percentage": lprog["completion_percentage"],
                "is_completed": lprog["is_completed"],
                "steps": steps_preview,
                "total_steps_count": total_steps_count,
                "remaining_steps_count": total_steps_count - len(steps_preview),
                "last_activity": last_activity,
                "submission": submission,
                "is_locked": is_locked,
            }
        )

        if submission and submission.status == "approved":
            previous_lesson_approved = True
        else:
            previous_lesson_approved = False

    total_steps_all = sum(ls["total_steps_count"] for ls in lesson_stats)
    estimated_time = round(total_steps_all * MINUTES_PER_STEP / 60, 1)
    average_score = 0

    return render(
        request,
        "students/dashboard/course-detail.html",
        {
            "course": course,
            "lesson_stats": lesson_stats,
            "course_progress": course_progress,
            "estimated_time": estimated_time,
            "average_score": average_score,
        },
    )


@login_required
def lesson_detail_view(
    request: HttpRequest, user_uuid: uuid.UUID, course_slug: str, lesson_slug: str
) -> HttpResponse:
    """
    Просмотр информации об уроке.
    """
    profile = get_object_or_404(Student, user=request.user)
    course = get_object_or_404(Course, slug=course_slug)
    lesson = get_object_or_404(Lesson, slug=lesson_slug, course=course)

    if course not in profile.courses.all():
        profile.courses.add(course)
        logger.info(f"Student {profile.user.email} auto-enrolled to course {course.name}")

    if lesson.lesson_number > 1:
        prev_lesson = (
            lesson.course.lessons.filter(lesson_number__lt=lesson.lesson_number)
            .order_by("-lesson_number")
            .first()
        )
        if prev_lesson:
            prev_submission = LessonSubmission.objects.filter(
                student=profile, lesson=prev_lesson
            ).first()
            if not prev_submission or prev_submission.status != "approved":
                from django.contrib import messages

                messages.warning(
                    request,
                    f"🔒 Урок '{lesson.name}' заблокирован. "
                    f"Сначала завершите и отправьте на проверку урок {prev_lesson.lesson_number}: '{prev_lesson.name}'",
                )
                return redirect(
                    "students:course_detail", user_uuid=profile.id, course_slug=course.slug
                )

    raw_steps = lesson.steps.all()
    form = LessonSubmissionForm()

    existing_submission = (
        LessonSubmission.objects.filter(student=profile, lesson=lesson)
        .select_related("review")
        .prefetch_related("review__improvements")
        .first()
    )

    steps_list = []
    for step in raw_steps:
        progress = StepProgress.objects.filter(profile=profile, step=step).first()
        steps_list.append(
            {
                "step": step,
                "is_completed": bool(progress.is_completed) if progress else False,
                "completed_at": (
                    progress.completed_at if progress and progress.is_completed else None
                ),
            }
        )

    last_incomplete_step = next((s["step"] for s in steps_list if not s["is_completed"]), None)
    if not last_incomplete_step:
        last_incomplete_step = raw_steps.last()

    lesson_progress = lesson.get_progress_for_profile(profile)

    total_lessons = lesson.course.lessons.count()

    prev_lesson = (
        lesson.course.lessons.filter(lesson_number__lt=lesson.lesson_number)
        .order_by("-lesson_number")
        .first()
    )
    next_lesson = (
        lesson.course.lessons.filter(lesson_number__gt=lesson.lesson_number)
        .order_by("lesson_number")
        .first()
    )

    incomplete_improvements = 0
    if existing_submission:
        incomplete_improvements = existing_submission.improvements.filter(
            is_completed=False
        ).count()

    next_lesson_available = False
    if next_lesson and existing_submission and existing_submission.status == "approved":
        total_steps = lesson.steps.count()
        completed_steps = StepProgress.objects.filter(
            profile=profile, step__lesson=lesson, is_completed=True
        ).count()

        if completed_steps >= total_steps:
            next_lesson_available = True
            logger.info(
                f"Next lesson unlocked for {request.user.email}: "
                f"all {completed_steps}/{total_steps} steps completed in lesson {lesson.slug}"
            )
        else:
            logger.warning(
                f"Next lesson BLOCKED for {request.user.email}: "
                f"only {completed_steps}/{total_steps} steps completed in lesson {lesson.slug}"
            )

    return render(
        request,
        "students/dashboard/lesson-detail.html",
        {
            "course": course,
            "lesson": lesson,
            "user_uuid": user_uuid,  # Добавлено для формирования URL
            "steps": steps_list,
            "submission_form": form if not existing_submission else None,
            "existing_submission": existing_submission,
            "lesson_progress": lesson_progress,
            "last_incomplete_step": last_incomplete_step,
            "total_lessons": total_lessons,
            "estimated_time": lesson_progress.get("total_steps", 0)
            * MINUTES_PER_STEP,  # 20 мин на шаг для начинающего
            "prev_lesson": prev_lesson,
            "next_lesson": next_lesson,
            "next_lesson_available": next_lesson_available,
            "incomplete_improvements_count": incomplete_improvements,
        },
    )


@login_required
def lesson_submit_view(request, user_uuid: uuid.UUID, course_slug, lesson_slug):
    """
    AJAX обработка отправки работы на проверку.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Метод не поддерживается"}, status=405)

    profile = get_object_or_404(Student, user=request.user)
    course = get_object_or_404(profile.courses, slug=course_slug)
    lesson = get_object_or_404(course.lessons, slug=lesson_slug, course=course)

    total_steps = lesson.steps.count()
    completed_steps = StepProgress.objects.filter(
        profile=profile, step__lesson=lesson, is_completed=True
    ).count()

    if completed_steps < total_steps:
        return JsonResponse(
            {
                "success": False,
                "error": "Необходимо выполнить все шаги урока перед отправкой работы",
                "completed_steps": completed_steps,
                "total_steps": total_steps,
            },
            status=400,
        )

    form = LessonSubmissionForm(request.POST)

    if form.is_valid():
        existing_submission = LessonSubmission.objects.filter(
            student=profile, lesson=lesson
        ).first()

        is_resubmission = False
        if existing_submission:
            # Обновляем существующую работу (resubmit)
            # Увеличиваем revision_count только если работа была возвращена на доработку
            if existing_submission.status == "changes_requested":
                existing_submission.revision_count += 1
                is_resubmission = True

            existing_submission.lesson_url = form.cleaned_data["lesson_url"]
            existing_submission.status = "pending"  # Сбрасываем статус
            existing_submission.submitted_at = timezone.now()
            existing_submission.mentor = None  # Очищаем ментора для новой проверки
            existing_submission.mentor_comment = ""  # Очищаем старый комментарий
            existing_submission.reviewed_at = None  # Очищаем дату проверки

            # НЕ помечаем улучшения как выполненные - они остаются для истории
            # Студент может сам отметить их как выполненные через UI

            # Удаляем старый review чтобы избежать конфликта OneToOne при повторной проверке
            # Улучшения (StudentImprovement) НЕ удаляются т.к. теперь связаны с submission
            # и имеют on_delete=SET_NULL для review
            if hasattr(existing_submission, "review") and existing_submission.review:
                existing_submission.review.delete()

            existing_submission.save()

            # Уведомляем ревьюеров о повторной отправке работы
            if is_resubmission:
                from authentication.models import Reviewer
                from reviewers.tasks import send_new_submission_notification

                course = lesson.course
                reviewers = Reviewer.objects.filter(
                    courses=course, is_active=True, notify_new_submissions=True
                ).select_related("user")

                if reviewers.exists():
                    reviewer_emails = [r.user.email for r in reviewers]
                    student_name = profile.user.get_full_name() or profile.user.email

                    try:
                        send_new_submission_notification.delay(
                            reviewer_emails=reviewer_emails,
                            student_name=student_name,
                            course_name=course.name,
                            lesson_name=lesson.name,
                            lesson_url=existing_submission.lesson_url,
                            submission_id=str(existing_submission.id),
                        )
                        logger.info(
                            f"Задача уведомлений о resubmit поставлена в очередь для {reviewers.count()} ревьюеров"
                        )
                    except Exception as celery_error:
                        logger.warning(
                            f"Не удалось поставить задачу уведомления ревьюеров в очередь Celery: {celery_error}. "
                            f"Отправляем email синхронно."
                        )

                        # Fallback: отправляем синхронно
                        try:
                            from django.conf import settings
                            from django.core.mail import EmailMessage
                            from django.template.loader import render_to_string

                            subject = f"🔄 Работа переотправлена на проверку: {lesson.name}"

                            text_message = (
                                f"Работа переотправлена на проверку\n\n"
                                f"Студент {student_name} переотправил работу после доработки.\n\n"
                                f"Курс: {course.name}\n"
                                f"Урок: {lesson.name}\n"
                                f"Ссылка на работу: {existing_submission.lesson_url}\n\n"
                                f"Перейти к проверке: {settings.SITE_URL}/reviewers/submissions/"
                            )

                            success_count = 0
                            for email in reviewer_emails:
                                try:
                                    html_message = render_to_string(
                                        "reviewers/email/new_submission.html",
                                        {
                                            "student_name": student_name,
                                            "course_name": course.name,
                                            "lesson_name": lesson.name,
                                            "lesson_url": existing_submission.lesson_url,
                                            "site_url": settings.SITE_URL,
                                            "reviewer_email": email,
                                        },
                                    )

                                    email_msg = EmailMessage(
                                        subject=subject,
                                        body=text_message,
                                        from_email=settings.DEFAULT_FROM_EMAIL,
                                        to=[email],
                                    )
                                    email_msg.content_subtype = "html"
                                    email_msg.body = html_message
                                    email_msg.send(fail_silently=False)
                                    success_count += 1
                                except Exception as email_error:
                                    logger.error(
                                        f"Не удалось отправить email на {email}: {email_error}"
                                    )

                            logger.info(
                                f"Email уведомления о resubmit отправлены синхронно: {success_count}/{len(reviewer_emails)} успешно "
                                f"(работа {existing_submission.id})"
                            )
                        except Exception as email_error:
                            logger.error(
                                f"Не удалось отправить email уведомления ревьюерам даже синхронно: {email_error}"
                            )
            submission = existing_submission
            message = (
                "Исправленная работа успешно отправлена на проверку!"
                if is_resubmission
                else "Работа успешно отправлена на проверку!"
            )
        else:
            # Создаем новую работу
            submission = form.save(commit=False)
            submission.student = profile
            submission.lesson = lesson
            submission.save()
            message = "Работа успешно отправлена на проверку!"

        response_data = {
            "success": True,
            "message": message,
            "submission": {
                "id": str(submission.id),
                "url": submission.lesson_url,
                "submitted_at": submission.submitted_at.isoformat(),
                "revision_count": submission.revision_count,
            },
        }
        return JsonResponse(response_data)
    else:
        response_data = {
            "success": False,
            "error": "Некорректная ссылка на GitHub",
            "errors": form.errors,
        }
        return JsonResponse(response_data, status=400)


@login_required
@csrf_exempt
def toggle_improvement_view(request, improvement_id):
    """
    API endpoint для переключения состояния выполнения улучшения от ревьюера.
    """
    from reviewers.models import StudentImprovement

    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Method not allowed"}, status=405)

    try:
        profile = get_object_or_404(Student, user=request.user)

        improvement = get_object_or_404(
            StudentImprovement, id=improvement_id, lesson_submission__student=profile
        )

        improvement.is_completed = not improvement.is_completed
        improvement.completed_at = timezone.now() if improvement.is_completed else None
        improvement.save(update_fields=["is_completed", "completed_at"])

        logger.info(
            f"Student {profile.user.email} toggled improvement {improvement_id} to {improvement.is_completed}"
        )

        return JsonResponse(
            {
                "success": True,
                "is_completed": improvement.is_completed,
                "improvement_id": str(improvement.id),
            }
        )
    except Exception as e:
        logger.error(f"Error toggling improvement {improvement_id}: {str(e)}")
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
def toggle_step_progress(request, course_slug, lesson_slug, step_id):
    """
    AJAX представление для переключения статуса прохождения шага.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Метод не поддерживается"}, status=405)

    profile = get_object_or_404(Student, user=request.user)
    course = get_object_or_404(profile.courses, slug=course_slug)
    lesson = get_object_or_404(course.lessons, slug=lesson_slug, course=course)
    step = get_object_or_404(Step, id=step_id, lesson=lesson)

    step_progress, created = StepProgress.objects.get_or_create(
        profile=profile, step=step, defaults={"is_completed": False}
    )

    try:
        import json

        body = json.loads(request.body.decode("utf-8"))
        completed = body.get("completed")
        if completed is not None:
            step_progress.is_completed = completed
        else:
            step_progress.is_completed = not step_progress.is_completed
    except (json.JSONDecodeError, AttributeError):
        step_progress.is_completed = not step_progress.is_completed

    step_progress.completed_at = timezone.now() if step_progress.is_completed else None
    step_progress.save()

    lesson.invalidate_progress_cache(profile)
    course.invalidate_progress_cache(profile)

    safe_cache_delete(f"user_courses_stats_{profile.id}")
    safe_cache_delete(f"dashboard_stats_{profile.id}")
    safe_cache_delete(f"course_detail_{course.id}_{profile.id}")

    lesson_progress = lesson.get_progress_for_profile(profile, use_cache=False)
    course_progress = course.get_progress_for_profile(profile, use_cache=False)

    return JsonResponse(
        {
            "success": True,
            "is_completed": step_progress.is_completed,
            "step_id": str(step.id),
            "lesson_progress": {
                "total_steps": lesson_progress["total_steps"],
                "completed_steps": lesson_progress["completed_steps"],
                "completion_percentage": lesson_progress["completion_percentage"],
                "is_completed": lesson_progress["is_completed"],
            },
            "course_progress": {
                "total_steps": course_progress["total_steps"],
                "completed_steps": course_progress["completed_steps"],
                "completion_percentage": course_progress["completion_percentage"],
                "completed_lessons": course_progress["completed_lessons"],
            },
        }
    )
