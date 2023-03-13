from django.db import models
from django.urls import reverse
from mocktions.settings import AUTH_USER_MODEL as User, UPLOAD_MAX_SIZE
from django.core.files.storage import default_storage
from typing import Any, Optional, Iterable
from django.forms import ValidationError
from django.utils.translation import gettext as _
from django.template.defaultfilters import filesizeformat


ALLOWED_CONTENT_TYPES = [
    "image/png",
    "image/jpg",
    "image/jpeg",
    "image/bmp",
    "image/tiff",
    "image/webp",
]

def type_validator(value: models.ImageField) -> ValidationError | None:
    if value._file.content_type not in ALLOWED_CONTENT_TYPES:
        raise ValidationError(_("Invalid image type. Allowed types: png, jpg/jpeg, bmp, tiff, webp."))

def size_validator(value: models.ImageField) -> ValidationError | None:
    if value._file.size > UPLOAD_MAX_SIZE:
        raise ValidationError(_(
            "Image is too large. Images must be less than {max_size}".format(max_size = filesizeformat(UPLOAD_MAX_SIZE))
        ))

class Image(models.Model):
    image_field = models.ImageField(
        upload_to = "user_uploads", 
        storage = default_storage,
        height_field = None, 
        width_field = None, 
        max_length = None,
        #validators=[type_validator, size_validator]
    )
    uploaded_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="images"
    )

    def get_absolute_url(self):
        return reverse("images:update", kwargs={"pk": self.pk})

    def __str__(self) -> str:
        return f"Image id={self.pk}, uploaded by {self.uploaded_by}."
    
    class Meta:
        ordering = ['-pk']