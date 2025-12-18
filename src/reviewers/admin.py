"""
Reviewers Admin - Административная панель для управления ревьюерами.

Автор: Pyland Team
Дата: 2025
"""

from django.contrib import admin
from django.db.models import Max
from django.urls import reverse
from django.utils.html import format_html

from .models import (  # ReviewerProfile moved to authentication.models as Reviewer
    ImprovementStep,
    LessonSubmission,
    Review,
    ReviewerNotification,
    StudentImprovement,
)

# ReviewerProfile moved to authentication.models as Reviewer - admin registration handled in authentication/admin.py
# @admin.register(ReviewerProfile)
# class ReviewerProfileAdmin(admin.ModelAdmin):
#     """Административная панель для профилей ревьюеров."""
#
#     list_display = [
#         'user_email',
#         'role_badge',
#         'is_active',
#         'rating',
#         'total_reviews',
#         'courses_count',
#         'registered_at'
#     ]
#     list_filter = ['is_active', 'registered_at', 'courses']
#     search_fields = ['user__email', 'user__first_name', 'user__last_name', 'bio']
#     filter_horizontal = ['courses']
#     readonly_fields = ['total_reviews', 'average_review_time', 'registered_at', 'updated_at']
#
#     fieldsets = (
#         ('Основная информация', {
#             'fields': ('user', 'bio', 'expertise_areas')
#         }),
#         ('Курсы и статус', {
#             'fields': ('courses', 'is_active')
#         }),
#         ('Статистика', {
#             'fields': ('rating', 'total_reviews', 'average_review_time'),
#             'classes': ('collapse',)
#         }),
#         ('Метаданные', {
#             'fields': ('registered_at', 'updated_at'),
#             'classes': ('collapse',)
#         }),
#     )
#
#     def user_email(self, obj):
#         return obj.user.email
#     user_email.short_description = 'Email'
#     user_email.admin_order_field = 'user__email'
#
#     def role_badge(self, obj):
#         role = obj.get_role_display()
#         colors = {
#             'Ревьюер': '#10b981',
#             'Ментор': '#3b82f6',
#             'Проверяющий': '#6b7280'
#         }
#         color = colors.get(role, '#6b7280')
#         return format_html(
#             '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
#             color,
#             role
#         )
#     role_badge.short_description = 'Роль'
#
#     def courses_count(self, obj):
#         return obj.courses.count()
#     courses_count.short_description = 'Курсов'


class ImprovementStepInline(admin.TabularInline):
    """Inline для шагов доработки, создаваемых ментором"""

    model = ImprovementStep
    extra = 1
    fields = ("title", "description")
    verbose_name = "Шаг доработки"
    verbose_name_plural = "Шаги доработки для студента"

    def save_model(self, request, obj, form, change):
        """Автоматически устанавливаем порядковый номер"""
        if not obj.order:
            # Получаем максимальный order для этой работы
            max_order = (
                ImprovementStep.objects.filter(submission=obj.submission).aggregate(Max("order"))[
                    "order__max"
                ]
                or 0
            )
            obj.order = max_order + 1
        super().save_model(request, obj, form, change)


