from django.urls import path, include
from .uploader import *

app_name = 'images'

urlpatterns = [
    path('hx-upload', HX_Upload.as_view(), name="hx_upload"),
    path('hx-fetch', HX_Upload.as_view(), name="hx_fetch"),
    path('hx-load/<int:pk>', HX_LoadForm.as_view(), name="hx-load"),
    path('hx-load/', HX_LoadForm.as_view(), name="hx-load"),
    path('hx-update/<int:pk>', HX_Update.as_view(), name="hx-update"),
    path('hx-destroy/<int:pk>', HX_Destroy.as_view(), name="hx-destroy"),
]