"""
Manager API Schemas Module - Схемы для административного API.

Pydantic схемы для валидации и сериализации данных Manager API.
Все эндпоинты Manager API требуют прав администратора (staff_member_required).

Схемы для обратной связи:
    - FeedbackOut: Вывод информации об обратной связи
    - FeedbackListOut: Пагинированный список обратной связи
    - FeedbackStatsOut: Статистика по обратной связи
    - FeedbackDeleteResponse: Ответ при удалении

Схемы для системных логов:
    - SystemLogOut: Информация о системном логе
    - SystemLogListOut: Список логов с пагинацией
    - SystemLogStatsOut: Статистика по логам

Схемы для управления настройками:
    - SettingOut: Информация о настройке
    - SettingUpdateIn: Обновление настройки
    - SettingsListOut: Список всех настроек

Схемы для системной статистики:
    - SystemStatsOut: Полная системная статистика
    - UserStatsOut: Статистика по пользователям
    - ContentStatsOut: Статистика по контенту

Особенности:
    - Все схемы с полными type hints
    - from_attributes = True для ORM моделей
    - Примеры в json_schema_extra
    - Русские докстринги для всех классов

Автор: Pyland Team
Дата: 2025
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

# ============================================================================
# FEEDBACK SCHEMAS - Схемы для управления обратной связью
# ============================================================================


class FeedbackOut(BaseModel):
    """
    Схема для вывода информации об обратной связи.

    Используется в админском API для просмотра деталей обратной связи.

    Attributes:
        id: Уникальный идентификатор
        first_name: Имя отправителя
        phone_number: Номер телефона
        email: Email адрес
        message: Текст сообщения
        registered_at: Дата и время создания

    Example:
        >>> feedback = FeedbackOut(
        >>>     id=1,
        >>>     first_name="Иван",
        >>>     phone_number="+79991234567",
        >>>     email="ivan@example.com",
        >>>     message="Интересуюсь курсами",
        >>>     registered_at=datetime.now()
        >>> )
    """

    id: int = Field(..., description="Уникальный идентификатор")
    first_name: str = Field(..., description="Имя отправителя")
    phone_number: str = Field(..., description="Номер телефона")
    email: str = Field(..., description="Email адрес")
    message: str = Field(..., description="Текст сообщения")
    registered_at: datetime = Field(..., description="Дата создания")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "first_name": "Иван",
                "phone_number": "+79991234567",
                "email": "ivan@example.com",
                "message": "Хочу узнать о курсах Python",
                "registered_at": "2025-11-10T10:00:00",
            }
        }


class FeedbackListOut(BaseModel):
    """
    Схема для пагинированного списка обратной связи.

    Используется для вывода списка всех сообщений обратной связи
    с поддержкой пагинации и поиска.

    Attributes:
        count: Общее количество записей
        results: Список объектов FeedbackOut
        page: Текущая страница
        page_size: Количество элементов на странице
        total_pages: Общее количество страниц
    """

    count: int = Field(..., description="Общее количество записей")
    results: list[FeedbackOut] = Field(..., description="Список обратной связи")
    page: int = Field(..., description="Текущая страница")
    page_size: int = Field(..., description="Элементов на странице")
    total_pages: int = Field(..., description="Всего страниц")


class FeedbackStatsOut(BaseModel):
    """
    Схема для статистики по обратной связи.

    Предоставляет агрегированную информацию о сообщениях обратной связи
    за различные периоды времени.

    Attributes:
        total_feedback: Всего сообщений
        today_feedback: Сообщений сегодня
        this_week_feedback: Сообщений за неделю
        this_month_feedback: Сообщений за месяц
        average_per_day: Среднее количество в день
        most_active_day: Самый активный день (или None)
        recent_feedback: Последние N сообщений
    """

    total_feedback: int = Field(..., description="Всего сообщений")
    today_feedback: int = Field(..., description="Сообщений сегодня")
    this_week_feedback: int = Field(..., description="За неделю")
    this_month_feedback: int = Field(..., description="За месяц")
    average_per_day: float = Field(..., description="Среднее в день")
    most_active_day: Optional[str] = Field(None, description="Самый активный день")
    recent_feedback: list[FeedbackOut] = Field(..., description="Последние сообщения")


class FeedbackDeleteResponse(BaseModel):
    """
    Схема ответа при удалении обратной связи.

    Возвращает статус операции удаления.

    Attributes:
        success: Успешно ли выполнена операция
        message: Сообщение о результате
        deleted_id: ID удаленной записи (или None при ошибке)
    """

    success: bool = Field(..., description="Статус операции")
    message: str = Field(..., description="Сообщение о результате")
    deleted_id: Optional[int] = Field(None, description="ID удаленной записи")


# ============================================================================
# SYSTEM LOGS SCHEMAS - Схемы для системных логов
# ============================================================================


class SystemLogOut(BaseModel):
    """
    Схема для вывода системного лога.

    Используется для просмотра истории действий администраторов
    и системных событий.

    Attributes:
        id: Уникальный идентификатор
        user_email: Email пользователя (или None для системных событий)
        action: Тип действия (CREATE, UPDATE, DELETE и т.д.)
        model_name: Название модели
        object_id: ID объекта (или None)
        details: Дополнительные детали в JSON
        ip_address: IP адрес пользователя
        timestamp: Дата и время события
    """

    id: int = Field(..., description="ID лога")
    user_email: Optional[str] = Field(None, description="Email пользователя")
    action: str = Field(..., description="Тип действия")
    model_name: str = Field(..., description="Название модели")
    object_id: Optional[int] = Field(None, description="ID объекта")
    details: Optional[dict] = Field(None, description="Детали в JSON")
    ip_address: Optional[str] = Field(None, description="IP адрес")
    timestamp: datetime = Field(..., description="Время события")

    class Config:
        from_attributes = True


class SystemLogListOut(BaseModel):
    """
    Схема для пагинированного списка системных логов.

    Attributes:
        count: Общее количество логов
        results: Список логов
        page: Текущая страница
        page_size: Элементов на странице
        total_pages: Всего страниц
    """

    count: int = Field(..., description="Общее количество")
    results: list[SystemLogOut] = Field(..., description="Список логов")
    page: int = Field(..., description="Текущая страница")
    page_size: int = Field(..., description="Элементов на странице")
    total_pages: int = Field(..., description="Всего страниц")


class SystemLogStatsOut(BaseModel):
    """
    Схема для статистики системных логов.

    Attributes:
        total_logs: Всего логов
        today_logs: Логов сегодня
        by_action: Распределение по типам действий
        by_model: Распределение по моделям
        top_users: Топ пользователей по активности
    """

    total_logs: int = Field(..., description="Всего логов")
    today_logs: int = Field(..., description="Логов сегодня")
    by_action: dict[str, int] = Field(..., description="По типам действий")
    by_model: dict[str, int] = Field(..., description="По моделям")
    top_users: list[dict] = Field(..., description="Топ пользователей")


# ============================================================================
# SETTINGS SCHEMAS - Схемы для системных настроек
# ============================================================================


class SettingOut(BaseModel):
    """
    Схема для вывода системной настройки.

    Attributes:
        id: ID настройки
        key: Ключ настройки (уникальный)
        value: Значение
        description: Описание назначения
        value_type: Тип значения (string, int, bool, json)
        is_active: Активна ли настройка
        updated_at: Дата последнего обновления
    """

    id: int = Field(..., description="ID настройки")
    key: str = Field(..., description="Ключ настройки")
    value: str = Field(..., description="Значение")
    description: Optional[str] = Field(None, description="Описание")
    value_type: str = Field(..., description="Тип значения")
    is_active: bool = Field(..., description="Активна ли")
    updated_at: datetime = Field(..., description="Дата обновления")

    class Config:
        from_attributes = True


class SettingUpdateIn(BaseModel):
    """
    Схема для обновления настройки.

    Attributes:
        value: Новое значение
        is_active: Активировать/деактивировать
    """

    value: Optional[str] = Field(None, description="Новое значение")
    is_active: Optional[bool] = Field(None, description="Активность")


class SettingsListOut(BaseModel):
    """
    Схема для списка всех настроек.

    Attributes:
        count: Количество настроек
        results: Список настроек
    """

    count: int = Field(..., description="Количество")
    results: list[SettingOut] = Field(..., description="Список настроек")


# ============================================================================
# SYSTEM STATISTICS SCHEMAS - Схемы для системной статистики
# ============================================================================


class UserStatsOut(BaseModel):
    """
    Схема для статистики пользователей.

    Attributes:
        total_users: Всего пользователей
        active_users: Активных пользователей
        new_today: Новых сегодня
        new_this_week: Новых за неделю
        new_this_month: Новых за месяц
        by_role: Распределение по ролям
    """

    total_users: int = Field(..., description="Всего")
    active_users: int = Field(..., description="Активных")
    new_today: int = Field(..., description="Новых сегодня")
    new_this_week: int = Field(..., description="Новых за неделю")
    new_this_month: int = Field(..., description="Новых за месяц")
    by_role: dict[str, int] = Field(..., description="По ролям")


class ContentStatsOut(BaseModel):
    """
    Схема для статистики контента.

    Attributes:
        total_courses: Всего курсов
        total_lessons: Всего уроков
        total_articles: Всего статей
        total_comments: Всего комментариев
    """

    total_courses: int = Field(..., description="Курсов")
    total_lessons: int = Field(..., description="Уроков")
    total_articles: int = Field(..., description="Статей")
    total_comments: int = Field(..., description="Комментариев")


class SystemStatsOut(BaseModel):
    """
    Схема для полной системной статистики.

    Объединяет все виды статистики платформы.

    Attributes:
        users: Статистика пользователей
        content: Статистика контента
        feedback: Статистика обратной связи
        system_load: Нагрузка на систему (опционально)
        cache_status: Статус кеша (опционально)
    """

    users: UserStatsOut = Field(..., description="Статистика пользователей")
    content: ContentStatsOut = Field(..., description="Статистика контента")
    feedback: FeedbackStatsOut = Field(..., description="Статистика обратной связи")
    system_load: Optional[dict] = Field(None, description="Нагрузка системы")
    cache_status: Optional[dict] = Field(None, description="Статус кеша")


# ============================================================================
# ERROR SCHEMAS - Схемы для ошибок
# ============================================================================


class ErrorResponse(BaseModel):
    """
    Стандартная схема для ошибок API.

    Используется для единообразного возврата ошибок.

    Attributes:
        error: Краткое описание ошибки
        detail: Детальное описание (опционально)
        field: Поле с ошибкой валидации (опционально)
    """

    error: str = Field(..., description="Описание ошибки")
    detail: Optional[str] = Field(None, description="Детали ошибки")
    field: Optional[str] = Field(None, description="Поле с ошибкой")
