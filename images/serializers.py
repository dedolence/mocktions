from rest_framework import serializers
from images.models import Image

from django.template.defaultfilters import filesizeformat
from typing import Any, Optional, Iterable
from django.forms import ValidationError
from mocktions.settings import UPLOAD_MAX_SIZE
from django.db import models
from django.utils.translation import gettext as _
from sys import getsizeof

ALLOWED_CONTENT_TYPES = [
    "image/png",
    "image/jpg",
    "image/jpeg",
    "image/bmp",
    "image/tiff",
    "image/webp",
]

def type_validator(value: models.ImageField) -> ValidationError | None:
    print("Image type is:", value.file.content_type)
    return value.file.content_type in ALLOWED_CONTENT_TYPES

def size_validator(value: models.ImageField) -> ValidationError | None:
    """
        This worked whereas sys.getsizeof (and __sizeof__()) didn't.
        getvalue() also worked but I think that has to copy the file
        into another memory chunk to tell, and this method with tell()
        doesn't.

        At least according to: https://stackoverflow.com/a/54030779/9137423
    """
    file = value.file
    file.seek(0,2)
    size = value.file.tell()
    return size < UPLOAD_MAX_SIZE
    
class ImageUploadSerializer(serializers.ModelSerializer):

    def validate_image_field(self, value):
        if not size_validator(value):
            raise ValidationError(_(
                "Image is too large. Images must be less than {max_size}".format(
                    max_size = filesizeformat(UPLOAD_MAX_SIZE))
            ))
        """
        if not type_validator(value):
            raise ValidationError(_("Invalid image type. Allowed types: png, jpg/jpeg, bmp, tiff, webp.")) """       
        return value

    class Meta:
        model = Image
        fields = "__all__"
