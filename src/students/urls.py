"""
Students URL Configuration

Маршруты для приложения личного кабинета студента.
Структура аналогична reviewers app для консистентности.

Все маршруты требуют авторизации и роль 'student'.

Автор: Pyland Team
Дата: 2025
"""

from django.urls import path

from . import views

app_name = "students"

urlpatterns = [
    # Dashboard и профиль
    path("dashboard/<uuid:user_uuid>/", views.dashboard_view, name="dashboard"),
    path("settings/<uuid:user_uuid>/", views.settings_view, name="settings"),
    path("avatar/delete/", views.delete_avatar_view, name="delete_avatar"),
    # Курсы и обучение
    path("courses/<uuid:user_uuid>/", views.courses_view, name="courses"),
    path(
        "courses/<uuid:user_uuid>/<slug:course_slug>/",
        views.course_detail_view,
        name="course_detail",
    ),
    path(
        "courses/<uuid:user_uuid>/<slug:course_slug>/lessons/<slug:lesson_slug>/",
        views.lesson_detail_view,
        name="lesson_detail",
    ),
    path(
        "courses/<uuid:user_uuid>/<slug:course_slug>/lessons/<slug:lesson_slug>/submit/",
        views.lesson_submit_view,
        name="lesson_submit",
    ),
    # API endpoints
    path(
        "api/toggle-improvement/<uuid:improvement_id>/",
        views.toggle_improvement_view,
        name="toggle_improvement",
    ),
    path(
        "courses/<slug:course_slug>/lessons/<slug:lesson_slug>/steps/<uuid:step_id>/toggle/",
        views.toggle_step_progress,
        name="toggle_step_progress",
    ),
    # Экспорт и удаление данных
    path("export-data/", views.export_user_data, name="export_user_data"),
    path("delete-account/", views.delete_account, name="delete_account"),
]
