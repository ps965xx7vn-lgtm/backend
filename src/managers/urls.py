"""
URL Configuration for Manager Application - Современная структура URL для менеджеров.

Структура аналогична reviewers app для консистентности.
Все views защищены декоратором @require_any_role(['manager']).

URL Patterns:
    Dashboard:
        - /dashboard/ - Главная страница менеджера

    Feedback (Обратная связь):
        - /feedback/ - Список всех обращений
        - /feedback/<id>/ - Детальный просмотр обращения
        - /feedback/<id>/delete/ - Удаление обращения

    System Logs (Системные логи):
        - /logs/ - Просмотр системных логов

    API Endpoints:
        - /api/feedback-stats/ - Статистика по обратной связи
        - /api/unprocessed-count/ - Количество необработанных обращений

Автор: Pyland Team
Дата: 2025
"""

from __future__ import annotations

from django.urls import path

from . import views

app_name = "managers"

urlpatterns = [
    # Dashboard
    path("<uuid:user_uuid>/dashboard/", views.dashboard_view, name="dashboard"),
    # Feedback Management
    path("<uuid:user_uuid>/feedback/", views.feedback_list_view, name="feedback_list"),
    path("<uuid:user_uuid>/feedback/<int:pk>/", views.feedback_detail_view, name="feedback_detail"),
    path(
        "<uuid:user_uuid>/feedback/<int:pk>/delete/",
        views.feedback_delete_view,
        name="feedback_delete",
    ),
    # System Logs
    path("<uuid:user_uuid>/logs/", views.system_logs_view, name="system_logs"),
    # API Endpoints
    path(
        "<uuid:user_uuid>/api/feedback-stats/", views.api_feedback_stats, name="api_feedback_stats"
    ),
    path(
        "<uuid:user_uuid>/api/unprocessed-count/",
        views.api_unprocessed_count,
        name="api_unprocessed_count",
    ),
]
