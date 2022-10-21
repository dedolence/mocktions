from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from accounts.models import User
from django import forms
from .strings import en

class DeleteAccountForm(forms.Form):
    delete_confirmation = forms.BooleanField(
        label=en.DELETE_CONFIRMATION_CHECKBOX_LABEL, 
        widget=forms.CheckboxInput)


class LoginForm(AuthenticationForm):
    def __init__(self, request: any = ..., *args: any, **kwargs: any) -> None:
        super().__init__(request, *args, **kwargs)
        ''' Customize CSS to provide Bootstrap floating labels. '''

        self.fields['username'].widget.attrs.update(
            {'class': 'form-control'}
        )
        self.fields['password'].widget.attrs.update(
            {'class': 'form-control'}
        )


class RegistrationForm(UserCreationForm):

    class Meta:
        model = User
        fields = [
            'username',
            'password1', 
            'password2',
            'first_name',
            'last_name',
            'email', 
            'street',
            'city',
            'state',
            'postcode',
            'country',
            'phone'
            ]
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
