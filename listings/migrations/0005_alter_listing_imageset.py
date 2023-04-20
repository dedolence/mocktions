# Generated by Django 4.1.2 on 2023-04-20 19:47

from django.db import migrations, models
import django.db.models.deletion
import listings.models


class Migration(migrations.Migration):

    dependencies = [
        ("images", "0009_imageset_user"),
        ("listings", "0004_alter_listing_imageset"),
    ]

    operations = [
        migrations.AlterField(
            model_name="listing",
            name="imageset",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.RESTRICT,
                related_name="listing",
                to="images.imageset",
                validators=[
                    listings.models.validate_images_added,
                    listings.models.validate_max_images,
                ],
            ),
        ),
    ]
