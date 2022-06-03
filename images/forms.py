from django import forms

class UploadImageForm(forms.Form):
    image = forms.ImageField()
    image_url = forms.CharField(widget=forms.HiddenInput())