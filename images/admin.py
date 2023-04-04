from django.contrib import admin
from images.models import Image, ImageSet

admin.site.register(ImageSet)
admin.site.register(Image)