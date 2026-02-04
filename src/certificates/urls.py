"""
Certificates URLs Module - URL маршруты для сертификатов.

URL patterns:
    Students (authenticated):
        /students/certificates/ - Список сертификатов студента
        /students/certificates/<pk>/ - Детали сертификата
        /students/certificates/<pk>/download/ - Скачать PDF

    Public:
        /certificates/verify/<number>/ - Публичная верификация
        /certificates/verify/ - Форма верификации по коду

Автор: Pyland Team
Дата: 2026
"""

from django.urls import path

from . import views

app_name = "certificates"

urlpatterns = [
    path("students/certificates/", views.certificates_list_view, name="list"),
    path(
        "students/certificates/<str:verification_code>/",
        views.certificate_detail_view,
        name="detail",
    ),
    path(
        "students/certificates/<str:verification_code>/download/",
        views.certificate_download_view,
        name="download",
    ),
    path(
        "certificates/verify/<str:verification_code>/",
        views.certificate_verify_view,
        name="verify",
    ),
    path("certificates/verify/", views.certificate_verify_by_code_view, name="verify_form"),
]
