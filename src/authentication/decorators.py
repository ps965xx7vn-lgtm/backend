"""
Authentication Decorators Module - Декораторы для управления доступом на основе ролей и permissions.

Этот модуль содержит декораторы для проверки ролей и permissions пользователей
в API endpoints (Django Ninja) и Django views. Поддерживает:
- Проверку одной или нескольких ролей
- Проверку Django permissions
- Комбинированные проверки (роль + permissions)
- Разделение для API (JSON) и веб-views (редиректы)

Decorators:
    - require_role: Проверяет наличие конкретной роли
    - require_any_role: Проверяет наличие хотя бы одной из ролей
    - require_permission: Проверяет Django permission
    - require_any_permission: Проверяет хотя бы один permission
    - require_role_and_permission: Комбинированная проверка

Utilities:
    - has_role: Проверить роль пользователя
    - has_permission: Проверить permission пользователя
    - get_user_role: Получить текущую роль

Author: Pyland Team
Date: 2025
"""

from __future__ import annotations

import functools
import logging
from collections.abc import Callable

from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse

logger = logging.getLogger(__name__)

# ============================================================================
# УТИЛИТЫ ДЛЯ ПРОВЕРКИ РОЛЕЙ И PERMISSIONS
# ============================================================================


def has_role(user, role_name: str) -> bool:
    """
    Проверяет наличие конкретной роли у пользователя.

    Args:
        user: Django User объект
        role_name: Название роли ('student', 'mentor', 'reviewer', 'manager', 'admin', 'support')

    Returns:
        bool: True если у пользователя есть роль

    Example:
        >>> if has_role(request.user, 'reviewer'):
        ...     # Код для ревьюера
    """
    if not user or not user.is_authenticated:
        return False

    # Superuser имеет все роли (для Django admin)
    if user.is_superuser:
        return True

    try:
        return user.role and user.role.name == role_name
    except Exception as e:
        logger.error(f"Error checking role for user {user.id}: {e}")
        return False


def has_permission(user, permission: str) -> bool:
    """
    Проверяет наличие Django permission у пользователя.

    Args:
        user: Django User объект
        permission: Строка вида 'app.permission_codename' (например, 'authentication.review_submissions')

    Returns:
        bool: True если у пользователя есть permission

    Example:
        >>> if has_permission(request.user, 'authentication.review_submissions'):
        ...     # Код для проверки работ
    """
    if not user or not user.is_authenticated:
        return False

    # Superuser имеет все permissions
    if user.is_superuser:
        return True

    try:
        return user.has_perm(permission)
    except Exception as e:
        logger.error(f"Error checking permission '{permission}' for user {user.id}: {e}")
        return False


def get_user_role(user) -> str | None:
    """
    Получает текущую роль пользователя.

    Args:
        user: Django User объект

    Returns:
        Optional[str]: Название роли или None

    Example:
        >>> role = get_user_role(request.user)
        >>> if role == 'admin':
        ...     # Показать админ-панель
    """
    if not user or not user.is_authenticated:
        return None

    try:
        return user.role.name if user.role else None
    except Exception as e:
        logger.error(f"Error getting role for user {user.id}: {e}")
        return None


# ============================================================================
# ДЕКОРАТОРЫ ДЛЯ ПРОВЕРКИ РОЛЕЙ
# ============================================================================


