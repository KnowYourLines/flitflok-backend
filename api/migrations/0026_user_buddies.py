# Generated by Django 4.2.13 on 2024-08-23 15:26

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0025_video_currency_video_money_spent_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="buddies",
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