class StudentImprovementInline(admin.TabularInline):
    """Inline для улучшений в рецензии."""

    model = StudentImprovement
    extra = 1
    fields = ["improvement_number", "improvement_text", "is_completed", "completed_at"]
    readonly_fields = ["completed_at"]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Административная панель для рецензий."""

    list_display = [
        "submission_info",
        "reviewer_email",
        "status_badge",
        "time_spent",
        "reviewed_at",
    ]
    list_filter = ["status", "reviewed_at", "reviewer"]
    search_fields = [
        "lesson_submission__lesson__name",
        "lesson_submission__student__user__email",
        "reviewer__user__email",
        "comments",
    ]
    readonly_fields = ["reviewed_at", "updated_at"]
    inlines = [StudentImprovementInline]

    fieldsets = (
        ("Информация о работе", {"fields": ("lesson_submission", "reviewer")}),
        ("Результат проверки", {"fields": ("status", "time_spent", "comments")}),
        ("Метаданные", {"fields": ("reviewed_at", "updated_at"), "classes": ("collapse",)}),
    )

    def submission_info(self, obj):
        submission = obj.lesson_submission
        return f"{submission.lesson.name} — {submission.student.user.email}"

    submission_info.short_description = "Работа"

    def reviewer_email(self, obj):
        return obj.reviewer.user.email if obj.reviewer else "Не указан"

    reviewer_email.short_description = "Ревьюер"
    reviewer_email.admin_order_field = "reviewer__user__email"

    def status_badge(self, obj):
        colors = {"approved": "#10b981", "needs_work": "#f59e0b", "rejected": "#ef4444"}
        color = colors.get(obj.status, "#6b7280")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_badge.short_description = "Статус"


@admin.register(LessonSubmission)
class LessonSubmissionAdmin(admin.ModelAdmin):
    """Админка для отправленных работ студентов"""

    list_display = (
        "review_link",
        "student_link",
        "lesson_link",
        "status_badge",
        "revision_count_display",
        "github_link",
        "submitted_at",
    )
    search_fields = (
        "student__user__username",
        "student__user__email",
        "lesson__name",
        "lesson_url",
    )
    list_filter = ("status", "lesson__course", "lesson", "submitted_at", "mentor")
    ordering = ("-submitted_at",)
    readonly_fields = ("submitted_at", "submission_info")
    actions = ["mark_approved", "mark_changes_requested"]
    inlines = [ImprovementStepInline]

    fieldsets = (
        (
            "Основная информация",
            {"fields": ("student", "lesson", "lesson_url", "status")},
        ),
        (
            "Проверка",
            {"fields": ("mentor", "mentor_comment", "reviewed_at", "revision_count")},
        ),
        ("Детали", {"fields": ("submission_info",), "classes": ("collapse",)}),
        ("Системная информация", {"fields": ("submitted_at",)}),
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Ограничиваем выбор ментора только пользователями с ролью 'Ментор'"""
        if db_field.name == "mentor":
            from authentication.models import Role, Student

            # Получаем роль ментора
            mentor_role = Role.objects.filter(name__icontains="ментор").first()
            if mentor_role:
                kwargs["queryset"] = (
                    Student.objects.filter(roles=mentor_role)
                    .select_related("user")
                    .order_by("user__username")
                )
            else:
                kwargs["queryset"] = (
                    Student.objects.all().select_related("user").order_by("user__username")
                )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        """Автоматически устанавливаем reviewed_at при изменении статуса"""
        from django.utils import timezone

        if change:  # Если это редактирование существующего объекта
            # Получаем старый объект из БД
            old_obj = LessonSubmission.objects.get(pk=obj.pk)

            # Если статус изменился на approved или changes_requested
            if old_obj.status != obj.status and obj.status in ["approved", "changes_requested"]:
                # Устанавливаем текущее время проверки
                obj.reviewed_at = timezone.now()
                # Устанавливаем ментора, если не был установлен
                if not obj.mentor:
                    obj.mentor = request.user.student

        super().save_model(request, obj, form, change)

    def student_link(self, obj):
        """Ссылка на студента"""
        url = reverse("admin:authentication_student_change", args=[obj.student.id])
        return format_html('<a href="{}">{}</a>', url, obj.student.user.email)

    student_link.short_description = "Студент"

    def lesson_link(self, obj):
        """Ссылка на урок"""
        url = reverse("admin:courses_lesson_change", args=[obj.lesson.id])
        return format_html('<a href="{}">{}</a>', url, obj.lesson.name)

    lesson_link.short_description = "Урок"

    def status_badge(self, obj):
        """Цветной бейдж статуса"""
        colors = {
            "pending": "#f59e0b",
            "changes_requested": "#ef4444",
            "approved": "#10b981",
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 12px; '
            'border-radius: 16px; font-weight: 600; font-size: 0.875rem;">'
            "{} {}</span>",
            colors.get(obj.status, "#6b7280"),
            obj.get_status_icon(),
            obj.get_status_display(),
        )

    status_badge.short_description = "Статус"

    def revision_count_display(self, obj):
        """Отображение попытки"""
        if obj.revision_count > 0:
            return format_html(
                '<span style="color: #f59e0b; font-weight: bold;">Попытка: {}</span>',
                obj.revision_count + 1,
            )
        return format_html('<span style="color: #10b981;">Первая попытка</span>')

    revision_count_display.short_description = "Попытка"

    def review_link(self, obj):
        """Ссылка на страницу проверки работы"""
        url = reverse("admin:reviewers_lessonsubmission_change", args=[obj.id])
        return format_html(
            '<a href="{}" style="display: inline-flex; align-items: center; gap: 0.5rem; '
            'color: #10b981; font-weight: 600; text-decoration: none;">'
            '<svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="flex-shrink: 0;">'
            '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" '
            'd="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>'
            "</svg>"
            "Проверить</a>",
            url,
        )

    review_link.short_description = "Действие"

    def github_link(self, obj):
        """Кликабельная ссылка на GitHub репозиторий"""
        return format_html(
            '<a href="{}" target="_blank" style="display: inline-flex; align-items: center; gap: 0.5rem; '
            'color: #3b82f6; font-weight: 600; text-decoration: none;">'
            '<svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16" style="flex-shrink: 0;">'
            '<path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58-8-8-8z"/>'
            "</svg>"
            "Открыть</a>",
            obj.lesson_url,
        )

    github_link.short_description = "Репозиторий"

    def submission_info(self, obj):
        """Информация о работе"""
        return format_html(
            '<div style="background: #f3f4f6; padding: 15px; border-radius: 8px;">'
            "<div><strong>Студент:</strong> {}</div>"
            "<div><strong>Email:</strong> {}</div>"
            "<div><strong>Курс:</strong> {}</div>"
            "<div><strong>Урок:</strong> {}</div>"
            '<div><strong>GitHub:</strong> <a href="{}" target="_blank">{}</a></div>'
            "<div><strong>Статус:</strong> {} {}</div>"
            "<div><strong>Отправлено:</strong> {}</div>"
            "{}"
            "{}"
            "</div>",
            obj.student.user.get_full_name() or obj.student.user.username,
            obj.student.user.email,
            obj.lesson.course.name,
            obj.lesson.name,
            obj.lesson_url,
            obj.lesson_url,
            obj.get_status_icon(),
            obj.get_status_display(),
            obj.submitted_at.strftime("%d.%m.%Y %H:%M"),
            (
                f'<div style="margin-top: 10px;"><strong>Ментор:</strong> {obj.mentor.user.get_full_name() or obj.mentor.user.email}</div>'
                if obj.mentor
                else ""
            ),
            (
                f'<div style="margin-top: 10px;"><strong>Комментарий:</strong><br>{obj.mentor_comment}</div>'
                if obj.mentor_comment
                else ""
            ),
        )

    submission_info.short_description = "Информация"

    # Admin Actions
    def mark_approved(self, request, queryset):
        """Одобрить работы"""
        from django.utils import timezone

        updated = 0
        for submission in queryset:
            if submission.status in ["pending", "changes_requested"]:
                submission.status = "approved"
                submission.mentor = request.user.student
                submission.reviewed_at = timezone.now()
                submission.save()
                updated += 1

        self.message_user(request, f"Одобрено: {updated} работ(ы)")

    mark_approved.short_description = "✅ Одобрить"

    def mark_changes_requested(self, request, queryset):
        """Вернуть на доработку (требуется добавить комментарий вручную)"""
        from django.utils import timezone

        updated = 0
        for submission in queryset:
            if submission.status == "pending":
                submission.status = "changes_requested"
                submission.mentor = request.user.student
                submission.reviewed_at = timezone.now()
                submission.save()
                updated += 1

        self.message_user(
            request,
            f"Возвращено на доработку: {updated} работ(ы). Не забудьте добавить комментарии к каждой работе!",
            level="warning",
        )

    mark_changes_requested.short_description = "✏️ Вернуть на доработку"

    def get_queryset(self, request):
        """Оптимизация запросов"""
        qs = super().get_queryset(request)
        return qs.select_related(
            "student",
            "student__user",
            "lesson",
            "lesson__course",
            "mentor",
            "mentor__user",
        )


