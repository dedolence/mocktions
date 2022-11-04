from django.contrib import admin
from django.urls import path, include
from django.conf.urls import handler400, handler500, handler403

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('base.urls', namespace='base')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
]


handler404 = 'base.views.handler404'
handler500 = 'base.views.handler500'
handler403 = 'base.views.handler403'