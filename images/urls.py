from django.urls import path
import images.views as views

app_name = "images"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
]