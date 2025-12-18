"""
Authentication URL Configuration

Маршруты для системы аутентификации:
- Вход и регистрация пользователей
- Подтверждение email адреса
- Восстановление пароля
- Выход из системы

Все маршруты используют function-based views для простоты и ясности логики.
"""

from __future__ import annotations

from django.urls import path

from . import views

app_name = "authentication"

urlpatterns = [
    # =========================
    # Аутентификация
    # =========================
    path("signin/", views.signin_view, name="signin"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.user_logout, name="logout"),
    # =========================
    # Подтверждение email
    # =========================
    path(
        "verify-email-confirm/<uidb64>/<token>/",
        views.verify_email_confirm,
        name="verify_email_confirm",
    ),
    path(
        "resend-verification-email/",
        views.resend_verification_email,
        name="resend_verification_email",
    ),
    # =========================
    # Сброс пароля
    # =========================
    path("password-reset/", views.password_reset_view, name="password_reset"),
    path(
        "reset-password/<uidb64>/<token>/",
        views.password_reset_confirm,
        name="password_reset_confirm",
    ),
]
