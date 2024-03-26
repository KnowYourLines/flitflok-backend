# Generated by Django 4.2.10 on 2024-03-26 21:53

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0006_video_hidden_from_video_reported_by"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="blocked_users",
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
