"""
Pyland School Main API Configuration

Главный API файл, объединяющий все роутеры приложений.
Используется Django Ninja для REST API.

Доступен по адресу: /api/

Подключенные модули:
- /auth/ - аутентификация и регистрация
- /students/ - управление профилем пользователя
- /blog/ - блог и статьи
- /certificates/ - сертификаты
- /core/ - основные функции (feedback, subscription, stats)
- /courses/ - курсы и уроки
- /mentors/ - менторы
- /notifications/ - уведомления
- /payments/ - платежи
- /reviews/ - отзывы
- /support/ - поддержка

Health check: GET /api/ping
"""

from ninja import NinjaAPI
from ninja_jwt.authentication import JWTAuth

from authentication.api import auth_router
from blog.api import router as blog_router
from certificates.api import router as certificates_router
from core.api import router as core_router
from core.health import health_check, readiness_check
from courses.api import router as courses_router
from managers.api import router as manager_router
from mentors.api import router as mentors_router
from notifications.api import router as notifications_router
from payments.api import router as payments_router
from reviewers.api import router as reviews_router
from students.api import router as account_router
from support.api import router as support_router

# Глобальная переменная для хранения единственного экземпляра API
_api_instance = None


def get_api():
    """
    Возвращает singleton инстанс NinjaAPI.

    Используется для предотвращения создания множественных экземпляров API.
    """
    global _api_instance

    if _api_instance is not None:
        return _api_instance

    api_instance = NinjaAPI(
        title="Pyland School API",
        version="1.0.0",
        description="API для онлайн‑школы Pyland",
        auth=JWTAuth(),
        urls_namespace="pyland_api",
    )

    # Аутентификация и регистрация
    api_instance.add_router("/auth/", auth_router)

    # Управление профилями студентов
    api_instance.add_router("/students/", account_router)

    # Основные модули приложения
    api_instance.add_router("/blog/", blog_router)
    api_instance.add_router("/certificates/", certificates_router)
    api_instance.add_router("/core/", core_router)
    api_instance.add_router("/courses/", courses_router)
    api_instance.add_router("/managers/", manager_router)  # Admin-only endpoints
    api_instance.add_router("/mentors/", mentors_router)
    api_instance.add_router("/notifications/", notifications_router)
    api_instance.add_router("/payments/", payments_router)
    api_instance.add_router("/reviews/", reviews_router)
    api_instance.add_router("/support/", support_router)

    @api_instance.get("/ping", auth=None)
    def ping(request):
        """
        Health check эндпоинт.

        Публичный эндпоинт для проверки доступности API.

        Returns:
            dict: {"ping": "pong"}

        Example:
            GET /api/ping
            Response: {"ping": "pong"}
        """
        return {"ping": "pong"}

    @api_instance.get("/health/", auth=None, include_in_schema=False)
    def health_endpoint(request):
        """
        Liveness probe для Docker/Kubernetes.
        Базовая проверка что приложение запущено.
        """
        return health_check()

    @api_instance.get("/readiness/", auth=None, include_in_schema=False)
    def readiness_endpoint(request):
        """
        Readiness probe для Kubernetes.
        Проверка что приложение готово обрабатывать запросы (БД, Redis доступны).
        """
        from ninja.responses import Response

        result = readiness_check()
        status_code = 200 if result.get("ready", False) else 503
        return Response(result, status=status_code)

    _api_instance = api_instance
    return _api_instance


# Создаем API при первом импорте модуля
api = get_api()
