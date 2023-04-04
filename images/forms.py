from django.forms import ModelForm, forms
from .models import Image
from django import forms

class BaseImageForm(forms.Form):
    pass

class ImageUploadForm(BaseImageForm, ModelForm):
    error_css_class = "text-danger small"
    required_css_class = "text-danger small"

    class Meta:
        model = Image 
        fields = ('image_field', 'imageset')

        widgets = {
            'image_field': forms.ClearableFileInput(
                attrs={'class': 'form-control my-1', 'accept': 'image/*'}
            ),
            'imageset': forms.TextInput(attrs={'type': 'hidden'})
        }

        labels = {
            'image_field': ""
        }


class ImageFetchForm(forms.Form):
    url = forms.URLField(
        widget=forms.URLInput(attrs={'class': 'form-control my-1'}),
        label=""
    )
    imageset = forms.TextInput(attrs={'type': 'hidden'})