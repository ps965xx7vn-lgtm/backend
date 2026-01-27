"""
Courses URL Configuration

Маршруты для приложения курсов:
- Список всех доступных курсов
- Детальная страница курса с уроками

Публичный доступ для просмотра, авторизация для прохождения.
"""

from django.urls import path

from . import views

app_name = "courses"

urlpatterns = [
    path("", views.course_list_view, name="courses"),
    path("<slug:course_slug>/", views.course_detail_view, name="course_detail"),
]
