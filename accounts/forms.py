from django.contrib.auth.forms import UserCreationForm
from accounts.models import User

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
