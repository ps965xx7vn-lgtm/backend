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

    Logic:
        1. Проверяет запись студента на курс
        2. Проверяет прогресс >= 100%
        3. Проверяет завершение всех уроков
        4. Проверяет отсутствие ожидающих проверки заданий
    """
    if not student.courses.filter(id=course.id).exists():
        return False, "Студент не записан на этот курс"

    progress_data = course.get_progress_for_profile(student)
    course_progress = (
        progress_data.get("completion_percentage", 0)
        if isinstance(progress_data, dict)
        else progress_data
    )
    if course_progress < 100:
        return False, f"Прогресс курса {course_progress:.1f}% (требуется 100%)"

    total_lessons = course.lessons.count()
    if total_lessons == 0:
        return False, "В курсе нет уроков"

    completed_lessons = 0
    for lesson in course.lessons.all():
        progress_data = lesson.get_progress_for_profile(student)
        lesson_progress = (
            progress_data.get("completion_percentage", 0)
            if isinstance(progress_data, dict)
            else progress_data
        )
        if lesson_progress >= 100:
            completed_lessons += 1

    if completed_lessons < total_lessons:
        return False, f"Завершено {completed_lessons}/{total_lessons} уроков"
    from reviewers.models import LessonSubmission

    pending_submissions = LessonSubmission.objects.filter(
        student=student, lesson__course=course, status="pending"
    ).count()

    if pending_submissions > 0:
        return False, f"Есть {pending_submissions} заданий на проверке"

    # Все проверки пройдены
    return True, ""


def generate_certificate_pdf(certificate: Certificate, language: str = "ru") -> None:
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
        from reportlab.graphics.barcode.qr import QrCodeWidget
        from reportlab.graphics.shapes import Drawing
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import cm
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.platypus import (
            Image,
            KeepTogether,
            PageBreak,
            Paragraph,
            SimpleDocTemplate,
            Spacer,
            Table,
            TableStyle,
        )
        from reportlab.platypus.flowables import HRFlowable

    except ImportError as e:
        logger.error("ReportLab is not installed. Install it: poetry add reportlab")
        raise ImportError(
            "ReportLab требуется для генерации PDF. Установите: poetry add reportlab"
        ) from e

    # Тексты на разных языках
    translations = {
        "ru": {
            "certificate": "СЕРТИФИКАТ",
            "completion": "О ЗАВЕРШЕНИИ ОНЛАЙН-КУРСА",
            "this_certifies": "Настоящим подтверждается, что",
            "successfully_completed": "успешно завершил(а) образовательную программу",
            "completion_date": "Дата завершения",
            "certificate_number": "Номер сертификата",
            "verification_code": "Код верификации",
            "verify_at": "Проверить подлинность",
            "issued_by": "Выдан PyLand - Онлайн Школой Программирования",
            "director": "Директор",
            "course_details": "ДЕТАЛЬНАЯ ИНФОРМАЦИЯ О ПРОХОЖДЕНИИ КУРСА",
            "statistics": "Статистика прохождения",
            "lessons_completed": "Уроков завершено",
            "assignments_submitted": "Заданий отправлено",
            "assignments_approved": "Заданий одобрено",
            "reviews_received": "Получено проверок",
            "study_time": "Время обучения",
            "hours": "часов",
            "final_grade": "Итоговая оценка",
            "lesson": "Урок",
            "step": "Шаг",
            "status": "Статус",
            "completed": "Завершен",
            "in_progress": "В процессе",
        },
        "en": {
            "certificate": "CERTIFICATE",
            "completion": "OF COMPLETION",
            "this_certifies": "This certifies that",
            "successfully_completed": "has successfully completed the educational program",
            "completion_date": "Completion Date",
            "certificate_number": "Certificate Number",
            "verification_code": "Verification Code",
            "verify_at": "Verify at",
            "issued_by": "Issued by PyLand - Online Programming School",
            "director": "Director",
            "course_details": "DETAILED COURSE INFORMATION",
            "statistics": "Course Statistics",
            "lessons_completed": "Lessons Completed",
            "assignments_submitted": "Assignments Submitted",
            "assignments_approved": "Assignments Approved",
            "reviews_received": "Reviews Received",
            "study_time": "Study Time",
            "hours": "hours",
            "final_grade": "Final Grade",
            "lesson": "Lesson",
            "step": "Step",
            "status": "Status",
            "completed": "Completed",
            "in_progress": "In Progress",
        },
        "ka": {
            "certificate": "სერტიფიკატი",
            "completion": "კურსის დასრულების შესახებ",
            "this_certifies": "ვადასტურებთ, რომ",
            "successfully_completed": "წარმატებით დაასრულა საგანმანათლებლო პროგრამა",
            "completion_date": "დასრულების თარიღი",
            "certificate_number": "სერტიფიკატის ნომერი",
            "verification_code": "ვერიფიკაციის კოდი",
            "verify_at": "შეამოწმეთ",
            "issued_by": "გაცემულია PyLand - ონლაინ პროგრამირების სკოლის მიერ",
            "director": "დირექტორი",
            "course_details": "კურსის დეტალური ინფორმაცია",
            "statistics": "სტატისტიკა",
            "lessons_completed": "დასრულებული გაკვეთილები",
            "assignments_submitted": "გაგზავნილი დავალებები",
            "assignments_approved": "დამტკიცებული დავალებები",
            "reviews_received": "მიღებული შეფასებები",
            "study_time": "სასწავლო დრო",
            "hours": "საათი",
            "final_grade": "საბოლოო შეფასება",
            "lesson": "გაკვეთილი",
            "step": "ნაბიჯი",
            "status": "სტატუსი",
            "completed": "დასრულებული",
            "in_progress": "პროგრესში",
        },
    }

    t = translations.get(language, translations["ru"])

    # Логирование для отладки
    logger.info(f"Generating PDF certificate for {certificate.certificate_number}")
    logger.info(f"Language: {language}")
    logger.info(f"Translation keys available: {list(t.keys())}")
    logger.info(
        f"Sample translations: certificate={t['certificate']}, completion={t['completion']}"
    )

    # Создать BytesIO buffer для PDF
    buffer = BytesIO()

    # Регистрация шрифтов с поддержкой Unicode (кириллица, грузинский)
    # Попробуем найти DejaVu или Arial Unicode шрифты в системе
    try:
        import os

        # Возможные пути к шрифтам с Unicode поддержкой
        font_paths = [
            # macOS - Arial Unicode (ЛУЧШИЙ ВЫБОР для кириллицы и грузинского)
            "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
            "/Library/Fonts/Arial Unicode.ttf",
            # macOS - Arial
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            # Linux - DejaVu
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/dejavu/DejaVuSans.ttf",
            # macOS - DejaVu (если установлен)
            "/System/Library/Fonts/Supplemental/DejaVuSans.ttf",
            "/Library/Fonts/DejaVuSans.ttf",
            # Windows - Arial
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/DejaVuSans.ttf",
        ]

        font_found = False
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont("CustomFont", font_path))

                    # Для Bold версии
                    bold_path = None
                    if "Arial Unicode" in font_path:
                        # Arial Unicode is already bold-capable
                        pdfmetrics.registerFont(TTFont("CustomFont-Bold", font_path))
                    elif "Arial.ttf" in font_path:
                        bold_path = font_path.replace("Arial.ttf", "Arial Bold.ttf")
                    elif "DejaVuSans.ttf" in font_path:
                        bold_path = font_path.replace("DejaVuSans.ttf", "DejaVuSans-Bold.ttf")

                    if bold_path and os.path.exists(bold_path):
                        pdfmetrics.registerFont(TTFont("CustomFont-Bold", bold_path))
                    else:
                        # Fallback: use same font for bold
                        pdfmetrics.registerFont(TTFont("CustomFont-Bold", font_path))

                    font_found = True
                    logger.info(f"✅ Registered Unicode font from: {font_path}")
                    break
                except Exception as e:
                    logger.warning(f"Failed to register font from {font_path}: {e}")
                    continue

        if not font_found:
            logger.warning(
                "⚠️  No Unicode fonts found, using Helvetica (кириллица может не отображаться)"
            )
            font_name = "Helvetica"
            font_name_bold = "Helvetica-Bold"
        else:
            font_name = "CustomFont"
            font_name_bold = "CustomFont-Bold"
    except Exception as e:
        logger.error(f"Font registration error: {e}, falling back to Helvetica")
        font_name = "Helvetica"
        font_name_bold = "Helvetica-Bold"

    # Настроить документ (альбомная ориентация A4)
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    # Стили
    styles = getSampleStyleSheet()

    # Кастомные стили - чистый современный дизайн
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=32,
        textColor=colors.HexColor("#1a365d"),
        spaceAfter=10,
        alignment=TA_CENTER,
        fontName=font_name_bold,
        leading=36,
    )

    subtitle_style = ParagraphStyle(
        "CustomSubtitle",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=colors.HexColor("#4a5568"),
        spaceAfter=10,
        alignment=TA_CENTER,
        fontName=font_name,
        leading=18,
    )

    name_style = ParagraphStyle(
        "NameStyle",
        parent=styles["Normal"],
        fontSize=24,
        textColor=colors.HexColor("#2b6cb0"),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName=font_name_bold,
        leading=28,
    )

    course_style = ParagraphStyle(
        "CourseStyle",
        parent=styles["Normal"],
        fontSize=18,
        textColor=colors.HexColor("#1a365d"),
        spaceAfter=10,
        alignment=TA_CENTER,
        fontName=font_name_bold,
        leading=22,
    )

    # ==================== СТРАНИЦА 1: Современный дизайн в стиле программирования ====================
    story = []

    # Генерация QR кода для верификации с логотипом в центре
    verify_url_full = (
        f"https://pylandschool.com/certificates/verify/{certificate.verification_code}/"
    )

    # Попробовать найти favicon/logo
    import os

    logo_paths = [
        os.path.join(settings.BASE_DIR, "static", "images", "favicon.png"),
        os.path.join(settings.BASE_DIR, "static", "images", "logo-icon.png"),
        os.path.join(settings.BASE_DIR, "static", "favicon.ico"),
    ]
    logo_path = None
    for path in logo_paths:
        if os.path.exists(path):
            logo_path = path
            logger.info(f"Found logo for QR code: {path}")
            break

    # Генерировать QR с логотипом используя qrcode + PIL (УВЕЛИЧЕННЫЙ)
    try:
        from .qr_utils import generate_qr_with_logo

        qr_buffer = generate_qr_with_logo(verify_url_full, logo_path=logo_path, size=300)
        qr_image = Image(qr_buffer, width=2.5 * cm, height=2.5 * cm)
    except Exception as e:
        logger.warning(f"Failed to generate QR with logo: {e}. Using standard QR.")
        # Fallback на стандартный QR без логотипа
        qr_code = QrCodeWidget(verify_url_full)
        qr_bounds = qr_code.getBounds()
        qr_width = qr_bounds[2] - qr_bounds[0]
        qr_height = qr_bounds[3] - qr_bounds[1]
        qr_drawing = Drawing(90, 90, transform=[90.0 / qr_width, 0, 0, 90.0 / qr_height, 0, 0])
        qr_drawing.add(qr_code)
        qr_image = qr_drawing

    # Получить данные
    student_name = certificate.student.user.get_full_name()
    if not student_name.strip():
        student_name = certificate.student.user.email

    completion_date_str = certificate.completion_date.strftime("%d.%m.%Y")
    issued_date_str = certificate.issued_at.strftime("%d.%m.%Y")

    # Краткое описание курса (первые 200 символов)
    course_description = (
        certificate.course.description[:200] + "..."
        if len(certificate.course.description) > 200
        else certificate.course.description
    )
    if not course_description.strip():
        course_description = f"Полный онлайн-курс по теме: {certificate.course.name}"

    # Логирование данных
    logger.info(f"Student name: {student_name}")
    logger.info(f"Completion date: {completion_date_str}")
    logger.info(f"Issued date: {issued_date_str}")
    logger.info(f"Certificate title will be: [ {t['certificate']} ]")

    # Верхняя декоративная рамка
    story.append(
        HRFlowable(
            width="100%", thickness=2, color=colors.HexColor("#667eea"), spaceBefore=0, spaceAfter=3
        )
    )

    # Шапка с логотипом и QR кодом
    header_data = [
        [
            Paragraph(
                "<b>PyLand School</b><br/><font size=8>Онлайн Школа Программирования</font>",
                ParagraphStyle(
                    "LogoText",
                    parent=styles["Normal"],
                    fontSize=12,
                    textColor=colors.HexColor("#667eea"),
                    alignment=TA_LEFT,
                    fontName=font_name_bold,
                    leading=14,
                ),
            ),
            qr_image,
        ]
    ]

    header_table = Table(header_data, colWidths=[20.5 * cm, 5.5 * cm])
    header_table.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (0, 0), "LEFT"),
                ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    story.append(header_table)

    # Заголовок
    story.append(Paragraph(t["certificate"], title_style))
    story.append(Paragraph(t["completion"], subtitle_style))
    story.append(Spacer(1, 0.08 * cm))
    story.append(
        HRFlowable(
            width="50%", thickness=1, color=colors.HexColor("#cbd5e0"), spaceBefore=2, spaceAfter=4
        )
    )

    # Информация о студенте (без подтверждающей строки)
    story.append(Paragraph(f"<b>{student_name}</b>", name_style))
    story.append(Spacer(1, 0.03 * cm))
    story.append(Paragraph(f'<b>"{certificate.course.name}"</b>', course_style))

    # Краткое описание курса
    description_style = ParagraphStyle(
        "Description",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#718096"),
        alignment=TA_CENTER,
        fontName=font_name,
        leading=13,
        leftIndent=3 * cm,
        rightIndent=3 * cm,
    )
    story.append(Spacer(1, 0.03 * cm))
    story.append(Paragraph(course_description, description_style))
    story.append(Spacer(1, 0.08 * cm))

    # Стили для статистики и информации
    info_style = ParagraphStyle(
        "InfoText",
        parent=styles["Normal"],
        fontSize=12,
        textColor=colors.HexColor("#2d3748"),
        fontName=font_name,
        leading=16,
        leftIndent=10,
    )

    stats_data = [
        [
            f"{t['lessons_completed']}:",
            f"<b>{certificate.lessons_completed} / {certificate.total_lessons}</b>",
        ],
        [f"{t['assignments_submitted']}:", f"<b>{certificate.assignments_submitted}</b>"],
        [f"{t['reviews_received']}:", f"<b>{certificate.reviews_received}</b>"],
        [f"{t['study_time']}:", f"<b>{certificate.total_time_spent:.1f} {t['hours']}</b>"],
    ]

    if certificate.final_grade:
        stats_data.append([f"🎯 {t['final_grade']}:", f"<b>{certificate.get_grade_display()}</b>"])

    formatted_stats = [[Paragraph(cell, info_style) for cell in row] for row in stats_data]

    stats_table = Table(formatted_stats, colWidths=[10 * cm, 9 * cm])
    stats_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f7fafc")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#2d3748")),
                ("ALIGN", (0, 0), (0, -1), "LEFT"),
                ("ALIGN", (1, 0), (1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, -1), font_name),
                ("FONTSIZE", (0, 0), (-1, -1), 12),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
                (
                    "ROWBACKGROUNDS",
                    (0, 0),
                    (-1, -1),
                    [colors.HexColor("#ffffff"), colors.HexColor("#f7fafc")],
                ),
                ("BOX", (0, 0), (-1, -1), 1.5, colors.HexColor("#667eea")),
            ]
        )
    )

    story.append(stats_table)
    story.append(Spacer(1, 0.08 * cm))

    # Информация о сертификате (компактно, без таблицы)
    cert_info_style = ParagraphStyle(
        "CertInfo",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#4a5568"),
        alignment=TA_LEFT,
        fontName=font_name,
        leading=12,
    )

    story.append(
        Paragraph(
            f"<b>{t['completion_date']}:</b> {completion_date_str} | <b>Дата выдачи:</b> {issued_date_str} | <b>{t['certificate_number']}:</b> {certificate.certificate_number}",
            cert_info_style,
        )
    )
    story.append(Spacer(1, 0.1 * cm))

    # Ссылка для верификации (компактно)
    verify_url = f"pylandschool.com/certificates/verify/{certificate.verification_code}/"
    story.append(Paragraph(f"<b>{t['verify_at']}:</b> {verify_url}", cert_info_style))

    story.append(Spacer(1, 0.08 * cm))

    # Нижняя рамка и подпись с печатью
    story.append(
        HRFlowable(
            width="100%", thickness=2, color=colors.HexColor("#667eea"), spaceBefore=3, spaceAfter=3
        )
    )

    signature_style = ParagraphStyle(
        "Signature",
        parent=styles["Normal"],
        fontSize=11,
        textColor=colors.HexColor("#4a5568"),
        alignment=TA_CENTER,
        fontName=font_name,
        leading=14,
    )

    # Подпись и печать
    signature_data = [
        [
            Paragraph(
                f"<font size=16><i>〰 Д.А.Масляев 〰</i></font><br/><b>_____________________</b><br/>{t['director']}<br/><font size=9>Масляев Дмитрий Алексеевич</font>",
                signature_style,
            ),
            Paragraph(
                f"<b>{t['completion_date']}</b><br/><font size=9>{completion_date_str}</font>",
                ParagraphStyle(
                    "Seal",
                    parent=styles["Normal"],
                    fontSize=11,
                    textColor=colors.HexColor("#2d3748"),
                    alignment=TA_CENTER,
                    fontName=font_name,
                    leading=12,
                ),
            ),
        ]
    ]

    signature_table = Table(signature_data, colWidths=[13 * cm, 13 * cm])
    signature_table.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (0, 0), "CENTER"),
                ("ALIGN", (1, 0), (1, 0), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story.append(signature_table)

    # ==================== СТРАНИЦА 2: Детальная информация по урокам ====================
    story.append(PageBreak())

    # Заголовок второй страницы
    page2_title_style = ParagraphStyle(
        "Page2Title",
        parent=styles["Heading1"],
        fontSize=28,
        textColor=colors.HexColor("#2d3748"),
        spaceAfter=15,
        alignment=TA_LEFT,
        fontName=font_name_bold,
        leading=32,
        leftIndent=0,
    )

    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(t["course_details"], page2_title_style))
    story.append(
        HRFlowable(
            width="100%",
            thickness=2,
            color=colors.HexColor("#667eea"),
            spaceBefore=8,
            spaceAfter=15,
        )
    )

    # Получить детальную информацию по урокам
    from reviewers.models import StepProgress

    lesson_style = ParagraphStyle(
        "LessonText",
        parent=styles["Normal"],
        fontSize=13,
        textColor=colors.HexColor("#1a365d"),
        fontName=font_name_bold,
        leading=16,
        leftIndent=0,
        spaceBefore=8,
        spaceAfter=4,
        backColor=colors.HexColor("#f7fafc"),
    )

    step_style = ParagraphStyle(
        "StepText",
        parent=styles["Normal"],
        fontSize=11,
        textColor=colors.HexColor("#4a5568"),
        fontName=font_name,
        leading=14,
    )

    lessons = certificate.course.lessons.all().order_by("id")

    for idx, lesson in enumerate(lessons, 1):
        # Создать группу элементов для каждого урока (предотвращает разрыв страницы)
        lesson_elements = []

        # Подсчет прогресса по уроку
        lesson_steps = lesson.steps.all()
        total_steps = lesson_steps.count()
        completed_lesson_steps = StepProgress.objects.filter(
            profile=certificate.student, step__lesson=lesson, is_completed=True
        ).count()

        # Заголовок урока БЕЗ процента (если сертификат выдан, значит все завершено)
        lesson_title = f"<b>{idx}. {lesson.name}</b> — {completed_lesson_steps}/{total_steps} {t['step'].lower()}"
        lesson_elements.append(Paragraph(lesson_title, lesson_style))
        lesson_elements.append(Spacer(1, 0.1 * cm))

        # Получить все шаги урока
        steps = lesson.steps.all().order_by("id")
        steps_data = []

        for _step_idx, step in enumerate(steps, 1):
            # Проверить статус шага
            step_progress = StepProgress.objects.filter(
                profile=certificate.student, step=step
            ).first()

            status_icon = "✓" if (step_progress and step_progress.is_completed) else "•"

            # Детальное описание шага
            step_details = []

            # Название
            step_details.append(f"<b>{step.name}</b>")

            # Описание (если есть)
            if step.description and step.description.strip():
                step_desc = (
                    step.description[:100] + "..."
                    if len(step.description) > 100
                    else step.description
                )
                step_details.append(f"<font size=9><i>{step_desc}</i></font>")

            # Действия (если есть)
            if step.actions and step.actions.strip():
                actions_short = (
                    step.actions[:80] + "..." if len(step.actions) > 80 else step.actions
                )
                step_details.append(f"<font size=8>Действия: {actions_short}</font>")

            # Самопроверка (если есть)
            if step.self_check and step.self_check.strip():
                step_details.append("<font size=8>✓ Самопроверка включена</font>")

            # Помощь при трудностях (если есть)
            if step.troubleshooting_help and step.troubleshooting_help.strip():
                step_details.append("<font size=8>💡 Подсказки доступны</font>")

            step_content = "<br/>".join(step_details)

            steps_data.append(
                [
                    Paragraph(f"{status_icon}", step_style),
                    Paragraph(step_content, step_style),
                ]
            )

        # Таблица шагов с увеличенной шириной для описания (2 колонки)
        if steps_data:
            steps_table = Table(steps_data, colWidths=[1 * cm, 18.5 * cm])
            steps_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#ffffff")),
                        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#2d3748")),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("ALIGN", (2, 0), (2, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, -1), font_name),
                        ("FONTSIZE", (0, 0), (-1, -1), 10),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                        ("TOPPADDING", (0, 0), (-1, -1), 6),
                        ("LEFTPADDING", (0, 0), (-1, -1), 8),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                        (
                            "ROWBACKGROUNDS",
                            (0, 0),
                            (-1, -1),
                            [colors.HexColor("#f9fafb"), colors.HexColor("#ffffff")],
                        ),
                    ]
                )
            )
            lesson_elements.append(steps_table)

        # Добавить все элементы урока как группу (не разбивается на страницы)
        story.append(KeepTogether(lesson_elements))
        story.append(Spacer(1, 0.3 * cm))

    # Итоговая информация
    story.append(
        HRFlowable(
            width="100%",
            thickness=2,
            color=colors.HexColor("#667eea"),
            spaceBefore=10,
            spaceAfter=15,
        )
    )

    summary_style = ParagraphStyle(
        "Summary",
        parent=styles["Normal"],
        fontSize=12,
        textColor=colors.HexColor("#4a5568"),
        alignment=TA_CENTER,
        fontName=font_name,
        leading=15,
    )

    total_steps = sum(lesson.steps.count() for lesson in lessons)
    completed_steps = StepProgress.objects.filter(
        profile=certificate.student, step__lesson__course=certificate.course, is_completed=True
    ).count()

    story.append(
        Paragraph(
            f"<b>{t['statistics']}:</b> {completed_steps}/{total_steps} {t['step'].lower()} {t['completed'].lower()}",
            summary_style,
        )
    )

    # Построить PDF
    doc.build(story)

    # Сохранить в модель
    pdf_content = buffer.getvalue()
    buffer.close()

    filename = f"certificate_{certificate.certificate_number}.pdf"
    certificate.pdf_file.save(filename, ContentFile(pdf_content), save=True)

    logger.info(f"Generated PDF certificate for {certificate.certificate_number}")

    # Возвращаем относительный путь для использования в URL (certificates/file.pdf)
    # НЕ используем .path (полный системный путь), а .name (относительный путь от MEDIA_ROOT)
    return certificate.pdf_file.name


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
            subject=f"🎓 Поздравляем! Вы получили сертификат - {certificate.course.name}",
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
