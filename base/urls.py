from django.urls import path, include
from . import views

app_name = 'base'
urlpatterns = [
    path("", views.index, name="index"),
    path("images/", include("images.urls", namespace="images"))
]
