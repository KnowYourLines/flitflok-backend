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
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    place_name = models.TextField(blank=True)
    address = models.TextField(blank=True)
    location = models.PointField()
    file_id = models.UUIDField(unique=True)
    reported_by = models.ManyToManyField(User, related_name="reported_videos")
    hidden_from = models.ManyToManyField(User, related_name="hidden_videos")
    directions_requested_by = models.ManyToManyField(
        User, related_name="directions_requested_videos"
    )
