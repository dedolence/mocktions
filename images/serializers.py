from rest_framework import serializers
from images.models import Image


class ImageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ["image_field"]