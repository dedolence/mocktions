from django.db import models
import pathlib
from uuid import uuid4

# Adapted from this guide:
# https://www.hacksoft.io/blog/direct-to-s3-file-upload-with-django

def image_generate_upload_path(instance, filename):
    return f"images/{instance.file_name}"

""" class Image(models.Model):
    image = models.ImageField(
        upload_to=image_generate_upload_path,
        null=True,
        blank=True,
    ) """

def file_generate_name(original_file_name):
    """
        Generates unique file name but preserves file extension.
    """
    extension = pathlib.Path(original_file_name).suffix

    return f"{uuid4().hex}{extension}"