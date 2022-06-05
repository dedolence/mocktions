from django.urls import include, path
from . import views

app_name = 'site'
urlpatterns = [
    path('', views.index, name="index"),
    ]