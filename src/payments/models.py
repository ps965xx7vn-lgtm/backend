"""
Payments Models Module - Модели данных для обработки платежей.

Этот модуль содержит модели для обработки платежей через Paddle Billing.

Модели:
    Payment - Основная модель платежа
        - Статусы: pending, processing, completed, failed, cancelled, refunded
        - Метод оплаты: paddle (Paddle Billing)
        - Валюты: USD, EUR, RUB, GEL
        - Связь с пользователем и курсом

Поля:
    - user: Пользователь, совершивший платеж
    - course: Курс, за который произведена оплата
    - amount: Сумма платежа
    - currency: Валюта (USD, EUR, RUB, GEL)
    - status: Текущий статус платежа
    - payment_method: Способ оплаты (paddle)
    - transaction_id: Уникальный ID транзакции от Paddle
    - payment_url: URL для перенаправления на страницу оплаты
    - extra_data: Дополнительные данные от Paddle (JSON)

Особенности:
    - UUID для первичных ключей
    - Трекинг времени создания и обновления
    - Хранение ответов от Paddle в JSON
    - Автоматическое логирование всех транзакций
    - Автоматическое зачисление на курс после оплаты

Автор: Pyland Team
Дата: 2026
"""

from __future__ import annotations

import logging
import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from courses.models import Course

logger = logging.getLogger(__name__)


class Payment(models.Model):
    """
    Модель платежа за курс.

    Поддерживает оплату через Paddle Billing.
    Хранит информацию о транзакции и статусе оплаты.
    """

    STATUS_CHOICES = [
        ("pending", "Ожидает оплаты"),
        ("processing", "Обрабатывается"),
        ("completed", "Успешно завершён"),
        ("failed", "Ошибка оплаты"),
        ("cancelled", "Отменён"),
        ("refunded", "Возвращён"),
    ]

    PAYMENT_METHOD_CHOICES = [
        ("paddle", "Paddle"),
    ]

    CURRENCY_CHOICES = [
        ("USD", "Доллар США"),
        ("EUR", "Евро"),
        ("RUB", "Российский рубль"),
        ("GEL", "Грузинский лари"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID",
        help_text="Уникальный идентификатор платежа",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Пользователь",
        help_text="Пользователь, совершающий покупку",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Курс",
        help_text="Приобретаемый курс",
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Сумма платежа",
        help_text="Стоимость курса в выбранной валюте",
    )
    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default="USD",
        verbose_name="Валюта",
        help_text="Валюта платежа",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name="Статус платежа",
        db_index=True,
        help_text="Текущий статус транзакции",
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        verbose_name="Метод оплаты",
        help_text="Выбранная платежная система",
    )
    transaction_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="ID транзакции",
        db_index=True,
        help_text="Уникальный идентификатор транзакции от платежной системы",
    )
    payment_url = models.URLField(
        blank=True,
        verbose_name="URL оплаты",
        help_text="Ссылка для перенаправления на страницу оплаты",
    )
    payment_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата оплаты",
        help_text="Время успешного завершения платежа",
    )
    extra_data = models.JSONField(
        blank=True,
        null=True,
        verbose_name="Дополнительные данные",
        help_text="Ответы и данные от платежного шлюза",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания", help_text="Время создания платежа"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Обновлено", help_text="Время последнего обновления"
    )

    class Meta:
        verbose_name = "Платёж"
        verbose_name_plural = "Платежи"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["transaction_id"]),
        ]

    def __str__(self) -> str:
        return (
            f"Платёж {self.id} - {self.get_status_display()} "
            f"({self.amount} {self.currency}) - {self.user.email}"
        )

    def mark_as_completed(self) -> None:
        """
        Отметить платеж как успешно завершённый.

        Обновляет статус, устанавливает дату оплаты,
        зачисляет студента на курс.
        """
        self.status = "completed"
        self.payment_date = timezone.now()
        self.save(update_fields=["status", "payment_date", "updated_at"])

        try:
            student = self.user.student
            if not self.course.student_enrollments.filter(id=student.id).exists():
                self.course.student_enrollments.add(student)
                logger.info(
                    f"Студент {self.user.email} зачислен на курс {self.course.name} "
                    f"после оплаты {self.id}"
                )
        except Exception as e:
            logger.error(f"Ошибка при зачислении студента на курс: {e}")

    def mark_as_failed(self, error_message: str | None = None) -> None:
        """
        Отметить платеж как неудавшийся.

        Args:
            error_message: Сообщение об ошибке для сохранения в extra_data
        """
        self.status = "failed"
        if error_message:
            if not self.extra_data:
                self.extra_data = {}
            self.extra_data["error"] = error_message
        self.save(update_fields=["status", "extra_data", "updated_at"])
        logger.warning(f"Платеж {self.id} отмечен как неудавшийся: {error_message}")

    def is_successful(self) -> bool:
        """
        Проверка, успешно ли завершён платеж.

        Returns:
            bool: True если статус "completed"
        """
        return bool(self.status == "completed")

    def can_be_refunded(self) -> bool:
        """
        Проверка, может ли платеж быть возвращён.

        Условия для возврата:
        - Статус должен быть "completed"
        - Платеж не должен быть уже возвращен

        Returns:
            bool: True если можно вернуть средства
        """
        return bool(self.status == "completed")

    def get_payment_method_display_name(self) -> str:
        """
        Получить читаемое название платежной системы.

        Returns:
            str: "Paddle Billing"
        """
        return "Paddle Billing"