def require_role(
    role_name: str, *, api_response: bool = False, redirect_url: str | None = None
) -> Callable:
    """
    Декоратор для проверки наличия конкретной роли.

    Args:
        role_name: Название роли ('student', 'mentor', 'reviewer', 'manager', 'admin', 'support')
        api_response: Если True, возвращает JSON ошибку (для API). Если False - редирект (для views)
        redirect_url: URL для редиректа при отсутствии роли (только для views)

    Example:
        Для API:
        >>> @require_role('reviewer', api_response=True)
        ... def review_submission(request, submission_id: int):
        ...     return {"status": "ok"}

        Для Django view:
        >>> @require_role('manager', redirect_url='/dashboard/')
        ... def admin_dashboard(request):
        ...     return render(request, 'admin.html')
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            # Проверка авторизации
            if not request.user.is_authenticated:
                logger.warning(f"Unauthorized access attempt to {func.__name__}")

                if api_response:
                    return JsonResponse(
                        {
                            "error": "Unauthorized",
                            "detail": "Authentication required",
                            "code": "auth_required",
                        },
                        status=401,
                    )
                else:
                    return redirect(f"{reverse('authentication:signin')}?next={request.path}")

            # Проверка роли
            if not has_role(request.user, role_name):
                user_role = get_user_role(request.user)
                logger.warning(
                    f"User {request.user.email} (role: {user_role}) denied access to "
                    f"{func.__name__}: required role '{role_name}'"
                )

                if api_response:
                    return JsonResponse(
                        {
                            "error": "Forbidden",
                            "detail": f"Role '{role_name}' required",
                            "code": "role_required",
                            "required_role": role_name,
                            "current_role": user_role,
                        },
                        status=403,
                    )
                else:
                    if redirect_url:
                        return redirect(redirect_url)
                    else:
                        return HttpResponseForbidden(f"Access denied. Role '{role_name}' required.")

            logger.info(f"User {request.user.email} (role: {role_name}) accessed {func.__name__}")

            return func(request, *args, **kwargs)

        return wrapper

    return decorator


def require_any_role(
    role_names: list[str], *, api_response: bool = False, redirect_url: str | None = None
) -> Callable:
    """
    Декоратор для проверки наличия хотя бы одной из ролей.

    Args:
        role_names: Список названий ролей
        api_response: Если True, возвращает JSON ошибку (для API)
        redirect_url: URL для редиректа при отсутствии ролей (только для views)

    Example:
        >>> @require_any_role(['mentor', 'reviewer'], api_response=True)
        ... def submit_review(request):
        ...     return {"status": "submitted"}
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            # Проверка авторизации
            if not request.user.is_authenticated:
                logger.warning(f"Unauthorized access attempt to {func.__name__}")

                if api_response:
                    return JsonResponse(
                        {
                            "error": "Unauthorized",
                            "detail": "Authentication required",
                            "code": "auth_required",
                        },
                        status=401,
                    )
                else:
                    return redirect(f"{reverse('authentication:signin')}?next={request.path}")

            # Проверка роли
            user_role = get_user_role(request.user)
            has_any_role = any(has_role(request.user, role) for role in role_names)

            if not has_any_role:
                logger.warning(
                    f"User {request.user.email} (role: {user_role}) denied access to "
                    f"{func.__name__}: required one of {role_names}"
                )

                if api_response:
                    return JsonResponse(
                        {
                            "error": "Forbidden",
                            "detail": f"One of these roles required: {', '.join(role_names)}",
                            "code": "role_required",
                            "required_roles": role_names,
                            "current_role": user_role,
                        },
                        status=403,
                    )
                else:
                    if redirect_url:
                        return redirect(redirect_url)
                    else:
                        return HttpResponseForbidden(
                            f"Access denied. Requires one of roles: {', '.join(role_names)}"
                        )

            logger.info(f"User {request.user.email} (role: {user_role}) accessed {func.__name__}")

            return func(request, *args, **kwargs)

        return wrapper

    return decorator


# ============================================================================
# ДЕКОРАТОРЫ ДЛЯ ПРОВЕРКИ PERMISSIONS
# ============================================================================


