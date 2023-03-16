from django import forms

class TestForm(forms.Form):
    button = forms.CharField(max_length=50, required=False)