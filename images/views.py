from django.views.generic import CreateView
from images.models import Image

class ImageUpload(CreateView):
    model = Image