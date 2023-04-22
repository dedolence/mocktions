# Generated by Django 4.1.2 on 2023-04-22 19:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("images", "0009_imageset_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="imageset",
            name="min_size",
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name="imageset",
            name="max_size",
            field=models.IntegerField(default=2),
        ),
    ]
