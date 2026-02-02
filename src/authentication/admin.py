"""
Административный интерфейс Django для управления аутентификацией.

Этот модуль содержит настройки Django Admin для моделей системы аутентификации,
включая кастомные действия, отображение полей и фильтры.

ModelAdmin классы:
    - CustomUserAdmin: Управление пользователями
    - RoleAdmin: Управление ролями пользователей

Примечание: Profile управление теперь в students app (StudentAdmin)

Автор: Pyland Team
Дата: 2025
"""

from __future__ import annotations

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from .models import ExpertiseArea, Manager, Mentor, Reviewer, Role, Student, User


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    """Расширенная админка для User"""

    list_display = [
        "email",
        "full_name_display",
        "role_display",
        "email_verified_status",
        "is_active",
        "is_staff",
        "date_joined_short",
    ]

    list_filter = [
        "role",
        "is_staff",
        "is_active",
        "email_is_verified",
        "date_joined",
    ]

    search_fields = [
        "email",
        "first_name",
        "last_name",
    ]

    ordering = ["-date_joined"]

    readonly_fields = ["last_login", "date_joined"]

    # Отключаем filter_horizontal/filter_vertical для groups и user_permissions
    # Используется role-based система вместо Django permissions
    filter_horizontal = []
    filter_vertical = []

    fieldsets = (
        ("Аутентификация", {"fields": ("email", "password")}),
        ("Личная информация", {"fields": ("first_name", "last_name", "username")}),
        (
            "Роль и доступ",
            {
                "fields": ("role", "is_active"),
                "description": "Выберите роль пользователя в системе",
            },
        ),
        (
            "Административные права",
            {
                "classes": ("collapse",),
                "fields": ("is_staff", "is_superuser"),
                "description": "Используется role-based система доступа. is_staff - только для Django Admin.",
            },
        ),
        (
            "Верификация email",
            {
                "fields": ("email_is_verified",),
                "classes": ("collapse",),
                "description": "Подтверждение email адреса пользователя",
            },
        ),
        ("Важные даты", {"fields": ("last_login", "date_joined"), "classes": ("collapse",)}),
    )

    add_fieldsets = (
        (
            "Создание пользователя",
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "username",
                    "password1",
                    "password2",
                    "role",
                    "is_active",
                    "email_is_verified",
                ),
            },
        ),
    )

    @admin.display(description="Имя")
    def full_name_display(self, obj):
        """Отображение полного имени"""
        name = f"{obj.first_name} {obj.last_name}".strip()
        return name if name else "-"

    @admin.display(
        description="Роль",
        ordering="role",
    )
    def role_display(self, obj):
        """Красивое отображение роли пользователя"""
        if obj.role:
            role_colors = {
                "unassigned": "#95a5a6",  # Серый
                "manager": "#3498db",  # Синий
                "reviewer": "#9b59b6",  # Фиолетовый
                "mentor": "#2ecc71",  # Зеленый
                "student": "#f39c12",  # Оранжевый
            }
            color = role_colors.get(obj.role.name, "#34495e")
            return format_html(
                '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
                color,
                obj.role.get_name_display(),
            )
        return format_html('<span style="color: #999;">Не назначена</span>')

    @admin.display(description="Email")
    def email_verified_status(self, obj):
        """Красивое отображение статуса верификации email"""
        if obj.email_is_verified:
            return format_html('<span style="color: green; font-weight: bold;">✓</span>')
        return format_html('<span style="color: red; font-weight: bold;">✗</span>')

    @admin.display(
        description="Дата регистрации",
        ordering="date_joined",
    )
    def date_joined_short(self, obj):
        """Короткое отображение даты регистрации"""
        return obj.date_joined.strftime("%d.%m.%Y")


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """Админка для Role - простая и понятная"""

    list_display = ["name_display", "users_count", "description_short"]
    search_fields = ["name", "description"]
    readonly_fields = ["name", "users_count", "users_with_role", "permissions_list"]

    fieldsets = (
        ("Информация о роли", {"fields": ("name", "description")}),
        (
            "Права доступа (Permissions)",
            {
                "fields": ("permissions_list",),
                "classes": ("collapse",),
                "description": "Кастомные права для этой роли",
            },
        ),
        ("Статистика", {"fields": ("users_count", "users_with_role"), "classes": ("collapse",)}),
    )

    @admin.display(
        description="Роль",
        ordering="name",
    )
    def name_display(self, obj):
        """Красивое отображение названия роли"""
        role_colors = {
            "unassigned": "#95a5a6",  # Серый
            "manager": "#3498db",  # Синий
            "reviewer": "#9b59b6",  # Фиолетовый
            "mentor": "#2ecc71",  # Зеленый
            "student": "#f39c12",  # Оранжевый
        }
        color = role_colors.get(obj.name, "#34495e")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_name_display(),
        )

    @admin.display(description="Описание")
    def description_short(self, obj):
        """Краткое описание роли"""
        if obj.description:
            return obj.description[:50] + "..." if len(obj.description) > 50 else obj.description
        return "-"

    @admin.display(description="Пользователей")
    def users_count(self, obj):
        """Количество пользователей с этой ролью"""
        count = obj.users.count()
        return f"{count} пользователей" if count != 1 else "1 пользователь"

    @admin.display(description="Пользователи с этой ролью")
    def users_with_role(self, obj):
        """Подробный список пользователей с этой ролью"""
        users = obj.users.all()
        if not users.exists():
            return "Нет пользователей"

        html = '<ul style="margin: 0; padding-left: 20px;">'
        for user in users:
            html += f"<li>{user.email} ({user.first_name} {user.last_name})</li>"
        html += "</ul>"
        return format_html(html)

    @admin.display(description="Permissions")
    def permissions_list(self, obj):
        """Отображение всех permissions для этой роли"""
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType

        # Получаем ContentType для модели по имени роли
        model_map = {
            "student": "student",
            "reviewer": "reviewer",
            "mentor": "mentor",
            "manager": "manager",
        }

        model_name = model_map.get(obj.name)
        if not model_name:
            return "Роль не имеет специфичных прав"

        try:
            ct = ContentType.objects.get(app_label="authentication", model=model_name)
            permissions = Permission.objects.filter(content_type=ct).exclude(
                codename__in=[
                    "add_" + model_name,
                    "change_" + model_name,
                    "delete_" + model_name,
                    "view_" + model_name,
                ]
            )

            if not permissions.exists():
                return "Нет кастомных прав"

            html = '<ul style="margin: 0; padding-left: 20px; line-height: 1.8;">'
            for perm in permissions:
                html += f'<li><code>authentication.{perm.codename}</code><br/><span style="color: #666;">{perm.name}</span></li>'
            html += "</ul>"
            return format_html(html)
        except ContentType.DoesNotExist:
            return "Модель не найдена"


