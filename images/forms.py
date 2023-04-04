from django.forms import ModelForm, forms
from .models import Image
from django import forms

class FileInput(forms.ClearableFileInput):
    template_name="mocktions/images/html/includes/file_input.html"

class ImageUploadForm(ModelForm):
    image_field = forms.ImageField(
        widget=forms.ClearableFileInput(
            attrs={'class': 'form-control', 'accept': 'image/*'}
        ),
        label=""
    )
    class Meta:
        model = Image
        fields = ["image_field"]


class ImageFetchForm(forms.Form):
    url = forms.URLField(
        widget=forms.URLInput(attrs={'class': 'form-control'}),
        label=""
    )