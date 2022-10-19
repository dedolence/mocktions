from django.urls import path, include
from django.contrib.auth import views as auth_views
import accounts.views as views
import mocktions.settings as settings
from django.urls import reverse

app_name = 'accounts'
urlpatterns = [
    path('', views.index, name="index"),
    path('login/', 
        auth_views.LoginView.as_view(
            template_name = 'accounts/html/templates/login.html',
        ), 
        name="login"),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('profile/', views.Profile.as_view(), name="profile"),
    path('register/', views.Register.as_view(), name="register"),
]