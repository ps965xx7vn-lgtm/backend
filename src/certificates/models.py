"""
Certificates Models Module - Модели данных для системы сертификатов.

Этот модуль содержит модели для генерации и управления сертификатами:

Модели:
    Certificate - Основная модель сертификата
        - student: Студент, получивший сертификат
        - course: Курс, по которому выдан сертификат
        - completion_date: Дата завершения курса
        - certificate_number: Уникальный номер (CERT-YYYYMMDD-XXXX)
        - verification_code: Код для проверки подлинности

        Статистика по курсу:
        - lessons_completed: Количество пройденных уроков
        - total_lessons: Общее количество уроков
        - assignments_submitted: Количество сданных заданий
        - assignments_approved: Количество одобренных заданий
        - reviews_received: Количество полученных проверок
        - total_time_spent: Общее время обучения (в часах)
        - final_grade: Итоговая оценка (если есть)

        PDF и верификация:
        - pdf_file: Ссылка на сгенерированный PDF
        - is_valid: Статус действительности сертификата
        - issued_at: Дата выдачи

Особенности:
    - Автоматическая генерация при завершении курса (100%)
    - Уникальные номера с префиксом CERT-
    - Верификационный код для проверки подлинности
    - Детальная статистика прохождения курса
    - PDF генерация с красивым дизайном
    - Публичная верификация по номеру/коду

Автор: Pyland Team
Дата: 2026
"""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

if TYPE_CHECKING:
    from authentication.models import Student
    from courses.models import Course


def generate_certificate_number() -> str:
    """
    Генерировать уникальный номер сертификата.

    Формат: CERT-YYYYMMDD-XXXX
    Пример: CERT-20260131-A3F9

    Returns:
        str: Уникальный номер сертификата
    """
    date_str = datetime.now().strftime("%Y%m%d")
    unique_part = uuid.uuid4().hex[:4].upper()
    return f"CERT-{date_str}-{unique_part}"


def generate_verification_code(certificate_number: str, student_email: str) -> str:
    """
    Генерировать код верификации на основе номера сертификата и email студента.

    Args:
        certificate_number: Номер сертификата
        student_email: Email студента

    Returns:
        str: Хеш для верификации (первые 12 символов SHA-256)
    """
    data = f"{certificate_number}:{student_email}:{settings.SECRET_KEY}"
    hash_obj = hashlib.sha256(data.encode())
    return hash_obj.hexdigest()[:12].upper()


