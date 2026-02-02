"""
Certificates Utils Module - Утилиты для работы с сертификатами.

Этот модуль содержит функции для:
    - Генерации PDF сертификатов
    - Проверки готовности студента к получению сертификата
    - Отправки уведомлений о получении сертификата

Основные функции:
    - generate_certificate_pdf: Генерация красивого PDF сертификата
    - can_receive_certificate: Проверка, может ли студент получить сертификат
    - send_certificate_notification: Отправка email о выдаче сертификата

Используемые библиотеки:
    - ReportLab для генерации PDF (установить: poetry add reportlab)
    - или WeasyPrint для HTML to PDF (poetry add weasyprint)

Автор: Pyland Team
Дата: 2026
"""

from __future__ import annotations

import logging
from io import BytesIO
from typing import TYPE_CHECKING

from django.conf import settings
from django.core.files.base import ContentFile
from django.template.loader import render_to_string

if TYPE_CHECKING:
    from authentication.models import Student
    from courses.models import Course

    from .models import Certificate

logger = logging.getLogger(__name__)


def can_receive_certificate(student: Student, course: Course) -> tuple[bool, str]:
    """
    Проверить, может ли студент получить сертификат за курс.

    Критерии:
    - Прогресс курса >= 100%
    - Все обязательные уроки завершены
    - Нет ожидающих проверки заданий (опционально)

    Args:
        student: Студент
        course: Курс

    Returns:
        tuple: (can_receive: bool, reason: str)
            - True, "" если может получить
            - False, "причина" если не может

    Examples:
        >>> can_receive, reason = can_receive_certificate(student, course)
        >>> if can_receive:
        >>>     Certificate.create_for_student(student, course)
    """
    # Проверка 1: Студент записан на курс
    if not student.courses.filter(id=course.id).exists():
        return False, "Студент не записан на этот курс"

    # Проверка 2: Прогресс >= 100%
    course_progress = course.get_progress_for_profile(student)
    if course_progress < 100:
        return False, f"Прогресс курса {course_progress:.1f}% (требуется 100%)"

    # Проверка 3: Все уроки завершены
    total_lessons = course.lessons.count()
    if total_lessons == 0:
        return False, "В курсе нет уроков"

    completed_lessons = 0
    for lesson in course.lessons.all():
        lesson_progress = lesson.get_progress_for_profile(student)
        if lesson_progress >= 100:
            completed_lessons += 1

    if completed_lessons < total_lessons:
        return False, f"Завершено {completed_lessons}/{total_lessons} уроков"

    # Проверка 4: Нет ожидающих проверки заданий (опционально)
    from reviewers.models import LessonSubmission

    pending_submissions = LessonSubmission.objects.filter(
        student=student, lesson__course=course, status="pending"
    ).count()

    if pending_submissions > 0:
        return False, f"Есть {pending_submissions} заданий на проверке"

    # Все проверки пройдены
    return True, ""


