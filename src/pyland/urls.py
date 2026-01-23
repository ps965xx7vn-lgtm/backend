"""
Pyland URL Configuration

Главная конфигурация URL маршрутов платформы Pyland School.

Маршруты:
    Admin Panel:
        - /admin/ - Django административная панель

    API:
        - /api/ - REST API (Django Ninja) для всех приложений

    Internationalization:
        - /i18n/ - Переключение языков (ru, en, ka)

    Social Authentication:
        - /social-auth/ - OAuth вход через соцсети

    Applications (с поддержкой i18n):
        - / - Основные страницы (core)
        - /authentication/ - Аутентификация и регистрация
        - /students/ - Личный кабинет студента
        - /reviewers/ - Панель ревьюера/ментора
        - /courses/ - Каталог и детали курсов
        - /blog/ - Блог и статьи
        - /payments/ - Платежи и покупки
        - /notifications/ - Управление уведомлениями
        - /managers/ - Административная панель (staff only)

Особенности:
    - Все приложения поддерживают мультиязычность через i18n_patterns
    - prefix_default_language=True добавляет префикс языка для всех URL
    - В DEBUG режиме подключается Django Debug Toolbar
    - Статические файлы и медиа обслуживаются Django в DEV

Автор: Pyland Team
Дата: 2025
"""

from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from pyland.api import api

urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
    path("api/", api.urls),
    path("social-auth/", include("social_django.urls", namespace="social")),
]

# i18n для обычных Django view
urlpatterns += i18n_patterns(
    path("", include("core.urls")),
    path("authentication/", include("authentication.urls")),
    path("students/", include("students.urls")),
    path("reviewers/", include("reviewers.urls")),
    path("courses/", include("courses.urls")),
    path("blog/", include("blog.urls")),
    path("payments/", include("payments.urls")),
    path("notifications/", include("notifications.urls")),
    path("managers/", include("managers.urls")),
    prefix_default_language=True,
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += debug_toolbar_urls()
