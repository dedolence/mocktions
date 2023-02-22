from django.urls import path
import images.views as views

app_name = 'images'
urlpatterns = [
    path("", views.ImageListView.as_view(), name="index"),
    path("add/", views.ImageCreateView.as_view(), name="add"),
    path("add/", views.ImageCreateView.as_view(), name="create"),   #redundant because i can never remember
    path("<int:pk>/", views.ImageUpdateView.as_view(), name="update"),
    path("delete/<int:pk>", views.ImageDeleteView.as_view(), name="delete"),

    # delete this
    path("test_click/", views.TestPath.as_view(), name="test_click"),

    # test return an image for use inline
    path("add_inline/", views.ImageAddInline.as_view(), name="add_image_inline"),
]