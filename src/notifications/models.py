"""
Notifications Models Module - Модели данных для системы уведомлений.

Этот модуль содержит модели для управления уведомлениями:

Модели:
    Subscription - Email-подписки на рассылку
        - email: Уникальный email адрес
        - created_at: Дата подписки
        - is_active: Статус подписки

Планируемые модели:
    NotificationSettings - Настройки уведомлений пользователя
        - user: Связь с пользователем
        - email_enabled: Включены ли email уведомления
        - sms_enabled: Включены ли SMS уведомления
        - telegram_enabled: Включены ли Telegram уведомления
        - notification_types: Типы уведомлений (JSON)

    NotificationLog - Журнал отправленных уведомлений
        - История отправки
        - Статус доставки

Особенности:
    - Проверка уникальности email
    - Автоматическая дата подписки
    - Возможность отключения подписки
    - Интеграция с Celery для асинхронной отправки

Автор: Pyland Team
Дата: 2025
"""

from django.db import models


class Subscription(models.Model):
    """
    Email-подписка для уведомлений и рассылок.
    """

    email = models.EmailField(unique=True, verbose_name="Email")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата подписки")
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def __str__(self):
        return self.email
