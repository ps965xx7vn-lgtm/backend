"""
Context processors для приложения Students.

Добавляет глобальные переменные в контекст всех шаблонов.
"""

from typing import Any

from django.http import HttpRequest


def student_profile(request: HttpRequest) -> dict[str, Any]:
    """
    Добавляет профиль студента в контекст всех шаблонов.
    
    Это позволяет использовать {{ student_profile.id }} в любом template
    вместо {{ request.user.student.id }}.
    
    Args:
        request: HTTP запрос
        
    Returns:
        dict: Контекст с профилем студента
    """
    context = {}
    
    if request.user.is_authenticated:
        try:
            # Пытаемся получить профиль студента
            profile = request.user.student
            context['student_profile'] = profile
        except (AttributeError, Exception):
            # Если у пользователя нет профиля студента (например, это менеджер)
            context['student_profile'] = None
    else:
        context['student_profile'] = None
        
    return context
