"""
Reviewers Context Processors - Процессоры контекста для reviewers приложения.

Этот модуль добавляет общий контекст для всех шаблонов reviewers:
- pending_count: количество работ на проверку
- unread_count: количество непрочитанных уведомлений

Использование:
    Добавьте в settings.py:
    TEMPLATES = [{
        'OPTIONS': {
            'context_processors': [
                ...
                'reviewers.context_processors.reviewers_context',
            ],
        },
    }]

Автор: Pyland Team
Дата: 2025
"""

from __future__ import annotations

from typing import Any, Dict

from django.http import HttpRequest

from .models import LessonSubmission, ReviewerNotification


def reviewers_context(request: HttpRequest) -> Dict[str, Any]:
    """
    Добавляет контекст для reviewers приложения.

    Возвращает:
        - pending_count: количество работ в статусе pending для ревьюера
        - unread_count: количество непрочитанных уведомлений
    """
    context = {
        "pending_count": 0,
        "unread_count": 0,
    }

    # Проверяем что пользователь авторизован и является ревьюером
    if not request.user.is_authenticated:
        return context

    # Проверяем наличие reviewer_profile
    if not hasattr(request.user, "reviewer_profile"):
        return context

    reviewer = request.user.reviewer_profile

    # Количество работ на проверку
    context["pending_count"] = LessonSubmission.objects.filter(
        status="pending", lesson__course__in=reviewer.courses.all()
    ).count()

    # Количество непрочитанных уведомлений
    context["unread_count"] = ReviewerNotification.objects.filter(
        reviewer=reviewer, is_read=False
    ).count()

    return context
