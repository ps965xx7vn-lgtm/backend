from django.urls import path

from . import views

app_name = "payments"

urlpatterns = [
    path("purchase/<slug:course_slug>/", views.purchase_view, name="purchase"),
]
