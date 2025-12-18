"""
Reviewers Models Module - Модели для системы проверки работ студентов.

ВАЖНО:
    - ReviewerProfile была перемещена в authentication.models как Reviewer
    - Review: Рецензии на работы студентов
    - StudentImprovement: Улучшения для работ студентов
    - ReviewerNotification: Уведомления для ревьюеров

Используйте:
    from authentication.models import Reviewer

Автор: Pyland Team
Дата: 2025
"""

from __future__ import annotations

import logging
import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

logger = logging.getLogger(__name__)

# ReviewerProfile теперь находится в authentication.models как Reviewer
# Это сделано для централизации управления пользователями и ролями

# LessonSubmission теперь импортируется из courses.models
# Это позволяет использовать единую модель для всей системы


class Review(models.Model):
    """
    Рецензия на работу студента, оставленная проверяющим.

    Attributes:
        id: UUID первичный ключ
        lesson_submission: Связь с работой студента
        reviewer: Проверяющий (ReviewerProfile)
        status: Статус проверки (approved/needs_work/rejected)
        comments: Общие комментарии к работе
        rating: Оценка работы (1-5)
        time_spent: Время затраченное на проверку (минуты)
        reviewed_at: Время проверки
    """

    STATUS_CHOICES = [
        ("approved", "Принята"),
        ("needs_work", "Требуются доработки"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lesson_submission = models.OneToOneField(
        "LessonSubmission", on_delete=models.CASCADE, related_name="review"
    )
    reviewer = models.ForeignKey(
        "authentication.Reviewer",
        on_delete=models.SET_NULL,
        null=True,
        related_name="reviews",
        verbose_name="Проверяющий",
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="approved", verbose_name="Статус проверки"
    )
    comments = models.TextField(
        verbose_name="Комментарии проверяющего",
        help_text="Общие комментарии и рекомендации по работе",
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        verbose_name="Оценка работы",
        help_text="Оценка от 1 до 5",
    )
    time_spent = models.PositiveIntegerField(
        default=0,
        verbose_name="Время проверки (мин)",
        help_text="Примерное время затраченное на проверку",
    )
    reviewed_at = models.DateTimeField(
        default=timezone.now,  # Изменено с auto_now_add для возможности ручного обновления
        verbose_name="Дата проверки",
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Последнее обновление")

    class Meta:
        verbose_name = "Рецензия"
        verbose_name_plural = "Рецензии"
        ordering = ["-reviewed_at"]
        indexes = [
            models.Index(fields=["reviewer", "-reviewed_at"]),
            models.Index(fields=["lesson_submission"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        reviewer_email = self.reviewer.user.email if self.reviewer else "Не указан"
        return f"Рецензия для {self.lesson_submission.lesson.name} — Проверяющий: {reviewer_email}"

    def save(self, *args, **kwargs):
        """При сохранении обновляем статистику ревьюера."""
        is_new = self.pk is None
        super().save(*args, **kwargs)

        # Обновляем статистику ревьюера при новой проверке
        if is_new and self.reviewer:
            self.reviewer.update_statistics()


class StudentImprovement(models.Model):
    """
    Конкретное улучшение/исправление для работы студента.

    Ревьюер может указать несколько точечных улучшений,
    которые студент должен внести в свою работу.

    ВАЖНО: Улучшения привязаны к LessonSubmission (не к Review),
    чтобы сохранять историю всех улучшений даже при повторных проверках.

    Attributes:
        id: UUID первичный ключ
        lesson_submission: Связь с работой студента (основная связь)
        review: Связь с рецензией (может быть NULL если Review удален)
        improvement_number: Порядковый номер улучшения
        title: Название улучшения
        improvement_text: Описание улучшения
        priority: Приоритет улучшения (high/medium/low)
        is_completed: Выполнено ли улучшение студентом
        completed_at: Когда студент отметил как выполненное
        created_at: Когда улучшение было создано
    """

    PRIORITY_CHOICES = [
        ("high", "Высокий"),
        ("medium", "Средний"),
        ("low", "Низкий"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Основная связь с работой студента (сохраняется при повторных проверках)
    lesson_submission = models.ForeignKey(
        "LessonSubmission",  # Строка т.к. модель определена ниже в этом же файле
        on_delete=models.CASCADE,
        related_name="improvements",  # Изменено с improvement_steps_list
        verbose_name="Работа студента",
        null=True,  # Временно nullable для миграции
        blank=True,
    )

    # Связь с конкретной рецензией (может быть NULL если Review удален)
    review = models.ForeignKey(
        Review,
        on_delete=models.SET_NULL,
        related_name="improvements",
        null=True,
        blank=True,
        verbose_name="Рецензия",
    )

    improvement_number = models.PositiveIntegerField(default=1, verbose_name="Номер улучшения")
    title = models.CharField(
        max_length=200,
        verbose_name="Название улучшения",
        help_text="Краткое название шага улучшения",
        blank=True,
        default="",
    )
    improvement_text = models.TextField(
        verbose_name="Описание улучшения", help_text="Что именно нужно исправить или улучшить"
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default="medium",
        verbose_name="Приоритет",
        help_text="Важность данного улучшения",
    )
    is_completed = models.BooleanField(
        default=False, verbose_name="Выполнено", help_text="Отметка студента о выполнении"
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата выполнения",
        help_text="Когда студент отметил как выполненное",
    )
    created_at = models.DateTimeField(
        verbose_name="Дата создания",
        default=timezone.now,  # Автоматически устанавливается при создании
    )

    class Meta:
        ordering = ["improvement_number"]
        verbose_name = "Улучшение"
        verbose_name_plural = "Улучшения"
        indexes = [
            models.Index(fields=["lesson_submission", "improvement_number"]),
            models.Index(fields=["review"]),
            models.Index(fields=["is_completed"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        status = "✓" if self.is_completed else "○"
        return f"{status} Улучшение #{self.improvement_number} для {self.review.lesson_submission.lesson.name}"

    def save(self, *args, **kwargs):
        """
        Автоматическая нумерация улучшений по рецензии.
        """
        if not self.pk and not self.improvement_number:
            last = (
                StudentImprovement.objects.filter(review=self.review)
                .order_by("-improvement_number")
                .first()
            )
            self.improvement_number = last.improvement_number + 1 if last else 1

        # Обновляем completed_at при отметке как выполненное
        if self.is_completed and not self.completed_at:
            self.completed_at = timezone.now()

        super().save(*args, **kwargs)

    def mark_completed(self) -> None:
        """Отметить улучшение как выполненное."""
        self.is_completed = True
        self.completed_at = timezone.now()
        self.save(update_fields=["is_completed", "completed_at"])


class ReviewerNotification(models.Model):
    """
    Уведомления для ревьюеров о новых работах, ответах студентов и т.д.

    Attributes:
        id: UUID первичный ключ
        reviewer: Получатель уведомления
        notification_type: Тип уведомления
        title: Заголовок
        message: Текст сообщения
        link: Ссылка на связанный объект
        is_read: Прочитано ли
        created_at: Время создания
    """

    NOTIFICATION_TYPES = [
        ("new_submission", "Новая работа на проверку"),
        ("resubmission", "Повторная отправка работы"),
        ("student_question", "Вопрос от студента"),
        ("system", "Системное уведомление"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reviewer = models.ForeignKey(
        "authentication.Reviewer", on_delete=models.CASCADE, related_name="notifications"
    )
    notification_type = models.CharField(
        max_length=20, choices=NOTIFICATION_TYPES, verbose_name="Тип уведомления"
    )
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    message = models.TextField(verbose_name="Сообщение")
    link = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Ссылка",
        help_text="URL для перехода к связанному объекту",
    )
    is_read = models.BooleanField(default=False, verbose_name="Прочитано")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Уведомление ревьюера"
        verbose_name_plural = "Уведомления ревьюеров"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["reviewer", "-created_at"]),
            models.Index(fields=["is_read"]),
        ]

    def __str__(self) -> str:
        status = "📭" if self.is_read else "📬"
        return f"{status} {self.title} — {self.reviewer.user.email}"

    def mark_as_read(self) -> None:
        """Отметить уведомление как прочитанное."""
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=["is_read"])


class LessonSubmission(models.Model):
    """
    Работа студента для урока (отправка ссылки на проверку).

    Статусы:
    - pending: Ожидает проверки (только что отправлено)
    - changes_requested: Требуются доработки
    - approved: Одобрено ментором
    """

    STATUS_CHOICES = [
        ("pending", "Ожидает проверки"),
        ("changes_requested", "Требуются доработки"),
        ("approved", "Одобрено"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        "authentication.Student",
        on_delete=models.CASCADE,
        related_name="lesson_submissions",
        verbose_name="Студент",
    )
    lesson = models.ForeignKey(
        "courses.Lesson",
        on_delete=models.CASCADE,
        related_name="submissions",
        verbose_name="Урок",
    )
    lesson_url = models.URLField(verbose_name="Ссылка на работу")

    # Статус проверки
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name="Статус",
        db_index=True,
    )

    # Ментор и комментарий
    mentor = models.ForeignKey(
        "authentication.Student",
        on_delete=models.SET_NULL,
        related_name="reviewed_submissions",
        verbose_name="Ментор",
        null=True,
        blank=True,
    )
    mentor_comment = models.TextField(
        blank=True,
        verbose_name="Комментарий ментора",
        help_text="Комментарий для студента о необходимых правках (поддерживает Markdown)",
    )

    # Даты
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата отправки")
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата проверки",
        help_text="Когда ментор проверил работу",
    )

    # Количество попыток
    revision_count = models.IntegerField(
        default=0, verbose_name="Попытка", help_text="Сколько раз работа отправлялась на доработку"
    )

    class Meta:
        verbose_name = "Работа студента"
        verbose_name_plural = "Работы студентов"
        unique_together = ("student", "lesson")
        indexes = [
            models.Index(fields=["status", "-submitted_at"]),
            models.Index(fields=["mentor", "status"]),
        ]
        db_table = "courses_lessonsubmission"  # Сохраняем старую таблицу

    def __str__(self):
        return f"{self.student} — {self.lesson.name} ({self.get_status_display()})"

    def can_resubmit(self):
        """Можно ли повторно отправить работу (только если требуются правки)"""
        return self.status == "changes_requested"

    def is_approved(self):
        """Одобрена ли работа"""
        return self.status == "approved"

    def get_status_badge_color(self):
        """Возвращает цвет бейджа для статуса"""
        colors = {
            "pending": "warning",
            "changes_requested": "danger",
            "approved": "success",
        }
        return colors.get(self.status, "secondary")

    def get_status_icon(self):
        """Возвращает иконку для статуса"""
        icons = {
            "pending": "⏳",
            "changes_requested": "✏️",
            "approved": "✅",
        }
        return icons.get(self.status, "❓")


class ImprovementStep(models.Model):
    """
    Шаги доработки, которые ментор создает для студента.
    Это отдельные шаги с инструкциями, не связанные с шагами урока.
    """

    submission = models.ForeignKey(
        LessonSubmission,
        on_delete=models.CASCADE,
        related_name="improvement_steps_list",
        verbose_name="Работа студента",
    )
    title = models.CharField(
        max_length=300,
        verbose_name="Название шага",
        help_text="Краткое описание того, что нужно исправить",
    )
    description = models.TextField(
        verbose_name="Описание",
        help_text="Подробная инструкция для студента (поддерживает Markdown)",
    )
    order = models.IntegerField(
        default=0, verbose_name="Порядок", help_text="Порядковый номер шага"
    )
    is_completed = models.BooleanField(
        default=False, verbose_name="Выполнено", help_text="Студент отметил шаг как выполненный"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")

    class Meta:
        verbose_name = "Шаг доработки"
        verbose_name_plural = "Шаги доработки"
        ordering = ["order", "created_at"]
        indexes = [
            models.Index(fields=["submission", "order"]),
        ]
        db_table = "courses_improvementstep"  # Сохраняем старую таблицу

    def __str__(self):
        return f"{self.submission.student.user.username} - {self.title}"


class StepProgress(models.Model):
    """
    Модель прогресса по шагу для пользователя.
    """

    profile = models.ForeignKey(
        "authentication.Student", on_delete=models.CASCADE, related_name="step_progress"
    )
    step = models.ForeignKey("courses.Step", on_delete=models.CASCADE, related_name="progress")
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Прогресс по шагу"
        verbose_name_plural = "Прогресс по шагам"
        unique_together = ("profile", "step")
        db_table = "courses_stepprogress"  # Сохраняем старую таблицу

    def __str__(self):
        return f"{self.profile.user.username} - {self.step.name}"
