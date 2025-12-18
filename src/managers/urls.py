"""
URL Configuration for Manager Application - URL маршруты административной панели.

Этот модуль определяет URL паттерны для веб-интерфейса менеджера.
Все views требуют прав администратора (@staff_member_required).

URL Patterns:
    Dashboard:
        - / - Главная страница dashboard

    Feedback (Обратная связь):
        - /feedback/ - Список всех обращений
        - /feedback/<id>/ - Детальный просмотр обращения
        - /feedback/<id>/delete/ - Удаление обращения

    System Logs (Системные логи):
        - /logs/ - Просмотр системных логов

    Settings (Настройки):
        - /settings/ - Управление настройками системы

Примечание:
    API endpoints находятся в api.py и доступны через /api/managers/

Автор: Pyland Team
Дата: 2025
"""

from __future__ import annotations

from django.urls import path

from . import views

app_name = "managers"

urlpatterns = [
    # ========================================================================
    # DASHBOARD - Главная страница
    # ========================================================================
    path("", views.manager_dashboard, name="dashboard"),
    # ========================================================================
    # FEEDBACK MANAGEMENT - Управление обратной связью
    # ========================================================================
    path("feedback/", views.feedback_list, name="feedback_list"),
    path("feedback/<int:pk>/", views.feedback_detail, name="feedback_detail"),
    path("feedback/<int:pk>/delete/", views.feedback_delete, name="feedback_delete"),
    # ========================================================================
    # SYSTEM LOGS - Системные логи
    # ========================================================================
    path("logs/", views.system_logs, name="system_logs"),
    # ========================================================================
    # SYSTEM SETTINGS - Настройки системы
    # ========================================================================
    path("settings/", views.system_settings, name="system_settings"),
]
