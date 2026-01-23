"""
Payments Models Module - Модели данных для обработки платежей.

Этот модуль содержит модели для обработки платежей:

Модели:
    Payment - Основная модель платежа
        - Статусы: pending, completed, failed, refunded
        - Методы оплаты: card, paypal, stripe, manual
        - Связь с пользователем и курсом

Поля:
    - user: Пользователь, совершивший платеж
    - course: Курс, за который произведена оплата
    - amount: Сумма платежа
    - currency: Валюта (GEL по умолчанию)
    - status: Текущий статус платежа
    - payment_method: Способ оплаты
    - transaction_id: Уникальный ID транзакции
    - extra_data: Дополнительные данные (JSON)

Особенности:
    - UUID для первичных ключей
    - Трекинг времени создания и обновления
    - Хранение ответов платежных шлюзов в JSON
    - Логирование всех транзакций

Автор: Pyland Team
Дата: 2025
"""

import uuid

from django.conf import settings
from django.db import models

from courses.models import Course


class Payment(models.Model):
    STATUS_CHOICES = [
        ("pending", "Ожидает"),
        ("completed", "Завершён"),
        ("failed", "Неуспешен"),
        ("refunded", "Возвращён"),
    ]

    PAYMENT_METHOD_CHOICES = [
        ("card", "Банковская карта"),
        ("paypal", "PayPal"),
        ("stripe", "Stripe"),
        ("manual", "Ручная оплата"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Пользователь",
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="payments", verbose_name="Курс"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Сумма платежа")
    currency = models.CharField(max_length=10, default="USD", verbose_name="Валюта")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending", verbose_name="Статус платежа"
    )
    transaction_id = models.CharField(max_length=100, blank=True, verbose_name="ID транзакции")
    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_METHOD_CHOICES, verbose_name="Метод оплаты"
    )
    payment_date = models.DateTimeField(null=True, blank=True, verbose_name="Дата платежа")
    extra_data = models.JSONField(
        blank=True, null=True, verbose_name="Дополнительно"
    )  # для хранения ответа от платёжного шлюза
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Платёж"
        verbose_name_plural = "Платежи"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Платёж {self.id} ({self.get_status_display()}) для пользователя {self.user.email}"
