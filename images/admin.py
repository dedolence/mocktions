from django.contrib import admin
from images.models import Image
from typing import Any
from django.http import HttpRequest

class ImageAdmin(admin.ModelAdmin):

    def save_model(self, request: Any, obj: Image, form: Any, change: Any) -> None:
        obj.user = request.user
        return super().save_model(request, obj, form, change)

    def delete_model(self, request: HttpRequest, obj: Image) -> None:
        return False

admin.site.register(Image)