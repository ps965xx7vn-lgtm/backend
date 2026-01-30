"""
Notifications Models Module - Централизованная система подписок и уведомлений.

Этот модуль содержит модели для управления всеми типами подписок на платформе:

Модели:
    Subscription - Универсальная модель подписок с типизацией
        - user: Связь с пользователем (опционально для анонимных)
        - email: Уникальный email адрес (unique вместе с subscription_type)
        - subscription_type: Тип подписки (соответствует настройкам Student)
        - name: Имя подписчика (опционально)
        - is_active: Статус подписки
        - preferences: JSON с настройками (source, частота, категории, etc.)

Архитектурное решение:
    Централизованное хранение ВСЕХ подписок платформы в одном месте.
    Типы подписок ПОЛНОСТЬЮ СООТВЕТСТВУЮТ настройкам Student модели:
    - email_notifications - Все email уведомления
    - course_updates - Обновления курсов
    - lesson_reminders - Напоминания о уроках
    - achievement_alerts - Уведомления о достижениях
    - weekly_summary - Еженедельная сводка
    - marketing_emails - Маркетинговые письма

Преимущества:
    ✅ Единая точка управления всеми подписками
    ✅ Типы подписок совпадают с User preferences
    ✅ Нет дублирования кода между приложениями
    ✅ Легко добавлять новые типы подписок
    ✅ Централизованная аналитика
    ✅ Unified unsubscribe mechanism

Автор: Pyland Team
Дата: 2026
"""

from __future__ import annotations

from typing import Any

from django.db import models


class Subscription(models.Model):
    """
    Универсальная модель подписок на различные типы контента.

    Поддерживает как анонимные подписки (только email), так и подписки
    зарегистрированных пользователей (с привязкой к User).

    Типы подписок определяются через SUBSCRIPTION_TYPE_CHOICES.
    Дополнительные настройки хранятся в JSON поле preferences.
    """

    SUBSCRIPTION_TYPE_CHOICES = [
        ("email_notifications", "📧 Все email уведомления"),
        ("course_updates", "📚 Обновления курсов"),
        ("lesson_reminders", "⏰ Напоминания о уроках"),
        ("achievement_alerts", "🏆 Уведомления о достижениях"),
        ("weekly_summary", "📊 Еженедельная сводка"),
        ("marketing_emails", "🎁 Маркетинговые письма"),
    ]

    user = models.ForeignKey(
        "authentication.User",
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="Пользователь",
        null=True,
        blank=True,
        help_text="Связь с пользователем (null для анонимных подписок)",
    )

    email = models.EmailField(
        verbose_name="Email", help_text="Email адрес для отправки уведомлений"
    )

    subscription_type = models.CharField(
        max_length=50,
        choices=SUBSCRIPTION_TYPE_CHOICES,
        default="email_notifications",
        verbose_name="Тип подписки",
        help_text="Категория уведомлений (соответствует настройкам студента)",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Активна",
        help_text="Активна ли подписка (для отписки без удаления)",
    )

    preferences = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Настройки",
        help_text="Дополнительные настройки подписки (частота, категории, etc.)",
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата подписки")

    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлена")

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        ordering = ["-created_at"]
        unique_together = [("email", "subscription_type")]
        indexes = [
            models.Index(fields=["email", "subscription_type"]),
            models.Index(fields=["user", "is_active"]),
            models.Index(fields=["subscription_type", "is_active"]),
        ]

    def __str__(self) -> str:
        """Строковое представление подписки."""
        type_display = dict(self.SUBSCRIPTION_TYPE_CHOICES).get(
            self.subscription_type, self.subscription_type
        )
        status = "✅" if self.is_active else "❌"
        return f"{status} {self.email} → {type_display}"

    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Сохранение с автоматической привязкой к User по email.

        Если user=None, но email совпадает с существующим пользователем,
        автоматически создаем связь.
        """
        if not self.user:
            try:
                from authentication.models import User

                user = User.objects.filter(email=self.email).first()
                if user:
                    self.user = user
            except Exception:
                pass  # Игнорируем ошибки при попытке найти пользователя

        super().save(*args, **kwargs)

    @classmethod
    def subscribe(
        cls,
        email: str,
        subscription_type: str = "email_notifications",
        user=None,
        preferences: dict = None,
    ) -> tuple[Subscription, bool]:
        """
        Удобный метод для создания подписки.

        Args:
            email: Email адрес
            subscription_type: Тип подписки (по умолчанию 'email_notifications')
            user: Пользователь (опционально)
            preferences: Дополнительные настройки

        Returns:
            tuple: (subscription, created) - объект подписки и флаг создания
        """
        defaults = {"user": user, "is_active": True, "preferences": preferences or {}}

        subscription, created = cls.objects.get_or_create(
            email=email, subscription_type=subscription_type, defaults=defaults
        )

        # Реактивация если подписка была неактивна
        if not created and not subscription.is_active:
            subscription.is_active = True
            subscription.save()
            created = True  # Считаем как новую подписку

        return subscription, created

    @classmethod
    def unsubscribe(cls, email: str, subscription_type: str = None) -> int:
        """
        Отписка от рассылки(ок).

        Args:
            email: Email адрес
            subscription_type: Тип подписки (None = отписка от всех)

        Returns:
            int: Количество деактивированных подписок
        """
        queryset = cls.objects.filter(email=email, is_active=True)

        if subscription_type:
            queryset = queryset.filter(subscription_type=subscription_type)

        return queryset.update(is_active=False)
