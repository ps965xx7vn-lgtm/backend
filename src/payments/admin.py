"""
Payments Admin Module - Административный интерфейс Django для управления платежами.

Этот модуль содержит настройки Django Admin для моделей платежей:

ModelAdmin классы:
    - PaymentAdmin: Управление платежами
        - Отображение статусов с цветными индикаторами
        - Фильтры по статусу, методу оплаты, дате, валюте
        - Поиск по пользователю, курсу, transaction_id
        - Ссылки на пользователя и курс
        - Красивое отображение методов оплаты и валют
        - Только чтение (изменения через API/views)

Особенности:
    - Визуализация статусов платежей (зелёный/жёлтый/красный)
    - Иконки для методов оплаты
    - Форматирование сумм с символами валют
    - История изменений
    - Возможность рефанда через actions

Автор: Pyland Team
Дата: 2025
"""

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    Административная панель для управления платежами.

    Features:
        - Красивое отображение статусов с цветовой индикацией
        - Иконка для метода оплаты (Paddle)
        - Форматирование сумм с символами валют
        - Фильтры по статусу, методу оплаты, валюте, дате
        - Поиск по транзакциям, email пользователя, названию курса
        - Ссылки на связанные объекты
        - Action для возврата средств
    """

    list_display = (
        "id",
        "colored_status",
        "user_link",
        "course_link",
        "formatted_amount",
        "payment_method_display",
        "transaction_id",
        "created_at",
    )

    list_filter = (
        "status",
        "payment_method",
        "currency",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "transaction_id",
        "user__email",
        "user__first_name",
        "user__last_name",
        "course__title",
        "extra_data",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "colored_status",
        "user_link",
        "course_link",
        "formatted_amount",
        "payment_method_display",
        "transaction_id",
        "payment_url",
        "extra_data",
    )

    fieldsets = (
        (
            "Основная информация",
            {
                "fields": (
                    "id",
                    "colored_status",
                    "user_link",
                    "course_link",
                )
            },
        ),
        (
            "Детали платежа",
            {
                "fields": (
                    "formatted_amount",
                    "payment_method_display",
                    "transaction_id",
                    "payment_url",
                )
            },
        ),
        (
            "Дополнительные данные",
            {
                "fields": ("extra_data",),
                "classes": ("collapse",),
            },
        ),
        (
            "Временные метки",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    list_per_page = 50

    actions = ["mark_as_refunded"]

    @admin.display(
        description=_("Статус"),
        ordering="status",
    )
    def colored_status(self, obj: Payment) -> str:
        """
        Отображает статус платежа с цветовой индикацией.

        Args:
            obj: Экземпляр Payment

        Returns:
            HTML с цветным бейджем статуса
        """
        colors = {
            "pending": "#f59e0b",
            "processing": "#3b82f6",
            "completed": "#10b981",
            "failed": "#ef4444",
            "cancelled": "#6b7280",
            "refunded": "#8b5cf6",
        }

        status_labels = {
            "pending": "⏳ Ожидает",
            "processing": "🔄 Обработка",
            "completed": "✅ Завершён",
            "failed": "❌ Ошибка",
            "cancelled": "🚫 Отменён",
            "refunded": "↩️ Возврат",
        }

        color = colors.get(obj.status, "#6b7280")
        label = status_labels.get(obj.status, obj.get_status_display())

        return str(
            format_html(
                '<span style="background-color: {}; color: white; padding: 4px 12px; '
                "border-radius: 12px; font-weight: 600; font-size: 12px; "
                'display: inline-block; white-space: nowrap;">{}</span>',
                color,
                label,
            )
        )

    @admin.display(
        description=_("Пользователь"),
        ordering="user__email",
    )
    def user_link(self, obj: Payment) -> str:
        """
        Создаёт ссылку на пользователя в админке.

        Args:
            obj: Экземпляр Payment

        Returns:
            HTML со ссылкой на пользователя
        """
        if obj.user:
            url = reverse("admin:authentication_user_change", args=[obj.user.pk])
            return str(
                format_html(
                    '<a href="{}" target="_blank">👤 {} ({})</a>',
                    url,
                    obj.user.get_full_name() or obj.user.email,
                    obj.user.email,
                )
            )
        return "-"

    @admin.display(
        description=_("Курс"),
        ordering="course__name",
    )
    def course_link(self, obj: Payment) -> str:
        """
        Создаёт ссылку на курс в админке.

        Args:
            obj: Экземпляр Payment

        Returns:
            HTML со ссылкой на курс
        """
        if obj.course:
            url = reverse("admin:courses_course_change", args=[obj.course.pk])
            return str(format_html('<a href="{}" target="_blank">📚 {}</a>', url, obj.course.name))
        return "-"

    @admin.display(
        description=_("Сумма"),
        ordering="amount",
    )
    def formatted_amount(self, obj: Payment) -> str:
        """
        Форматирует сумму с символом валюты.

        Args:
            obj: Экземпляр Payment

        Returns:
            Отформатированная строка с суммой
        """
        currency_symbols = {
            "USD": "$",
            "EUR": "€",
            "RUB": "₽",
            "GEL": "₾",
        }

        symbol = currency_symbols.get(obj.currency, obj.currency)
        amount_formatted = f"{obj.amount:.2f}"

        return str(
            format_html(
                '<span style="font-weight: 700; color: #059669; font-size: 14px;">{}{}</span>',
                symbol,
                amount_formatted,
            )
        )

    @admin.display(
        description=_("Метод оплаты"),
        ordering="payment_method",
    )
    def payment_method_display(self, obj: Payment) -> str:
        """
        Отображает метод оплаты с иконкой.

        Args:
            obj: Экземпляр Payment

        Returns:
            HTML с иконкой и названием метода
        """
        methods = {
            "paddle": ("🌊", "Paddle Billing", "#4f46e5"),
        }

        icon, name, color = methods.get(
            obj.payment_method, ("💰", obj.get_payment_method_display(), "#6b7280")
        )

        return str(
            format_html(
                '<span style="color: {}; font-weight: 600;">{} {}</span>', color, icon, name
            )
        )

    @admin.action(description=_("Вернуть средства (refund)"))
    def mark_as_refunded(self, request, queryset):
        """
        Action для массового возврата платежей.

        Args:
            request: HTTP запрос
            queryset: Выбранные платежи
        """
        refunded_count = 0
        for payment in queryset:
            if payment.can_be_refunded():
                payment.status = "refunded"
                payment.save()
                refunded_count += 1

        self.message_user(
            request, f"Успешно возвращено платежей: {refunded_count} из {queryset.count()}"
        )

    def get_queryset(self, request):
        """
        Оптимизирует запросы с prefetch_related для связанных объектов.

        Args:
            request: HTTP запрос

        Returns:
            Оптимизированный QuerySet
        """
        qs = super().get_queryset(request)
        return qs.select_related("user", "course")

    def has_add_permission(self, request):
        """
        Запрещает создание платежей через админку.
        Платежи создаются только через API/views.

        Args:
            request: HTTP запрос

        Returns:
            False - создание запрещено
        """
        return False

    def has_change_permission(self, request, obj=None):
        """
        Запрещает изменение платежей через админку.
        Изменения только через API/views.

        Args:
            request: HTTP запрос
            obj: Экземпляр Payment (опционально)

        Returns:
            False - изменение запрещено
        """
        return False

    def has_delete_permission(self, request, obj=None):
        """
        Разрешает удаление только суперпользователям.

        Args:
            request: HTTP запрос
            obj: Экземпляр Payment (опционально)

        Returns:
            True если суперпользователь, иначе False
        """
        return request.user.is_superuser
