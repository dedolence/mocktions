from django.urls import include, path
from . import views

app_name = 'images'
urlpatterns = [
    path('', views.index, name="index"),
    path('sign_s3', views.sign_s3, name="sign_s3"),
    path('post_image', views.post_image, name="post_image"),
]