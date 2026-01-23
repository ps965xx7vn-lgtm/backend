"""
Notifications URL Configuration

Маршруты для приложения уведомлений:
- Управление подписками на уведомления
- Настройки каналов доставки (email, SMS, Telegram)

Требуется авторизация.
"""

from django.urls import path

from . import views

app_name = "notifications"

urlpatterns = [
    path("subscribe/", views.subscribe_view, name="subscribe"),
]
