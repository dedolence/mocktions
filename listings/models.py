from django.db import models
from mocktions.settings import AUTH_USER_MODEL as User
from base.models import TimeStampMixin
from globals import LISTING_DRAFT_EXPIRATION_DAYS
from django.utils.translation import gettext_lazy as _
from images.models import ImageSet
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator

def validate_images_added(pk_imageset):
    imageset = ImageSet.objects.get(pk=pk_imageset)
    if imageset.images.count() == 0:
        raise ValidationError(
            _("Listings must contain images.")
        )


def validate_max_images(pk_imageset):
    imageset = ImageSet.objects.get(pk=pk_imageset)
    if imageset.images.count() > imageset.max_size:
        raise ValidationError(
            _("This listing may have a maximum of %(max) \images."),
            params={"max": imageset.max_size},
        )


class Listing(TimeStampMixin, models.Model):
    class CategoryChoices(models.TextChoices):
        HAT = "H", _("Hats")
        ARTIFACT_BEN = "AB", _("Artifact (benevolent)")
        ARTIFACT_MAL = "AM", _("Artifact (malevolent)")
        THINGS_YELLOW = "TY", _("Things That Are Yellow")
        MIN_TUX = "MT", _("Mineral or Tuxedo")
        CONCEPT = "CO", _("Concepts, Decisions")

    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="listings",
        blank=False,
        null=False,
    )
    title = models.CharField(
        max_length=100,
        unique=True,
        blank=False,
        null=False,
    )
    description = models.CharField(
        max_length=500,
        blank=False,
        null=True,
    )
    starting_bid = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=False,
        null=False,
    )
    lifespan = models.IntegerField(
        default=LISTING_DRAFT_EXPIRATION_DAYS, 
        null=False, 
        blank=False, 
        help_text="days until listing expires, to a maximum of 30."
    )
    category = models.CharField(
        max_length=100,
        choices=CategoryChoices.choices,
        blank=False,
        null=False,
    )
    imageset = models.ForeignKey(
        ImageSet,
        blank=False,
        null=False,
        on_delete=models.RESTRICT,
        related_name="listing",
    )