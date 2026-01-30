"""
Reviewers URLs - Современная структура URL для приложения reviewers.

Структура аналогична students app для консистентности.

Автор: Pyland Team
Дата: 2025
"""

from django.urls import path

from . import views

app_name = "reviewers"

urlpatterns = [
    # Dashboard
    path("dashboard/<uuid:user_uuid>/", views.dashboard_view, name="dashboard"),
    # Работы
    path("submissions/<uuid:user_uuid>/", views.submissions_list_view, name="submissions"),
    path(
        "submissions/<uuid:user_uuid>/<uuid:submission_id>/",
        views.submission_review_view,
        name="submission_review",
    ),
    path(
        "submissions/<uuid:user_uuid>/<uuid:submission_id>/detail/",
        views.submission_detail_view,
        name="submission_detail",
    ),
    # Дополнительные страницы (MVP)
    path("history/<uuid:user_uuid>/", views.history_view, name="history"),
    path("statistics/<uuid:user_uuid>/", views.statistics_view, name="statistics"),
    # Настройки
    path("settings/<uuid:user_uuid>/", views.settings_view, name="settings"),
    # API endpoints
    path("api/pending-count/", views.api_pending_count, name="api_pending_count"),
]
