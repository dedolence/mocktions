from django.urls import path, include

import listings.views as views

app_name = 'listings'

urlpatterns = [
    path("", views.HX_List.as_view(), name="HX_List"),
    path("create/", views.ListingCreate.as_view(), name="create"),
    path("randomize/", views.ListingRandomizer.as_view(), name="randomize"),
    path("detail/<int:pk>", views.ListingDetail.as_view(), name="detail"),
    path("update/<int:pk>", views.ListingUpdate.as_view(), name="update"),
    path("delete/<int:pk>", views.ListingDelete.as_view(), name="delete"),
]