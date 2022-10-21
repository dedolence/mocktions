from django.urls import path
import accounts.views as views
from django.urls import reverse, reverse_lazy

app_name = 'accounts'
urlpatterns = [
    path('', views.index, name="index"),
    path('delete/<int:pk>', views.DeleteAccount.as_view(), name='delete_account'),
    path('login/',  views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('profile/<int:pk>', views.Profile.as_view(), name='profile'),
    path('register/', views.Register.as_view(), name='register'),
]