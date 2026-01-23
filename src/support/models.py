"""
Support Models Module - Модели данных для системы техподдержки.

Этот модуль содержит модели для работы с тикетами поддержки:

Модели:
    Ticket - Основная модель тикета поддержки
        - user: Пользователь, создавший тикет
        - subject: Тема обращения
        - message: Сообщение
        - status: Статус (open, in_progress, closed)
        - priority: Приоритет (low, medium, high)
        - assigned_to: Назначенный сотрудник support

Статусы:
    - open: Новый, ожидает обработки
    - in_progress: В работе
    - closed: Закрыт, решен

Приоритеты:
    - low: Низкий (общие вопросы)
    - medium: Средний (по умолчанию)
    - high: Высокий (технические проблемы)

Планируемые расширения:
    TicketMessage - Сообщения в тикете (история переписки)
    TicketAttachment - Прикрепленные файлы
    TicketCategory - Категории тикетов

Особенности:
    - Автоматическое назначение или ручное
    - Трекинг времени создания и обновления
    - Email уведомления при изменении статуса
    - Приоритетная обработка по уровню приоритета

Автор: Pyland Team
Дата: 2025
"""

from django.conf import settings
from django.db import models


class Ticket(models.Model):
    STATUS_CHOICES = [
        ("open", "Открыт"),
        ("in_progress", "В работе"),
        ("closed", "Закрыт"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tickets",
        verbose_name="Пользователь",
    )
    subject = models.CharField(max_length=255, verbose_name="Тема")
    message = models.TextField(verbose_name="Сообщение")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="open", verbose_name="Статус"
    )
    priority = models.CharField(
        max_length=20,
        choices=[("low", "Низкий"), ("medium", "Средний"), ("high", "Высокий")],
        default="medium",
        verbose_name="Приоритет",
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_tickets",
        verbose_name="Ответственный",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Тикет поддержки"
        verbose_name_plural = "Тикеты поддержки"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Тикет #{self.id} — {self.subject} ({self.get_status_display()})"
