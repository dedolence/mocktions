from django.forms import ModelForm, forms
from .models import Image
from django import forms

class ImageUploadForm(ModelForm):
    image_field = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={'multiple': True})
    )

    class Meta:
        model = Image
        fields = ["image_field"]