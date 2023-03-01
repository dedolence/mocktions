from django.urls import path
import images.views as views
from rest_framework.generics import ListCreateAPIView
import images.api as api
from images.models import Image
from images.serializers import ImageUploadSerializer

app_name = 'images'
urlpatterns = [
    path("", views.ImageListView.as_view(), name="index"),
    path("add/", views.ImageCreateView.as_view(), name="add"),
    path("add/", views.ImageCreateView.as_view(), name="create"),   #redundant because i can never remember
    path("<int:pk>/", views.ImageUpdateView.as_view(), name="update"),
    path("delete/<int:pk>", views.ImageDeleteView.as_view(), name="delete"),

    path("add_drf/", views.ImageUpload.as_view(), name="add_drf"),
]