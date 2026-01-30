"""
Payments URL Configuration

Маршруты для приложения платежей:
- Оформление заказа (checkout) для покупки курсов
- Страницы успеха и отмены платежа
- Webhook endpoints для CloudPayments и TBC Bank

Требуется авторизация для всех views кроме webhooks.
"""

from django.urls import path

from . import views

app_name = "payments"

urlpatterns = [
    # Страница оформления заказа
    path("checkout/<slug:course_slug>/", views.checkout_view, name="checkout"),
    # Страницы результатов оплаты
    path("success/<uuid:payment_id>/", views.payment_success_view, name="payment_success"),
    path("cancel/<uuid:payment_id>/", views.payment_cancel_view, name="payment_cancel"),
    # TODO: Webhooks для платежных систем (будут добавлены в API)
    # path("webhook/cloudpayments/", views.cloudpayments_webhook, name="cloudpayments_webhook"),
    # path("webhook/tbc/", views.tbc_webhook, name="tbc_webhook"),
]
