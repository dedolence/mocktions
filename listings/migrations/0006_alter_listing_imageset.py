# Generated by Django 4.1.2 on 2023-04-20 20:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("images", "0009_imageset_user"),
        ("listings", "0005_alter_listing_imageset"),
    ]

    operations = [
        migrations.AlterField(
            model_name="listing",
            name="imageset",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.RESTRICT,
                related_name="listing",
                to="images.imageset",
            ),
        ),
    ]