def generate_certificate_pdf(certificate: Certificate) -> None:
    """
    Сгенерировать PDF файл сертификата.

    Использует ReportLab для создания красивого PDF с:
    - Логотипом платформы
    - Данными студента (имя, фамилия)
    - Информацией о курсе
    - Датой завершения
    - Номером сертификата
    - Статистикой прохождения
    - QR кодом для верификации

    Args:
        certificate: Объект Certificate для генерации PDF

    Raises:
        ImportError: Если ReportLab не установлен
        Exception: При ошибке генерации PDF

    Examples:
        >>> from certificates.models import Certificate
        >>> cert = Certificate.objects.first()
        >>> generate_certificate_pdf(cert)
        >>> print(cert.pdf_file.url)  # URL к сгенерированному PDF
    """
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import cm
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    except ImportError as e:
        logger.error("ReportLab is not installed. Install it: poetry add reportlab")
        raise ImportError(
            "ReportLab требуется для генерации PDF. Установите: poetry add reportlab"
        ) from e

    # Создать BytesIO buffer для PDF
    buffer = BytesIO()

    # Настроить документ (альбомная ориентация A4)
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    # Стили
    styles = getSampleStyleSheet()

    # Кастомные стили
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=36,
        textColor=colors.HexColor("#2C3E50"),
        spaceAfter=30,
        alignment=1,  # Центрирование
        fontName="Helvetica-Bold",
    )

    subtitle_style = ParagraphStyle(
        "CustomSubtitle",
        parent=styles["Heading2"],
        fontSize=24,
        textColor=colors.HexColor("#3498DB"),
        spaceAfter=20,
        alignment=1,
        fontName="Helvetica",
    )

    body_style = ParagraphStyle(
        "CustomBody",
        parent=styles["Normal"],
        fontSize=14,
        textColor=colors.HexColor("#34495E"),
        spaceAfter=12,
        alignment=1,
        fontName="Helvetica",
    )

    # Контент для PDF
    story = []

    # Заголовок
    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph("🎓 СЕРТИФИКАТ 🎓", title_style))
    story.append(Paragraph("О ЗАВЕРШЕНИИ КУРСА", subtitle_style))
    story.append(Spacer(1, 1 * cm))

    # Информация о студенте
    student_name = certificate.student.user.get_full_name()
    if not student_name.strip():
        student_name = certificate.student.user.email

    story.append(Paragraph("Настоящий сертификат подтверждает, что", body_style))
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(f"<b>{student_name}</b>", subtitle_style))
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph("успешно завершил(а) онлайн-курс", body_style))
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(f"<b>{certificate.course.title}</b>", subtitle_style))
    story.append(Spacer(1, 1 * cm))

    # Статистика в таблице
    stats_data = [
        ["Уроков пройдено:", f"{certificate.lessons_completed} из {certificate.total_lessons}"],
        ["Заданий сдано:", f"{certificate.assignments_submitted}"],
        ["Заданий одобрено:", f"{certificate.assignments_approved}"],
        ["Проверок получено:", f"{certificate.reviews_received}"],
        ["Время обучения:", f"{certificate.total_time_spent:.1f} часов"],
    ]

    if certificate.final_grade:
        stats_data.append(["Итоговая оценка:", certificate.get_grade_display()])

    stats_table = Table(stats_data, colWidths=[8 * cm, 8 * cm])
    stats_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#ECF0F1")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#2C3E50")),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 12),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, -1), 12),
                ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#BDC3C7")),
            ]
        )
    )

    story.append(stats_table)
    story.append(Spacer(1, 1 * cm))

    # Дата завершения
    completion_date_str = certificate.completion_date.strftime("%d.%m.%Y")
    story.append(Paragraph(f"Дата завершения: <b>{completion_date_str}</b>", body_style))
    story.append(Spacer(1, 0.5 * cm))

    # Номер сертификата
    story.append(
        Paragraph(f"Номер сертификата: <b>{certificate.certificate_number}</b>", body_style)
    )
    story.append(Paragraph(f"Код верификации: <b>{certificate.verification_code}</b>", body_style))
    story.append(Spacer(1, 0.5 * cm))

    # Ссылка для верификации
    verify_url = f"https://pyland.ge{certificate.get_public_url()}"
    story.append(
        Paragraph(f'Проверить подлинность: <a href="{verify_url}">{verify_url}</a>', body_style)
    )

    # Построить PDF
    doc.build(story)

    # Сохранить в модель
    pdf_content = buffer.getvalue()
    buffer.close()

    filename = f"certificate_{certificate.certificate_number}.pdf"
    certificate.pdf_file.save(filename, ContentFile(pdf_content), save=True)

    logger.info(f"Generated PDF certificate for {certificate.certificate_number}")


def send_certificate_notification(certificate: Certificate) -> None:
    """
    Отправить email уведомление о получении сертификата.

    Args:
        certificate: Сертификат
    """
    from django.core.mail import send_mail

    from notifications.utils import can_send_notification

    student = certificate.student

    # Проверить, можно ли отправлять уведомления
    if not can_send_notification(student, "achievement_alert"):
        logger.info(
            f"Student {student.user.email} has notifications disabled. "
            f"Not sending certificate notification."
        )
        return

    # Подготовить контекст для email
    context = {
        "student": student,
        "certificate": certificate,
        "course": certificate.course,
        "download_url": certificate.get_download_url(),
        "verify_url": certificate.get_public_url(),
    }

    # Рендерить HTML и текстовую версию
    html_message = render_to_string("certificates/email/certificate_issued.html", context)
    text_message = render_to_string("certificates/email/certificate_issued.txt", context)

    # Отправить email
    try:
        send_mail(
            subject=f"🎓 Поздравляем! Вы получили сертификат - {certificate.course.title}",
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[student.user.email],
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(
            f"Certificate notification sent to {student.user.email} "
            f"for certificate {certificate.certificate_number}"
        )

    except Exception as e:
        logger.error(f"Failed to send certificate notification to {student.user.email}: {e}")
