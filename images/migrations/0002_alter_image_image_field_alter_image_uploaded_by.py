# Generated by Django 4.1.2 on 2023-02-16 03:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import images.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("images", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="image",
            name="image_field",
            field=models.ImageField(
                upload_to="user_uploads",
                validators=[images.models.type_validator, images.models.size_validator],
            ),
        ),
        migrations.AlterField(
            model_name="image",
            name="uploaded_by",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="images",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
# Generated by Django 4.1.2 on 2023-02-16 22:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import images.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("images", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="image",
            name="image_field",
            field=models.ImageField(
                upload_to="user_uploads",
                validators=[images.models.type_validator, images.models.size_validator],
            ),
        ),
        migrations.AlterField(
            model_name="image",
            name="uploaded_by",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="images",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
