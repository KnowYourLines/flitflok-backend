# Generated by Django 4.2.13 on 2024-06-04 02:32

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0010_user_points"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="display_name",
            field=models.CharField(blank=True, max_length=150, null=True, unique=True),
        ),
    ]