@admin.register(ExpertiseArea)
class ExpertiseAreaAdmin(admin.ModelAdmin):
    """Админка для ExpertiseArea"""

    list_display = ["name", "mentors_count", "reviewers_count", "created_at"]
    search_fields = ["name", "description"]
    readonly_fields = ["created_at"]

    fieldsets = (
        ("Основная информация", {"fields": ("name", "description")}),
        ("Метаданные", {"fields": ("created_at",), "classes": ("collapse",)}),
    )

    @admin.display(description="Менторов")
    def mentors_count(self, obj):
        """Количество менторов с этой экспертизой"""
        return obj.mentors.count()

    @admin.display(description="Ревьюеров")
    def reviewers_count(self, obj):
        """Количество ревьюеров с этой экспертизой"""
        return obj.reviewers.count()


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Админка для Student"""

    list_display = [
        "user_email",
        "user_role_display",
        "phone",
        "country",
        "created_at",
    ]
    list_filter = [
        "country",
        "created_at",
        "email_notifications",
        "course_updates",
    ]
    search_fields = [
        "user__email",
        "user__first_name",
        "user__last_name",
        "bio",
    ]
    readonly_fields = ["created_at", "updated_at"]
    filter_horizontal = ["courses"]

    fieldsets = (
        ("Основная информация", {"fields": ("user", "bio", "avatar")}),
        (
            "Личные данные",
            {"fields": ("phone", "birthday", "gender", "country", "city", "address")},
        ),
        ("Курсы", {"fields": ("courses",), "classes": ("collapse",)}),
        (
            "Уведомления",
            {
                "fields": (
                    "email_notifications",
                    "course_updates",
                    "lesson_reminders",
                    "achievement_alerts",
                    "weekly_summary",
                    "marketing_emails",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Приватность",
            {
                "fields": (
                    "profile_visibility",
                    "show_progress",
                    "show_achievements",
                    "allow_messages",
                ),
                "classes": ("collapse",),
            },
        ),
        ("Метаданные", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    @admin.display(
        description="Email пользователя",
        ordering="user__email",
    )
    def user_email(self, obj):
        return obj.user.email

    @admin.display(
        description="Роль",
        ordering="user__role",
    )
    def user_role_display(self, obj):
        if obj.user and obj.user.role:
            return obj.user.role.get_name_display()
        return "-"


@admin.register(Reviewer)
class ReviewerAdmin(admin.ModelAdmin):
    """Админка для Reviewer"""

    list_display = [
        "user_email",
        "role_badge",
        "is_active",
        "total_reviews",
        "courses_count",
        "registered_at",
    ]
    list_filter = ["is_active", "registered_at", "courses", "expertise_areas"]
    search_fields = ["user__email", "user__first_name", "user__last_name", "bio"]
    filter_horizontal = ["courses", "expertise_areas"]
    readonly_fields = ["total_reviews", "average_review_time", "registered_at", "updated_at"]

    fieldsets = (
        ("Основная информация", {"fields": ("user", "bio")}),
        ("Экспертиза", {"fields": ("expertise_areas",)}),
        ("Курсы и статус", {"fields": ("courses", "is_active")}),
        (
            "Статистика",
            {"fields": ("total_reviews", "average_review_time"), "classes": ("collapse",)},
        ),
        ("Метаданные", {"fields": ("registered_at", "updated_at"), "classes": ("collapse",)}),
    )

    @admin.display(
        description="Email",
        ordering="user__email",
    )
    def user_email(self, obj):
        return obj.user.email

    @admin.display(description="Роль")
    def role_badge(self, obj):
        role = obj.get_role_display()
        colors = {"Ревьюер": "#10b981", "Ментор": "#3b82f6", "Проверяющий": "#6b7280"}
        color = colors.get(role, "#6b7280")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            role,
        )

    @admin.display(description="Курсов")
    def courses_count(self, obj):
        return obj.courses.count()


@admin.register(Mentor)
class MentorAdmin(admin.ModelAdmin):
    """Админка для Mentor"""

    list_display = ["user_email", "is_active", "courses_count", "registered_at"]
    list_filter = ["is_active", "registered_at", "courses", "expertise_areas"]
    search_fields = ["user__email", "user__first_name", "user__last_name", "bio"]
    filter_horizontal = ["courses", "expertise_areas"]
    readonly_fields = ["registered_at", "updated_at"]

    fieldsets = (
        ("Основная информация", {"fields": ("user", "bio")}),
        ("Экспертиза", {"fields": ("expertise_areas",)}),
        ("Курсы и статус", {"fields": ("courses", "is_active")}),
        ("Метаданные", {"fields": ("registered_at", "updated_at"), "classes": ("collapse",)}),
    )

    @admin.display(
        description="Email",
        ordering="user__email",
    )
    def user_email(self, obj):
        return obj.user.email

    @admin.display(description="Курсов")
    def courses_count(self, obj):
        return obj.courses.count()


@admin.register(Manager)
class ManagerAdmin(admin.ModelAdmin):
    """Админка для Manager"""

    list_display = ["user_email", "is_active", "registered_at"]
    list_filter = ["is_active", "registered_at"]
    search_fields = ["user__email", "user__first_name", "user__last_name", "bio"]
    readonly_fields = ["registered_at", "updated_at"]

    fieldsets = (
        ("Основная информация", {"fields": ("user", "bio")}),
        ("Статус", {"fields": ("is_active",)}),
        ("Метаданные", {"fields": ("registered_at", "updated_at"), "classes": ("collapse",)}),
    )

    @admin.display(
        description="Email",
        ordering="user__email",
    )
    def user_email(self, obj):
        return obj.user.email
