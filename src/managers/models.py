"""
Manager Models Module - Модели данных для административной панели.

Этот модуль определяет базовые модели для управления платформой:
    - Feedback: Обратная связь от пользователей
    - SystemLog: Журнал системных событий
    - SystemSettings: Настройки платформы

Автор: Pyland Team
Дата: 2025
"""

from __future__ import annotations

from typing import Any

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Feedback(models.Model):
    """Модель для хранения обращений пользователей."""

    TOPIC_CHOICES = [
        ("courses", "Вопросы о курсах"),
        ("career", "Карьерная консультация"),
        ("technical", "Техническая поддержка"),
        ("partnership", "Сотрудничество"),
        ("other", "Другое"),
    ]

    first_name = models.CharField(max_length=50, verbose_name="Имя")
    phone_number = models.CharField(max_length=16, verbose_name="Номер телефона")
    email = models.CharField(max_length=200, verbose_name="Email адрес", db_index=True)
    topic = models.CharField(
        max_length=50, choices=TOPIC_CHOICES, blank=True, null=True, verbose_name="Тема обращения"
    )
    message = models.TextField(verbose_name="Сообщение")
    registered_at = models.DateTimeField(
        verbose_name="Дата регистрации", auto_now_add=True, db_index=True
    )

    is_processed = models.BooleanField(default=False, verbose_name="Обработано", db_index=True)
    processed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="processed_feedback",
        verbose_name="Обработал",
    )
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата обработки")
    admin_notes = models.TextField(blank=True, null=True, verbose_name="Заметки администратора")

    class Meta:
        db_table = "feedback"
        verbose_name = "Обратная связь"
        verbose_name_plural = "Обратная связь"
        ordering = ["-registered_at"]

    def __str__(self) -> str:
        return f"{self.first_name} ({self.email})"


class SystemLog(models.Model):
    """Модель для логирования системных событий."""

    LOG_LEVELS = [
        ("DEBUG", "Debug"),
        ("INFO", "Info"),
        ("WARNING", "Warning"),
        ("ERROR", "Error"),
        ("CRITICAL", "Critical"),
    ]

    ACTION_TYPES = [
        ("USER_LOGIN", "Вход пользователя"),
        ("USER_LOGOUT", "Выход пользователя"),
        ("USER_REGISTERED", "Регистрация пользователя"),
        ("USER_UPDATED", "Обновление пользователя"),
        ("USER_DELETED", "Удаление пользователя"),
        ("FEEDBACK_CREATED", "Создание обращения"),
        ("FEEDBACK_UPDATED", "Обновление обращения"),
        ("FEEDBACK_DELETED", "Удаление обращения"),
        ("SETTINGS_UPDATED", "Изменение настроек"),
        ("COURSE_CREATED", "Создание курса"),
        ("COURSE_UPDATED", "Обновление курса"),
        ("COURSE_DELETED", "Удаление курса"),
        ("PAYMENT_PROCESSED", "Обработка платежа"),
        ("ERROR_OCCURRED", "Ошибка"),
        ("SECURITY_EVENT", "Событие безопасности"),
    ]

    level = models.CharField(
        max_length=10, choices=LOG_LEVELS, default="INFO", verbose_name="Уровень", db_index=True
    )
    action_type = models.CharField(
        max_length=50, choices=ACTION_TYPES, verbose_name="Тип действия", db_index=True
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="system_logs",
        verbose_name="Пользователь",
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP адрес")
    user_agent = models.CharField(max_length=255, blank=True, verbose_name="User Agent")
    message = models.TextField(verbose_name="Сообщение")
    details = models.JSONField(default=dict, blank=True, verbose_name="Детали")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания", db_index=True
    )

    class Meta:
        db_table = "system_logs"
        verbose_name = "Системный лог"
        verbose_name_plural = "Системные логи"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.level} - {self.action_type}"


class SystemSettings(models.Model):
    """Модель для хранения настроек платформы."""

    VALUE_TYPES = [
        ("string", "String"),
        ("integer", "Integer"),
        ("boolean", "Boolean"),
        ("json", "JSON"),
    ]

    key = models.CharField(max_length=100, unique=True, verbose_name="Ключ", db_index=True)
    value = models.TextField(verbose_name="Значение")
    value_type = models.CharField(
        max_length=10, choices=VALUE_TYPES, default="string", verbose_name="Тип значения"
    )
    description = models.TextField(blank=True, verbose_name="Описание")
    is_public = models.BooleanField(default=False, verbose_name="Публичная")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_settings",
        verbose_name="Обновил",
    )

    class Meta:
        db_table = "system_settings"
        verbose_name = "Настройка системы"
        verbose_name_plural = "Настройки системы"
        ordering = ["key"]

    def __str__(self) -> str:
        return f"{self.key} ({self.value_type})"

    def get_typed_value(self) -> Any:
        """Возвращает значение с правильным типом."""
        import json

        if self.value_type == "integer":
            return int(self.value)
        elif self.value_type == "boolean":
            return self.value.lower() in ("true", "1", "yes")
        elif self.value_type == "json":
            return json.loads(self.value)
        else:
            return self.value


class ManagerNote(models.Model):
    """Модель для заметок менеджера о пользователе."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="manager_notes",
        verbose_name="Пользователь",
    )
    manager = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_notes",
        verbose_name="Менеджер",
    )
    note = models.TextField(verbose_name="Комментарий")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        db_table = "manager_notes"
        verbose_name = "Заметка менеджера"
        verbose_name_plural = "Заметки менеджера"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Заметка от {self.manager.email} о {self.user.email}"
