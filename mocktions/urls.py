from django.contrib import admin
from django.urls import path, include
from django.conf.urls import handler400, handler500, handler403
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('base.urls', namespace='base')),
    path('', include("django_backblaze_b2.urls", namespace="b2")),
    path('accounts/', include('accounts.urls', namespace="accounts")),
    path('images/', include("images.urls", namespace="images")),
    path('listings/', include('listings.urls', namespace='listings')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


handler404 = 'base.views.handler404'
handler500 = 'base.views.handler500'
handler403 = 'base.views.handler403'