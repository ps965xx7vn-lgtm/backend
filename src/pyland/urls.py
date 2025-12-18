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
    # Подключаем NinjaAPI с уникальным namespace
    path("api/", api.urls),
    # Подключаем вход через соцсети
    path("social-auth/", include("social_django.urls", namespace="social")),
]

# i18n для обычных Django view
urlpatterns += i18n_patterns(
    path("", include("core.urls")),
    path("authentication/", include("authentication.urls")),  # Аутентификация
    path("students/", include("students.urls")),  # Личный кабинет студента
    path("reviewers/", include("reviewers.urls")),  # Проверка работ (ревьюеры и менторы)
    path("courses/", include("courses.urls")),
    path("blog/", include("blog.urls")),
    path("payments/", include("payments.urls")),
    path("notifications/", include("notifications.urls")),
    path("managers/", include("managers.urls")),  # Административная панель (требует staff прав)
    prefix_default_language=True,
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += debug_toolbar_urls()
