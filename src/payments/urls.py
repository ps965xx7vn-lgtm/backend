"""
Payments URL Configuration

Маршруты для приложения платежей через Paddle Billing:
- Оформление заказа (checkout) для покупки курсов
- Paddle checkout handler для Retain feature
- Страницы успеха и отмены платежа

Требуется авторизация для всех views.
Webhooks от Paddle обрабатываются в API модуле.
"""

from django.urls import path

from . import views

app_name = "payments"

urlpatterns = [
    path("checkout/<slug:course_slug>/", views.checkout_view, name="checkout"),
    path("paddle-checkout/", views.paddle_checkout_handler, name="paddle_checkout"),
    path("success/<uuid:payment_id>/", views.payment_success_view, name="payment_success"),
    path("cancel/<uuid:payment_id>/", views.payment_cancel_view, name="payment_cancel"),
]