class Certificate(models.Model):
    """
    Модель сертификата о завершении курса.

    Автоматически создается при достижении студентом 100% прогресса курса.
    Содержит детальную статистику прохождения и уникальный номер для верификации.

    Attributes:
        student: Студент, получивший сертификат
        course: Курс, по которому выдан сертификат
        completion_date: Дата завершения курса (100% прогресс)
        certificate_number: Уникальный номер формата CERT-YYYYMMDD-XXXX
        verification_code: Код для проверки подлинности (SHA-256)

        Статистика курса:
            lessons_completed: Пройдено уроков
            total_lessons: Всего уроков в курсе
            assignments_submitted: Сдано заданий
            assignments_approved: Одобрено заданий
            reviews_received: Получено проверок
            total_time_spent: Общее время обучения (часы)
            final_grade: Итоговая оценка (0-100)

        PDF и статус:
            pdf_file: Сгенерированный PDF файл
            is_valid: Действителен ли сертификат
            revoked_at: Дата отзыва (если отозван)
            revoke_reason: Причина отзыва
            issued_at: Дата выдачи сертификата

        Метаданные:
            created_at: Дата создания записи
            updated_at: Дата обновления
    """

    # Основная информация
    student = models.ForeignKey(
        "authentication.Student",
        on_delete=models.CASCADE,
        related_name="certificates",
        verbose_name="Студент",
        help_text="Студент, получивший сертификат",
    )

    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="certificates",
        verbose_name="Курс",
        help_text="Курс, по которому выдан сертификат",
    )

    completion_date = models.DateField(
        verbose_name="Дата завершения",
        help_text="Дата достижения 100% прогресса курса",
    )

    certificate_number = models.CharField(
        max_length=50,
        unique=True,
        default=generate_certificate_number,
        verbose_name="Номер сертификата",
        help_text="Уникальный номер формата CERT-YYYYMMDD-XXXX",
        db_index=True,
    )

    verification_code = models.CharField(
        max_length=12,
        unique=True,
        verbose_name="Код верификации",
        help_text="Уникальный код для проверки подлинности",
        db_index=True,
    )

    # Статистика прохождения курса
    lessons_completed = models.PositiveIntegerField(
        default=0,
        verbose_name="Пройдено уроков",
        help_text="Количество завершенных уроков",
    )

    total_lessons = models.PositiveIntegerField(
        default=0,
        verbose_name="Всего уроков",
        help_text="Общее количество уроков в курсе",
    )

    assignments_submitted = models.PositiveIntegerField(
        default=0,
        verbose_name="Сдано заданий",
        help_text="Количество отправленных на проверку заданий",
    )

    assignments_approved = models.PositiveIntegerField(
        default=0,
        verbose_name="Одобрено заданий",
        help_text="Количество одобренных заданий",
    )

    reviews_received = models.PositiveIntegerField(
        default=0,
        verbose_name="Получено проверок",
        help_text="Количество полученных ревью от проверяющих",
    )

    total_time_spent = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Время обучения (часы)",
        help_text="Общее время, затраченное на курс",
    )

    final_grade = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="Итоговая оценка",
        help_text="Оценка от 0 до 100 (если применимо)",
    )

    # PDF и статус
    pdf_file = models.FileField(
        upload_to="certificates/",
        null=True,
        blank=True,
        verbose_name="PDF файл",
        help_text="Сгенерированный PDF сертификат",
    )

    is_valid = models.BooleanField(
        default=True,
        verbose_name="Действителен",
        help_text="Статус действительности сертификата",
        db_index=True,
    )

    revoked_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата отзыва",
        help_text="Когда сертификат был отозван",
    )

    revoke_reason = models.TextField(
        blank=True,
        verbose_name="Причина отзыва",
        help_text="Почему сертификат был отозван",
    )

    issued_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата выдачи",
        help_text="Когда сертификат был выдан",
        db_index=True,
    )

    # Метаданные
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Создан",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Обновлен",
    )

    class Meta:
        db_table = "certificates"
        verbose_name = "Сертификат"
        verbose_name_plural = "Сертификаты"
        ordering = ["-issued_at"]
        unique_together = [["student", "course"]]
        indexes = [
            models.Index(fields=["-issued_at"]),
            models.Index(fields=["certificate_number"]),
            models.Index(fields=["verification_code"]),
            models.Index(fields=["student", "-issued_at"]),
            models.Index(fields=["course", "-issued_at"]),
            models.Index(fields=["is_valid"]),
        ]

    def __str__(self) -> str:
        return (
            f"{self.certificate_number} - {self.student.user.get_full_name()} ({self.course.title})"
        )

    def save(self, *args, **kwargs):
        """Override save для генерации verification_code."""
        if not self.verification_code:
            self.verification_code = generate_verification_code(
                self.certificate_number, self.student.user.email
            )
        super().save(*args, **kwargs)

    def get_completion_percentage(self) -> float:
        """Получить процент завершенных уроков."""
        if self.total_lessons == 0:
            return 0.0
        return (self.lessons_completed / self.total_lessons) * 100

    def get_approval_rate(self) -> float:
        """Получить процент одобренных заданий."""
        if self.assignments_submitted == 0:
            return 0.0
        return (self.assignments_approved / self.assignments_submitted) * 100

    def get_grade_display(self) -> str:
        """Получить текстовое представление оценки."""
        if self.final_grade is None:
            return "Не оценивалось"

        if self.final_grade >= 90:
            return f"Отлично ({self.final_grade})"
        elif self.final_grade >= 75:
            return f"Хорошо ({self.final_grade})"
        elif self.final_grade >= 60:
            return f"Удовлетворительно ({self.final_grade})"
        else:
            return f"{self.final_grade}"

    def revoke(self, reason: str = "") -> None:
        """
        Отозвать сертификат.

        Args:
            reason: Причина отзыва
        """
        self.is_valid = False
        self.revoked_at = timezone.now()
        self.revoke_reason = reason
        self.save(update_fields=["is_valid", "revoked_at", "revoke_reason", "updated_at"])

    def restore(self) -> None:
        """Восстановить отозванный сертификат."""
        self.is_valid = True
        self.revoked_at = None
        self.revoke_reason = ""
        self.save(update_fields=["is_valid", "revoked_at", "revoke_reason", "updated_at"])

    def get_public_url(self) -> str:
        """Получить публичный URL для верификации сертификата."""
        from django.urls import reverse

        return reverse(
            "certificates:verify", kwargs={"certificate_number": self.certificate_number}
        )

    def get_download_url(self) -> str:
        """Получить URL для скачивания PDF."""
        from django.urls import reverse

        return reverse("certificates:download", kwargs={"pk": self.pk})

    @classmethod
    def create_for_student(
        cls, student: Student, course: Course, completion_date: datetime.date | None = None
    ) -> Certificate:
        """
        Создать сертификат для студента при завершении курса.

        Автоматически собирает статистику из базы данных.

        Args:
            student: Студент
            course: Курс
            completion_date: Дата завершения (по умолчанию сегодня)

        Returns:
            Certificate: Созданный сертификат

        Examples:
            >>> from authentication.models import Student
            >>> from courses.models import Course
            >>> student = Student.objects.first()
            >>> course = Course.objects.first()
            >>> cert = Certificate.create_for_student(student, course)
        """
        from reviewers.models import LessonSubmission, StepProgress

        if completion_date is None:
            completion_date = timezone.now().date()

        # Собрать статистику из базы данных
        total_lessons = course.lessons.count()

        # Подсчет завершенных уроков
        completed_lessons = 0
        for lesson in course.lessons.all():
            lesson_progress = lesson.get_progress_for_profile(student)
            if lesson_progress >= 100:
                completed_lessons += 1

        # Подсчет заданий и проверок
        submissions = LessonSubmission.objects.filter(student=student, lesson__course=course)
        assignments_submitted = submissions.count()
        assignments_approved = submissions.filter(status="approved").count()
        reviews_received = submissions.exclude(status="pending").count()

        # Подсчет времени (примерная оценка на основе прогресса)
        steps_completed = StepProgress.objects.filter(
            profile=student, step__lesson__course=course, is_completed=True
        ).count()
        # Примерно 15 минут на шаг
        total_time_spent = (steps_completed * 15) / 60  # В часах

        # Создать сертификат
        certificate = cls.objects.create(
            student=student,
            course=course,
            completion_date=completion_date,
            lessons_completed=completed_lessons,
            total_lessons=total_lessons,
            assignments_submitted=assignments_submitted,
            assignments_approved=assignments_approved,
            reviews_received=reviews_received,
            total_time_spent=total_time_spent,
        )

        return certificate
