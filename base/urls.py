from django.urls import path, include
from . import views

app_name = 'base'
urlpatterns = [
    path("", views.index, name="index"),
    path("", include("django_backblaze_b2.urls")),
    path("images/", include("images.urls", namespace="images"))
]
