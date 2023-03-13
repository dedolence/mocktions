from rest_framework import serializers
from images.models import Image


class ImageUploadSerializer(serializers.ModelSerializer):
    image_field = serializers.ImageField(
        label = "",
        style = {'template': 'images/html/includes/file_input.html'}
    )
    class Meta:
        model = Image
        fields = ["image_field"]

class ImageURLSerializer(serializers.Serializer):
    url = serializers.URLField(
        label = "",
        style = {'template': 'images/html/includes/url_input.html'}
    )