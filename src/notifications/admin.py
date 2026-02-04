from django.contrib import admin
from django.utils.html import format_html

from .models import Subscription


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """
    Админка для централизованного управления подписками.

    Поддерживает все типы подписок (blog, courses, events, marketing, etc.)
    с удобной фильтрацией и массовыми действиями.
    """

    list_display = (
        "status_icon",
        "email",
        "subscription_type_display",
        "user_link",
        "created_at",
    )
    list_filter = (
        "subscription_type",
        "is_active",
        "created_at",
    )
    search_fields = (
        "email",
        "user__email",
        "user__first_name",
        "user__last_name",
    )
    ordering = ("-created_at",)
    list_editable = ()
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Основная информация", {"fields": ("email", "user", "subscription_type", "is_active")}),
        (
            "Настройки",
            {
                "fields": ("preferences",),
                "classes": ("collapse",),
                "description": 'JSON настройки: {"frequency": "weekly", "categories": ["python", "javascript"]}',
            },
        ),
        ("Метаданные", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    actions = [
        "activate_subscriptions",
        "deactivate_subscriptions",
        "export_to_csv",
    ]

    @admin.display(description="Статус")
    def status_icon(self, obj):
        """Иконка статуса подписки."""
        if obj.is_active:
            return format_html('<span style="color: green; font-size: 16px;">✅</span>')
        return format_html('<span style="color: gray; font-size: 16px;">❌</span>')

    @admin.display(description="Тип")
    def subscription_type_display(self, obj):
        """Красивое отображение типа подписки."""
        type_colors = {
            "blog": "#3b82f6",  # blue
            "courses": "#10b981",  # green
            "events": "#f59e0b",  # amber
            "marketing": "#ec4899",  # pink
            "system": "#6366f1",  # indigo
            "weekly_digest": "#8b5cf6",  # purple
        }
        color = type_colors.get(obj.subscription_type, "#6b7280")
        type_label = dict(Subscription.SUBSCRIPTION_TYPE_CHOICES).get(
            obj.subscription_type, obj.subscription_type
        )

        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px; font-weight: 500;">{}</span>',
            color,
            type_label,
        )

    @admin.display(description="Пользователь")
    def user_link(self, obj):
        """Ссылка на пользователя в админке."""
        if obj.user:
            from django.urls import reverse

            url = reverse("admin:authentication_user_change", args=[obj.user.pk])
            return format_html('<a href="{}">{}</a>', url, obj.user.email)
        return format_html('<span style="color: gray;">Анонимная</span>')

    @admin.action(description="✅ Активировать выбранные подписки")
    def activate_subscriptions(self, request, queryset):
        """Массовая активация подписок."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f"✅ Активировано подписок: {updated}")

    @admin.action(description="❌ Деактивировать выбранные подписки")
    def deactivate_subscriptions(self, request, queryset):
        """Массовая деактивация подписок."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"❌ Деактивировано подписок: {updated}")

    @admin.action(description="📥 Экспортировать в CSV")
    def export_to_csv(self, request, queryset):
        """Экспорт подписок в CSV."""
        import csv

        from django.http import HttpResponse

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="subscriptions.csv"'

        writer = csv.writer(response)
        writer.writerow(["Email", "Тип", "Активна", "Дата подписки"])

        for sub in queryset:
            writer.writerow(
                [
                    sub.email,
                    sub.get_subscription_type_display(),
                    "Да" if sub.is_active else "Нет",
                    sub.created_at.strftime("%Y-%m-%d %H:%M"),
                ]
            )

        return response
