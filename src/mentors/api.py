"""
Mentors API Module - REST API для работы с менторами.

Этот модуль будет содержать эндпоинты для менторов:

Планируемые Endpoints:
    GET    /api/mentors/                    - Список менторов
    GET    /api/mentors/{id}                - Профиль ментора
    GET    /api/mentors/{id}/students       - Студенты ментора
    POST   /api/mentors/{id}/assign         - Назначить студента
    GET    /api/mentors/{id}/availability   - Расписание консультаций
    POST   /api/mentors/{id}/sessions       - Записаться на консультацию

Особенности:
    - Интеграция с Reviewer моделью из authentication
    - Управление связями ментор-студент
    - Система консультаций
    - Обратная связь от студентов

Автор: Pyland Team
Дата: 2025
"""

from ninja import Router

router = Router()


# Пример эндпоинта для теста
@router.get("/ping")
def ping(request):
    return {"ping": "pong"}
