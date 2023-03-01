from django.db import models
from django.urls import reverse
from django.core.files.storage import default_storage
from django.utils.translation import gettext as _
from rest_framework.permissions import BasePermission
from django.contrib.auth import get_user_model

User = get_user_model()

ALLOWED_CONTENT_TYPES = [
    "image/png",
    "image/jpg",
    "image/jpeg",
    "image/bmp",
    "image/tiff",
    "image/webp",
]

class CanUploadImages(BasePermission):
    """
        Placeholder in case I want to limit image uploads to specific
        users later.
    """
    def has_permission(self, request, view):
        return True


# These don't work with DRF
""" def type_validator(value: models.ImageField) -> ValidationError | None:
    if value._file.content_type not in ALLOWED_CONTENT_TYPES:
        raise ValidationError(_("Invalid image type. Allowed types: png, jpg/jpeg, bmp, tiff, webp."))

def size_validator(value: models.ImageField) -> ValidationError | None:
    if value._file.size > UPLOAD_MAX_SIZE:
        raise ValidationError(_(
            "Image is too large. Images must be less than {max_size}".format(max_size = filesizeformat(UPLOAD_MAX_SIZE))
        )) """

class Image(models.Model):
    image_field = models.ImageField(
        upload_to = "user_uploads", 
        storage = default_storage,
        height_field = None, 
        width_field = None, 
        max_length = None,

        # these go with the serializer; if they're here they don't recognize the _file attribute
        #validators=[type_validator, size_validator]
    )
    uploaded_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="images"
    )

    def get_absolute_url(self):
        return reverse("images:update", kwargs={"pk": self.pk})

    def __str__(self) -> str:
        return f"Image id={self.pk}, uploaded by {self.uploaded_by}."