def require_permission(
    permission: str, *, api_response: bool = False, redirect_url: str | None = None
) -> Callable:
    """
    Декоратор для проверки наличия Django permission.

    Args:
        permission: Строка вида 'app.permission_codename' (например, 'authentication.review_submissions')
        api_response: Если True, возвращает JSON ошибку (для API)
        redirect_url: URL для редиректа при отсутствии permission (только для views)

    Example:
        >>> @require_permission('authentication.review_submissions', api_response=True)
        ... def review_assignment(request, assignment_id: int):
        ...     return {"status": "reviewed"}
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            # Проверка авторизации
            if not request.user.is_authenticated:
                logger.warning(f"Unauthorized access attempt to {func.__name__}")

                if api_response:
                    return JsonResponse(
                        {
                            "error": "Unauthorized",
                            "detail": "Authentication required",
                            "code": "auth_required",
                        },
                        status=401,
                    )
                else:
                    return redirect(f"{reverse('authentication:signin')}?next={request.path}")

            # Проверка permission
            if not has_permission(request.user, permission):
                logger.warning(
                    f"User {request.user.email} denied access to {func.__name__}: "
                    f"missing permission '{permission}'"
                )

                if api_response:
                    return JsonResponse(
                        {
                            "error": "Forbidden",
                            "detail": f"Permission '{permission}' required",
                            "code": "permission_required",
                            "required_permission": permission,
                        },
                        status=403,
                    )
                else:
                    if redirect_url:
                        return redirect(redirect_url)
                    else:
                        return HttpResponseForbidden(
                            f"Access denied. Permission '{permission}' required."
                        )

            logger.info(
                f"User {request.user.email} accessed {func.__name__} with permission '{permission}'"
            )

            return func(request, *args, **kwargs)

        return wrapper

    return decorator


def require_any_permission(
    permissions: list[str], *, api_response: bool = False, redirect_url: str | None = None
) -> Callable:
    """
    Декоратор для проверки наличия хотя бы одного из permissions.

    Args:
        permissions: Список permissions ('app.permission_codename')
        api_response: Если True, возвращает JSON ошибку (для API)
        redirect_url: URL для редиректа при отсутствии permissions (только для views)

    Example:
        >>> @require_any_permission([
        ...     'authentication.review_submissions',
        ...     'authentication.approve_submissions'
        ... ], api_response=True)
        ... def handle_submission(request, submission_id: int):
        ...     return {"status": "handled"}
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            # Проверка авторизации
            if not request.user.is_authenticated:
                logger.warning(f"Unauthorized access attempt to {func.__name__}")

                if api_response:
                    return JsonResponse(
                        {
                            "error": "Unauthorized",
                            "detail": "Authentication required",
                            "code": "auth_required",
                        },
                        status=401,
                    )
                else:
                    return redirect(f"{reverse('login')}?next={request.path}")

            # Проверка permissions
            has_any_perm = any(has_permission(request.user, perm) for perm in permissions)

            if not has_any_perm:
                logger.warning(
                    f"User {request.user.email} denied access to {func.__name__}: "
                    f"missing any of permissions {permissions}"
                )

                if api_response:
                    return JsonResponse(
                        {
                            "error": "Forbidden",
                            "detail": f"One of these permissions required: {', '.join(permissions)}",
                            "code": "permission_required",
                            "required_permissions": permissions,
                        },
                        status=403,
                    )
                else:
                    if redirect_url:
                        return redirect(redirect_url)
                    else:
                        return HttpResponseForbidden(
                            f"Access denied. Requires one of permissions: {', '.join(permissions)}"
                        )

            logger.info(
                f"User {request.user.email} accessed {func.__name__} with valid permissions"
            )

            return func(request, *args, **kwargs)

        return wrapper

    return decorator


# ============================================================================
# КОМБИНИРОВАННЫЕ ДЕКОРАТОРЫ
# ============================================================================


