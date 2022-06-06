from django.db import models
from django.db.models import CASCADE

# Adapted from this guide:
# https://www.hacksoft.io/blog/direct-to-s3-file-upload-with-django

""" class ProfileImage(models.Model):
    
    path = models.CharField(
        max_length=200, 
        blank=False, 
        null=False
    )

    user = models.ForeignKey(
        'accounts.User', 
        on_delete=CASCADE, 
        related_name="profile_picture"
    ) """