# Generated by Django 4.2.13 on 2024-06-12 05:22

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0013_rename_created_at_video_uploaded_at_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="video",
            name="uploaded_at",
            field=models.DateTimeField(null=True),
        ),
    ]
