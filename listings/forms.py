from typing import Any, Dict

import django.forms as forms
from django.core.exceptions import ValidationError

from images.models import ImageSet
from listings.models import Listing

from django.utils.translation import gettext_lazy as _


class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        exclude = ["user", "imageset"]
        widgets = {
            "description": forms.Textarea(),
        }

    def clean_imageset(self):
        cd = self.cleaned_data
        imageset = cd.get("imageset")
        if imageset.images.count() == 0:
            raise ValidationError(_("A listing must contain at least one image."))
        
        if imageset.images.count() > imageset.max_size:
            raise ValidationError(
                _(f"Too many images. This listing can have a maximum of {imageset.max_size} images.")
            )