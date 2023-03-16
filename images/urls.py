from django.urls import path, include
import images.views as views
from rest_framework.generics import ListCreateAPIView
from images.api import ImageViewSet
from rest_framework import routers

app_name = 'images'

router = routers.SimpleRouter()
router.register('', ImageViewSet, basename="image")

urlpatterns = [
    path('test/', views.test_view, name="test-create"),
    path('', include(router.urls)),
]