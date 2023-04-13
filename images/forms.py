from django.forms import ModelForm, forms
from .models import Image
from django import forms

class BaseImageForm(forms.ModelForm):
    
    class Meta:
        model = Image
        fields = ('imageset',)

        widgets = {'imageset': forms.TextInput(attrs={'type': 'hidden'})}


class ImageUploadForm(BaseImageForm, ModelForm):
    error_css_class = "text-danger small"
    required_css_class = "text-danger small"

    class Meta:
        model = Image 
        fields = BaseImageForm.Meta.fields + ('image_field',)

        widgets = {
            'image_field': forms.ClearableFileInput(
                attrs={'class': 'form-control my-1', 'accept': 'image/*'}
            ),
            'imageset': BaseImageForm.Meta.widgets['imageset']
        }

        labels = {
            'image_field': ""
        }


class ImageFetchForm(BaseImageForm, forms.ModelForm):
    url = forms.URLField(
        widget=forms.URLInput(attrs={'class': 'form-control my-1'}),
        label=""
    )