def require_role_and_permission(
    role_name: str,
    permission: str,
    *,
    api_response: bool = False,
    redirect_url: str | None = None,
) -> Callable:
    """
    Декоратор для проверки роли И permission одновременно.

    Args:
        role_name: Название роли
        permission: Django permission ('app.permission_codename')
        api_response: Если True, возвращает JSON ошибку (для API)
        redirect_url: URL для редиректа (только для views)

    Example:
        >>> @require_role_and_permission(
        ...     'reviewer',
        ...     'authentication.approve_submissions',
        ...     api_response=True
        ... )
        ... def approve_assignment(request, assignment_id: int):
        ...     return {"status": "approved"}
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            # Проверка авторизации
            if not request.user.is_authenticated:
                logger.warning(f"Unauthorized access attempt to {func.__name__}")

                if api_response:
                    return JsonResponse(
                        {
                            "error": "Unauthorized",
                            "detail": "Authentication required",
                            "code": "auth_required",
                        },
                        status=401,
                    )
                else:
                    return redirect(f"{reverse('login')}?next={request.path}")

            # Проверка роли
            user_role = get_user_role(request.user)
            if not has_role(request.user, role_name):
                logger.warning(
                    f"User {request.user.email} (role: {user_role}) denied access to "
                    f"{func.__name__}: required role '{role_name}'"
                )

                if api_response:
                    return JsonResponse(
                        {
                            "error": "Forbidden",
                            "detail": f"Role '{role_name}' required",
                            "code": "role_required",
                            "required_role": role_name,
                            "current_role": user_role,
                        },
                        status=403,
                    )
                else:
                    if redirect_url:
                        return redirect(redirect_url)
                    else:
                        return HttpResponseForbidden(f"Access denied. Role '{role_name}' required.")

            # Проверка permission
            if not has_permission(request.user, permission):
                logger.warning(
                    f"User {request.user.email} denied access to {func.__name__}: "
                    f"missing permission '{permission}'"
                )

                if api_response:
                    return JsonResponse(
                        {
                            "error": "Forbidden",
                            "detail": f"Permission '{permission}' required",
                            "code": "permission_required",
                            "required_permission": permission,
                        },
                        status=403,
                    )
                else:
                    if redirect_url:
                        return redirect(redirect_url)
                    else:
                        return HttpResponseForbidden(
                            f"Access denied. Permission '{permission}' required."
                        )

            logger.info(
                f"User {request.user.email} (role: {role_name}) accessed {func.__name__} "
                f"with permission '{permission}'"
            )

            return func(request, *args, **kwargs)

        return wrapper

    return decorator


# ============================================================================
# ДЕКОРАТОР ДЛЯ РОУТИНГА ПО ДАШБОРДАМ
# ============================================================================


def redirect_to_role_dashboard(view_func: Callable) -> Callable:
    """
    Декоратор для автоматического перенаправления на dashboard в зависимости от роли.

    Использовать на view, которые должны показывать разные dashboard'ы для разных ролей.
    Например, общая точка входа '/dashboard/' может перенаправить на соответствующий dashboard.

    Поддерживаемые роли и их маршруты:
    - manager → managers:dashboard (управление платформой)
    - mentor → reviewers:dashboard (проверка работ + менторство)
    - reviewer → reviewers:dashboard (проверка работ)
    - student → students:dashboard (личный кабинет студента)
    - is_staff → managers:dashboard (персонал платформы)
    - Без роли → core:home (главная страница)
    - Не авторизован → authentication:login

    Example:
        >>> @redirect_to_role_dashboard
        >>> def dashboard_router(request):
        ...     # Этот код никогда не выполнится, т.к. произойдет редирект
        ...     pass

    Args:
        view_func: View функция для декорирования

    Returns:
        Callable: Обёрнутая функция с роутингом
    """

    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            logger.info("Unauthenticated user accessing dashboard, redirecting to login")
            return redirect(reverse("authentication:signin"))

        role = get_user_role(request.user)

        # Роль: manager - управление платформой
        if role == "manager":
            try:
                manager = request.user.manager
                logger.info(f"Redirecting {request.user.email} (manager) to managers dashboard")
                return redirect(reverse("managers:dashboard", kwargs={"user_uuid": manager.id}))
            except Exception as e:
                logger.error(f"Error getting manager profile for {request.user.email}: {e}")
                return redirect(reverse("core:home"))

        # Роль: mentor - проверка работ и менторство (пока через managers dashboard)
        elif role == "mentor":
            try:
                # У mentor может быть либо reviewer, либо manager профиль
                if hasattr(request.user, "reviewer"):
                    reviewer = request.user.reviewer
                    logger.info(f"Redirecting {request.user.email} (mentor) to reviewers dashboard")
                    return redirect(
                        reverse("reviewers:dashboard", kwargs={"user_uuid": reviewer.id})
                    )
                elif hasattr(request.user, "manager"):
                    manager = request.user.manager
                    logger.info(f"Redirecting {request.user.email} (mentor) to managers dashboard")
                    return redirect(reverse("managers:dashboard", kwargs={"user_uuid": manager.id}))
                else:
                    return redirect(reverse("core:home"))
            except Exception as e:
                logger.error(f"Error getting mentor profile for {request.user.email}: {e}")
                return redirect(reverse("core:home"))

        # Роль: reviewer - проверка работ студентов
        elif role == "reviewer":
            try:
                reviewer = request.user.reviewer
                logger.info(f"Redirecting {request.user.email} (reviewer) to reviewers dashboard")
                return redirect(reverse("reviewers:dashboard", kwargs={"user_uuid": reviewer.id}))
            except Exception as e:
                logger.error(f"Error getting reviewer profile for {request.user.email}: {e}")
                return redirect(reverse("core:home"))

        # Роль: student - личный кабинет
        elif role == "student":
            try:
                student = request.user.student
                logger.info(f"Redirecting {request.user.email} (student) to student dashboard")
                return redirect(reverse("students:dashboard", kwargs={"user_uuid": student.id}))
            except Exception as e:
                logger.error(f"Error getting student profile for {request.user.email}: {e}")
                return redirect(reverse("core:home"))

        # is_staff без роли - на managers dashboard (если есть профиль)
        elif request.user.is_staff:
            try:
                # Ищем любой профиль с dashboard доступом
                if hasattr(request.user, "manager"):
                    manager = request.user.manager
                    logger.info(
                        f"Redirecting staff user {request.user.email} to managers dashboard"
                    )
                    return redirect(reverse("managers:dashboard", kwargs={"user_uuid": manager.id}))
                elif hasattr(request.user, "admin"):
                    admin = request.user.admin
                    logger.info(
                        f"Redirecting staff user {request.user.email} to managers dashboard"
                    )
                    return redirect(reverse("managers:dashboard", kwargs={"user_uuid": admin.id}))
                else:
                    return redirect(reverse("core:home"))
            except Exception as e:
                logger.error(f"Error getting staff profile for {request.user.email}: {e}")
                return redirect(reverse("core:home"))

        # Нет роли или неизвестная роль - на главную
        else:
            logger.warning(
                f"Unknown or missing role '{role}' for user {request.user.email}, redirecting to home"
            )
            return redirect(reverse("core:home"))

    return wrapper


# ============================================================================
# API-SPECIFIC DECORATORS - Декораторы для API endpoints
# ============================================================================


def require_role_api(role_names: list[str]) -> Callable:
    """
    Декоратор для проверки роли в API endpoints (Django Ninja).

    Всегда возвращает JSON ответы (HttpError).
    Использует аутентификацию через JWT (уже настроено в router).

    Args:
        role_names: Список разрешенных ролей

    Returns:
        Callable: Декорированная функция

    Raises:
        HttpError: 403 если роль не соответствует

    Example:
        >>> from ninja import Router
        >>> from ninja_jwt.authentication import JWTAuth
        >>>
        >>> router = Router(auth=JWTAuth())
        >>>
        >>> @router.get("/manager-only/")
        >>> @require_role_api(['manager'])
        >>> def manager_endpoint(request):
        >>>     return {"status": "ok"}
    """
    from ninja.errors import HttpError

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            # Проверка аутентификации (JWT уже проверен на уровне router)
            if not request.user.is_authenticated:
                logger.warning(f"Unauthorized API access attempt to {func.__name__}")
                raise HttpError(401, "Authentication required")

            # Проверка роли
            user_role = get_user_role(request.user)
            has_required_role = any(has_role(request.user, role) for role in role_names)

            if not has_required_role:
                logger.warning(
                    f"User {request.user.email} (role: {user_role}) denied API access to "
                    f"{func.__name__}: required roles {role_names}"
                )
                raise HttpError(
                    403,
                    f"Access denied. Required roles: {', '.join(role_names)}. Your role: {user_role or 'none'}",
                )

            logger.debug(
                f"User {request.user.email} (role: {user_role}) accessed API {func.__name__}"
            )

            return func(request, *args, **kwargs)

        return wrapper

    return decorator
