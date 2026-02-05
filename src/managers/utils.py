"""
Manager Utils Module - Вспомогательные функции для менеджеров.

Этот модуль содержит утилиты для:
    - Получения IP адреса из запроса
    - Создания системных логов
    - Работы с User-Agent

Автор: Pyland Team
Дата: 2026
"""

from __future__ import annotations

import logging
from typing import Any

from django.contrib.auth import get_user_model
from django.http import HttpRequest

from managers.models import SystemLog

logger = logging.getLogger(__name__)

User = get_user_model()


def get_client_ip(request: HttpRequest) -> str | None:
    """
    Получает IP адрес клиента из HTTP запроса.

    Проверяет заголовки в порядке приоритета:
        1. X-Forwarded-For (прокси/балансировщики)
        2. X-Real-IP (nginx)
        3. REMOTE_ADDR (прямое соединение)

    Args:
        request: HTTP запрос

    Returns:
        str | None: IP адрес клиента или None если не найден
    """
    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        # X-Forwarded-For может содержать несколько IP через запятую
        # Берем первый (реальный IP клиента)
        ip = x_forwarded_for.split(",")[0].strip()
        return ip

    x_real_ip = request.headers.get("x-real-ip")
    if x_real_ip:
        return x_real_ip.strip()

    remote_addr = request.META.get("REMOTE_ADDR")
    return remote_addr


def get_user_agent(request: HttpRequest) -> str:
    """
    Получает User-Agent из HTTP запроса.

    Args:
        request: HTTP запрос

    Returns:
        str: User-Agent строка или пустая строка
    """
    return request.headers.get("user-agent", "")[:255]  # Ограничиваем до 255 символов


def create_system_log(
    level: str,
    action_type: str,
    message: str,
    request: HttpRequest | None = None,
    user: User | None = None,
    details: dict[str, Any] | None = None,
) -> SystemLog:
    """
    Создает запись в системном логе с автоматическим извлечением IP и User-Agent.

    Args:
        level: Уровень лога (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        action_type: Тип действия (USER_LOGIN, FEEDBACK_CREATED, и т.д.)
        message: Текст сообщения
        request: HTTP запрос (опционально, для извлечения IP и User-Agent)
        user: Пользователь (опционально, будет взят из request.user если не указан)
        details: Дополнительные детали в формате JSON (опционально)

    Returns:
        SystemLog: Созданная запись лога

    Example:
        >>> create_system_log(
        ...     level="INFO",
        ...     action_type="USER_LOGIN",
        ...     message="Пользователь вошел в систему",
        ...     request=request,
        ... )
    """
    log_data = {
        "level": level,
        "action_type": action_type,
        "message": message,
        "details": details or {},
    }

    # Если передан request, извлекаем IP и User-Agent
    if request:
        log_data["ip_address"] = get_client_ip(request)
        log_data["user_agent"] = get_user_agent(request)

        # Если user не указан, берем из request
        if user is None and request.user.is_authenticated:
            log_data["user"] = request.user
    elif user:
        log_data["user"] = user

    try:
        log_entry = SystemLog.objects.create(**log_data)
        logger.debug(f"System log created: {level} - {action_type}")
        return log_entry
    except Exception as e:
        logger.error(f"Failed to create system log: {e}")
        raise


def log_feedback_action(
    action_type: str,
    feedback_id: int,
    message: str,
    request: HttpRequest,
    details: dict[str, Any] | None = None,
) -> SystemLog:
    """
    Создает лог для действий с обратной связью.

    Args:
        action_type: Тип действия (FEEDBACK_CREATED, FEEDBACK_UPDATED, FEEDBACK_DELETED)
        feedback_id: ID обращения
        message: Текст сообщения
        request: HTTP запрос
        details: Дополнительные детали

    Returns:
        SystemLog: Созданная запись лога
    """
    log_details = details or {}
    log_details["feedback_id"] = feedback_id

    # Определяем уровень лога по типу действия
    level = "WARNING" if action_type == "FEEDBACK_DELETED" else "INFO"

    return create_system_log(
        level=level,
        action_type=action_type,
        message=message,
        request=request,
        details=log_details,
    )


def log_user_action(
    action_type: str,
    user_id: int,
    message: str,
    request: HttpRequest,
    level: str = "INFO",
    details: dict[str, Any] | None = None,
) -> SystemLog:
    """
    Создает лог для действий пользователя.

    Args:
        action_type: Тип действия (USER_LOGIN, USER_LOGOUT, и т.д.)
        user_id: ID пользователя
        message: Текст сообщения
        request: HTTP запрос
        level: Уровень лога (по умолчанию INFO)
        details: Дополнительные детали

    Returns:
        SystemLog: Созданная запись лога
    """
    log_details = details or {}
    log_details["user_id"] = user_id

    return create_system_log(
        level=level,
        action_type=action_type,
        message=message,
        request=request,
        details=log_details,
    )
