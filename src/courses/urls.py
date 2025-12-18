from django.urls import path

from . import views

app_name = "courses"

urlpatterns = [
    path("", views.course_list_view, name="courses"),
    path("<slug:course_slug>/", views.course_detail_view, name="course_detail"),
]
