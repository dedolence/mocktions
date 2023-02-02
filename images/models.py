from django.db import models
from django.urls import reverse
from mocktions.settings import AUTH_USER_MODEL as User
from django.core.files.storage import default_storage

class Image(models.Model):
    image_field = models.ImageField(
        upload_to = "user_uploads", 
        storage = default_storage,
        height_field = None, 
        width_field = None, 
        max_length = None
    )
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse("images:update", kwargs={"pk": self.pk})
    