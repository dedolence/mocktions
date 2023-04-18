from django.urls import path, include

import listings.views as views

app_name = 'listings'

urlpatterns = [
    path("", views.List.as_view(), name="index"),
]