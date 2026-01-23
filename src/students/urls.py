"""
Students URL Configuration

Маршруты для приложения личного кабинета студента:
- Dashboard и статистика прогресса
- Настройки профиля и аватара
- Просмотр и прохождение курсов
- Отправка работ на проверку
- Управление замечаниями ревьюеров
- Экспорт данных и удаление аккаунта

Все маршруты требуют авторизации и роль 'student'.
"""

from django.urls import path

from . import views

app_name = "students"

urlpatterns = [
    # Dashboard и профиль
    path("dashboard/<uuid:user_uuid>/", views.account_dashboard_view, name="account_dashboard"),
    path("settings/", views.account_settings_view, name="account_settings"),
    path("avatar/delete/", views.delete_avatar_view, name="delete_avatar"),
    # Курсы и обучение
    path("courses/", views.account_courses_view, name="account_courses"),
    path(
        "courses/<slug:course_slug>/",
        views.account_course_detail_view,
        name="account_course_detail",
    ),
    path(
        "courses/<slug:course_slug>/lessons/<slug:lesson_slug>/",
        views.account_lesson_detail_view,
        name="account_lesson_detail",
    ),
    path(
        "courses/<slug:course_slug>/lessons/<slug:lesson_slug>/submit/",
        views.account_lesson_submit_view,
        name="account_lesson_submit",
    ),
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
