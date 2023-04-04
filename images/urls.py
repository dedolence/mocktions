from django.urls import path, include
from .uploader import *

app_name = 'images'

urlpatterns = [
    path('hx-upload', HX_Upload.as_view(), name="hx_upload"),
    path('hx-fetch', HX_Upload.as_view(), name="hx_fetch"),
    path('hx-load', HX_LoadForm.as_view(), name="hx-load"),
    path('hx-detail', HX_Detail.as_view(), name="hx-detail"),
    path('hx-update/<int:pk>', HX_Update.as_view(), name="hx-update"),
    path('hx-destroy', HX_Destroy.as_view(), name="hx-destroy"),
]