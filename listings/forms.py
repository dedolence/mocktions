import django.forms as forms
from listings.models import Listing

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        exclude = ["user"]
