"""
Manager Admin Configuration.

Admin configuration for manager-related models including ManagerNote.

Author: Pyland Team
Date: 2025
"""

from django.contrib import admin

from .models import ManagerNote


@admin.register(ManagerNote)
class ManagerNoteAdmin(admin.ModelAdmin):
    """Админка для заметок менеджеров."""

    list_display = ["user_email", "manager_email", "note_preview", "created_at"]
    list_filter = ["created_at", "manager"]
    search_fields = ["user__email", "manager__email", "note"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        ("Информация", {"fields": ("user", "manager", "note")}),
        ("Метаданные", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    @admin.display(description="Пользователь", ordering="user__email")
    def user_email(self, obj):
        return obj.user.email

    @admin.display(description="Менеджер", ordering="manager__email")
    def manager_email(self, obj):
        return obj.manager.email

    @admin.display(description="Комментарий")
    def note_preview(self, obj):
        return obj.note[:50] + "..." if len(obj.note) > 50 else obj.note
