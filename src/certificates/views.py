"""
Certificates Views Module - Представления для работы с сертификатами.

Этот модуль содержит views для:
    - Просмотра списка сертификатов студента
    - Детального просмотра сертификата
    - Скачивания PDF сертификата
    - Публичной верификации сертификата

Доступные views:
    - certificates_list_view: Список всех сертификатов студента
    - certificate_detail_view: Детальная информация о сертификате
    - certificate_download_view: Скачивание PDF файла
    - certificate_verify_view: Публичная страница верификации

Особенности:
    - Автоматическая генерация при завершении курса (100%)
    - PDF экспорт с уникальным номером
    - Публичная страница верификации по номеру
    - Защита от подделки

Автор: Pyland Team
Дата: 2026
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils.translation import gettext_lazy as _

from .models import Certificate

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


@login_required
def certificates_list_view(request: HttpRequest) -> HttpResponse:
    """
    Список всех сертификатов текущего студента.

    URL: /students/certificates/
    Template: students/certificates/list.html

    Context:
        certificates: QuerySet всех сертификатов студента
        valid_count: Количество действительных сертификатов
        revoked_count: Количество отозванных сертификатов
    """
    try:
        student = request.user.student
    except Exception:
        messages.error(request, _("У вас нет профиля студента"))
        return render(request, "certificates/no_student.html")

    # Получить все сертификаты студента
    certificates = (
        Certificate.objects.filter(student=student).select_related("course").order_by("-issued_at")
    )

    # Статистика
    valid_count = certificates.filter(is_valid=True).count()
    revoked_count = certificates.filter(is_valid=False).count()

    context = {
        "certificates": certificates,
        "valid_count": valid_count,
        "revoked_count": revoked_count,
    }

    return render(request, "students/certificates/list.html", context)


@login_required
def certificate_detail_view(request: HttpRequest, verification_code: str) -> HttpResponse:
    """
    Детальная информация о конкретном сертификате.

    URL: /students/certificates/<verification_code>/
    Template: students/certificates/detail.html

    Context:
        certificate: Объект Certificate
        can_download: Можно ли скачать PDF
    """
    certificate = get_object_or_404(
        Certificate.objects.select_related("student__user", "course"),
        verification_code=verification_code.upper()
    )

    # Проверка доступа - только владелец может видеть свой сертификат
    if certificate.student != request.user.student:
        messages.error(request, _("У вас нет доступа к этому сертификату"))
        raise Http404(_("Сертификат не найден"))

    # Проверить наличие PDF файла
    can_download = bool(certificate.pdf_file)

    context = {
        "certificate": certificate,
        "can_download": can_download,
    }

    return render(request, "students/certificates/detail.html", context)


@login_required
def certificate_download_view(request: HttpRequest, verification_code: str) -> HttpResponse:
    """
    Скачивание PDF файла сертификата.

    URL: /students/certificates/<verification_code>/download/
    Response: FileResponse с PDF

    Если PDF еще не сгенерирован - генерирует его автоматически.
    """
    certificate = get_object_or_404(Certificate, verification_code=verification_code.upper())

    # Проверка доступа
    if certificate.student != request.user.student:
        messages.error(request, _("У вас нет доступа к этому сертификату"))
        raise Http404(_("Сертификат не найден"))

    # Если PDF не существует - генерируем
    if not certificate.pdf_file:
        try:
            from .utils import generate_certificate_pdf

            # Определить язык из запроса
            language = request.LANGUAGE_CODE if hasattr(request, 'LANGUAGE_CODE') else 'ru'
            if language not in ['ru', 'en', 'ka']:
                language = 'ru'
            
            generate_certificate_pdf(certificate, language=language)
            certificate.refresh_from_db()
        except Exception as e:
            logger.error(f"Failed to generate PDF for certificate {pk}: {e}")
            messages.error(request, _("Ошибка при генерации PDF сертификата"))
            raise Http404(_("PDF файл не найден")) from e

    # Открыть файл и отправить как FileResponse
    try:
        pdf_file = certificate.pdf_file.open("rb")
        filename = f"certificate_{certificate.certificate_number}.pdf"

        response = FileResponse(
            pdf_file, content_type="application/pdf", as_attachment=True, filename=filename
        )

        logger.info(
            f"Certificate {certificate.certificate_number} downloaded by user {request.user.email}"
        )

        return response

    except Exception as e:
        logger.error(f"Error serving PDF file for certificate {pk}: {e}")
        messages.error(request, _("Ошибка при скачивании файла"))
        raise Http404(_("PDF файл не найден")) from e


def certificate_verify_view(request: HttpRequest, verification_code: str) -> HttpResponse:
    """
    Публичная страница верификации сертификата.

    URL: /certificates/verify/<verification_code>/
    Template: students/certificates/verify.html

    Доступна ВСЕМ (не требует авторизации) для проверки подлинности сертификата.

    Context:
        certificate: Объект Certificate (если найден)
        is_valid: Действителен ли сертификат
        not_found: Если сертификат не найден
    """
    try:
        certificate = Certificate.objects.select_related("student__user", "course").get(
            verification_code=verification_code.upper()
        )

        context = {
            "certificate": certificate,
            "is_valid": certificate.is_valid,
            "not_found": False,
        }

    except Certificate.DoesNotExist:
        context = {
            "certificate": None,
            "is_valid": False,
            "not_found": True,
        }

    return render(request, "students/certificates/verify.html", context)


def certificate_verify_by_code_view(request: HttpRequest) -> HttpResponse:
    """
    Страница верификации сертификата по verification code.

    URL: /certificates/verify/
    Template: certificates/verify_form.html

    GET: Показывает форму для ввода кода
    POST: Проверяет код и показывает результат
    """
    certificate = None
    is_valid = False
    not_found = False

    if request.method == "POST":
        verification_code = request.POST.get("verification_code", "").strip().upper()

        if verification_code:
            try:
                certificate = Certificate.objects.select_related("student__user", "course").get(
                    verification_code=verification_code
                )

                is_valid = certificate.is_valid
                not_found = False

            except Certificate.DoesNotExist:
                not_found = True

    context = {
        "certificate": certificate,
        "is_valid": is_valid,
        "not_found": not_found,
    }

    return render(request, "certificates/verify_form.html", context)
