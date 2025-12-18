"""
Core URL Configuration

Маршруты для основных страниц приложения:
- Главная страница (home)
- Страница контактов (contacts)
- Страница "О нас" (about)
- Редирект по ролям (home_redirect)
- Юридические страницы в соответствии с законодательством Грузии:
  * terms_of_service - Условия использования
  * privacy_policy - Политика конфиденциальности
  * data_processing - Согласие на обработку персональных данных
  * refund_policy - Политика возвратов
  * cookies_policy - Политика использования cookie
  * public_offer - Публичная оферта
  * payment_policy - Правила оплаты
  * platform_rules - Правила использования платформы

URL namespace: 'core'
"""

from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("contacts/", views.contacts, name="contacts"),
    path("about/", views.about, name="about"),
    path(
        "dashboard/", views.home, name="dashboard"
    ),  # Роутер dashboard по ролям (декоратор на home)
    # Юридические страницы
    path("terms-of-service/", views.terms_of_service, name="terms_of_service"),
    path("privacy-policy/", views.privacy_policy, name="privacy_policy"),
    path("data-processing/", views.data_processing, name="data_processing"),
    path("refund-policy/", views.refund_policy, name="refund_policy"),
    path("cookies-policy/", views.cookies_policy, name="cookies_policy"),
    path("public-offer/", views.public_offer, name="public_offer"),
    path("payment-policy/", views.payment_policy, name="payment_policy"),
    path("platform-rules/", views.platform_rules, name="platform_rules"),
]
