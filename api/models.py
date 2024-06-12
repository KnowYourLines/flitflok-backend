import uuid

from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models


class User(AbstractUser):
    agreed_to_eula = models.BooleanField(default=False)
    blocked_users = models.ManyToManyField("self", blank=True)
    points = models.PositiveBigIntegerField(default=0)
    display_name = models.CharField(max_length=28, null=True, blank=True, unique=True)


class Video(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uploaded_at = models.DateTimeField(null=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    place_name = models.TextField(blank=True)
    address = models.TextField(blank=True)
    location = models.PointField(null=True)
    playback_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    asset_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    reported_by = models.ManyToManyField(User, related_name="reported_videos")
    hidden_from = models.ManyToManyField(User, related_name="hidden_videos")
    directions_requested_by = models.ManyToManyField(
        User, related_name="directions_requested_videos"
    )
