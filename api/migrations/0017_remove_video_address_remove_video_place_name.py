# Generated by Django 4.2.13 on 2024-06-28 22:58

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0016_video_location_purpose"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="video",
            name="address",
        ),
        migrations.RemoveField(
            model_name="video",
            name="place_name",
        ),
    ]
