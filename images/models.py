from django.db import models
from django.urls import reverse
from django_backblaze_b2 import BackblazeB2Storage
from django_backblaze_b2 import PublicStorage, StaffStorage, LoggedInStorage
from mocktions.settings import AUTH_USER_MODEL as User


class Image(models.Model):
    image_field = models.ImageField(
        upload_to = "images/user_uploads", 
        storage = PublicStorage,
        height_field = None, 
        width_field = None, 
        max_length = None
    )
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse("images:update", kwargs={"pk": self.pk})
    