@admin.register(StudentImprovement)
class StudentImprovementAdmin(admin.ModelAdmin):
    """Административная панель для улучшений."""

    list_display = [
        "review_info",
        "improvement_number",
        "is_completed",
        "created_at",
        "completed_at",
    ]
    list_filter = ["is_completed", "created_at"]
    search_fields = ["improvement_text", "title", "lesson_submission__lesson__name"]
    readonly_fields = ["created_at", "completed_at"]

    def review_info(self, obj):
        if obj.review:
            submission = obj.review.lesson_submission
            return f"{submission.lesson.name} — {submission.student.user.email}"
        elif obj.lesson_submission:
            return (
                f"{obj.lesson_submission.lesson.name} — {obj.lesson_submission.student.user.email}"
            )
        return "Нет связи"

    review_info.short_description = "Работа"


@admin.register(ReviewerNotification)
class ReviewerNotificationAdmin(admin.ModelAdmin):
    """Административная панель для уведомлений."""

    list_display = ["reviewer_email", "notification_type", "title", "is_read", "created_at"]
    list_filter = ["notification_type", "is_read", "created_at"]
    search_fields = ["title", "message", "reviewer__user__email"]
    readonly_fields = ["created_at"]

    fieldsets = (
        ("Получатель", {"fields": ("reviewer",)}),
        ("Содержимое", {"fields": ("notification_type", "title", "message", "link")}),
        ("Статус", {"fields": ("is_read", "created_at")}),
    )

    def reviewer_email(self, obj):
        return obj.reviewer.user.email

    reviewer_email.short_description = "Ревьюер"
    reviewer_email.admin_order_field = "reviewer__user__email"
