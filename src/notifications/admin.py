from django.contrib import admin

from .models import Subscription


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """
    Админка для модели Subscription.

    Позволяет управлять email-подписками на уведомления. В списке отображаются email, статус активности и дата создания.
    """

    list_display = ("email", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("email",)
    ordering = ("-created_at",)
    list_editable = ("is_active",)
    date_hierarchy = "created_at"
    readonly_fields = ("created_at",)
