from django.urls import path
import images.views as views

app_name = 'images'
urlpatterns = [
    path("", views.ImageCreateView.as_view(), name="add"),
    path("<int:pk>/", views.ImageUpdateView.as_view(), name="update"),
    path("<int:pk>/delete", views.ImageDeleteView.as_view(), name="delete"),
]