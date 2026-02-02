"""
Certificates URLs Module - URL маршруты для сертификатов.

URL patterns:
    /students/certificates/ - Список сертификатов студента
    /students/certificates/<pk>/ - Детали сертификата
    /students/certificates/<pk>/download/ - Скачать PDF
    /certificates/verify/<number>/ - Публичная верификация
    /certificates/verify/ - Форма верификации по коду

Автор: Pyland Team
Дата: 2026
"""

from django.urls import path

from . import views

app_name = "certificates"

urlpatterns = [
    # Для студентов (требуют авторизации)
    path("students/certificates/", views.certificates_list_view, name="list"),
    path("students/certificates/<int:pk>/", views.certificate_detail_view, name="detail"),
    path(
        "students/certificates/<int:pk>/download/", views.certificate_download_view, name="download"
    ),
    # Публичная верификация (без авторизации)
    path(
        "certificates/verify/<str:certificate_number>/",
        views.certificate_verify_view,
        name="verify",
    ),
    path("certificates/verify/", views.certificate_verify_by_code_view, name="verify_form"),
]
