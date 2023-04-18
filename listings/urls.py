from django.urls import path, include

import listings.views as views

app_name = 'listings'

urlpatterns = [
    path("", views.HX_List.as_view(), name="HX_List"),
    path("create/", views.ListingCreate.as_view(), name="create"),
]