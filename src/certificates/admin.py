"""
Certificates Admin Module - Административная панель для сертификатов.

Настройки Django Admin для модели Certificate.
"""

from __future__ import annotations

from django.contrib import admin
from django.http import HttpRequest
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Certificate


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    """Админ-панель для управления сертификатами."""

    list_display = (
        "certificate_number",
        "student_info",
        "course_info",
        "completion_date",
        "final_grade",
        "status_badge",
        "has_pdf",
    )
    list_filter = (
        "is_valid",
        "completion_date",
        "course",
        "final_grade",
    )
    search_fields = (
        "certificate_number",
        "verification_code",
        "student__user__email",
        "student__user__first_name",
        "student__user__last_name",
        "course__title",
    )
    readonly_fields = (
        "certificate_number",
        "verification_code",
        "created_at",
        "updated_at",
        "completion_date",
        "lessons_completed",
        "total_lessons",
        "assignments_submitted",
        "assignments_approved",
        "reviews_received",
        "total_time_spent",
        "final_grade",
        "pdf_file",
        "download_link",
        "verification_link",
    )
    fieldsets = (
        (
            _("Основная информация"),
            {
                "fields": (
                    "student",
                    "course",
                    "certificate_number",
                    "verification_code",
                    "completion_date",
                )
            },
        ),
        (
            _("Статистика прохождения"),
            {
                "fields": (
                    "lessons_completed",
                    "total_lessons",
                    "assignments_submitted",
                    "assignments_approved",
                    "reviews_received",
                    "total_time_spent",
                    "final_grade",
                )
            },
        ),
        (
            _("PDF и верификация"),
            {
                "fields": (
                    "pdf_file",
                    "download_link",
                    "verification_link",
                )
            },
        ),
        (
            _("Статус и отзыв"),
            {
                "fields": (
                    "is_valid",
                    "revoked_at",
                    "revoke_reason",
                )
            },
        ),
        (
            _("Системные поля"),
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )
    date_hierarchy = "completion_date"
    ordering = ("-completion_date",)
    actions = ["revoke_certificates", "restore_certificates"]

    @admin.display(description=_("Студент"))
    def student_info(self, obj: Certificate) -> str:
        """Информация о студенте."""
        return format_html(
            "<strong>{}</strong><br><small>{}</small>",
            obj.student.user.get_full_name() or obj.student.user.email,
            obj.student.user.email,
        )

    @admin.display(description=_("Курс"))
    def course_info(self, obj: Certificate) -> str:
        """Информация о курсе."""
        return format_html(
            "<strong>{}</strong><br><small>{} уроков</small>",
            obj.course.title,
            obj.total_lessons,
        )

    @admin.display(description=_("Статус"))
    def status_badge(self, obj: Certificate) -> str:
        """Бейдж статуса сертификата."""
        if obj.is_valid:
            return format_html(
                '<span style="color: white; background-color: green; '
                'padding: 3px 10px; border-radius: 3px;">✓ Действителен</span>'
            )
        return format_html(
            '<span style="color: white; background-color: red; '
            'padding: 3px 10px; border-radius: 3px;">✗ Отозван</span>'
        )

    @admin.display(description=_("PDF"))
    def has_pdf(self, obj: Certificate) -> str:
        """Наличие PDF файла."""
        if obj.pdf_file:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: red;">✗</span>')

    @admin.display(description=_("Скачивание"))
    def download_link(self, obj: Certificate) -> str:
        """Ссылка на скачивание PDF."""
        if obj.pdf_file:
            return format_html(
                '<a href="{}" target="_blank" class="button">Скачать PDF</a>',
                obj.pdf_file.url,
            )
        return "-"

    @admin.display(description=_("Верификация"))
    def verification_link(self, obj: Certificate) -> str:
        """Ссылка на публичную верификацию."""
        from django.urls import reverse

        url = reverse("certificates:verify_by_code", args=[obj.verification_code])
        return format_html(
            '<a href="{}" target="_blank">{}</a>',
            url,
            _("Проверить подлинность"),
        )

    @admin.action(description=_("Отозвать выбранные сертификаты"))
    def revoke_certificates(self, request: HttpRequest, queryset) -> None:
        """Action для отзыва сертификатов."""
        count = 0
        for certificate in queryset.filter(is_valid=True):
            certificate.revoke(reason=_("Отозван администратором"))
            count += 1

        self.message_user(
            request,
            _(f"Отозвано сертификатов: {count}"),
        )

    @admin.action(description=_("Восстановить выбранные сертификаты"))
    def restore_certificates(self, request: HttpRequest, queryset) -> None:
        """Action для восстановления сертификатов."""
        count = 0
        for certificate in queryset.filter(is_valid=False):
            certificate.restore()
            count += 1

        self.message_user(
            request,
            _(f"Восстановлено сертификатов: {count}"),
        )

    def has_delete_permission(self, request: HttpRequest, obj=None) -> bool:
        """Запрет удаления сертификатов напрямую."""
        return False  # Используем revoke вместо удаления
