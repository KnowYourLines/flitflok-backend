import uuid

from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models


class User(AbstractUser):
    agreed_to_eula = models.BooleanField(default=False)
    blocked_users = models.ManyToManyField("self", blank=True)
    points = models.PositiveBigIntegerField(default=0)
    display_name = models.CharField(max_length=28, null=True, blank=True, unique=True)


class Video(models.Model):
    FOOD_AND_DRINK = "Food & Drink"
    RECREATION_AND_ENTERTAINMENT = "Recreation & Entertainment"
    LANDMARKS_AND_ATTRACTIONS = "Landmarks & Attractions"
    SHOPPING = "Shopping"
    FACILITIES_AND_SERVICES = "Facilities & Services"
    LOCATION_PURPOSE_CHOICES = [
        (FOOD_AND_DRINK, FOOD_AND_DRINK),
        (RECREATION_AND_ENTERTAINMENT, RECREATION_AND_ENTERTAINMENT),
        (LANDMARKS_AND_ATTRACTIONS, LANDMARKS_AND_ATTRACTIONS),
        (SHOPPING, SHOPPING),
        (FACILITIES_AND_SERVICES, FACILITIES_AND_SERVICES),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uploaded_at = models.DateTimeField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.PointField()
    thumbnail = models.URLField()
    hls = models.URLField()
    preview = models.URLField()
    cloudflare_uid = models.CharField(max_length=255, default=uuid.uuid4, unique=True)
    reported_by = models.ManyToManyField(User, related_name="reported_videos")
    hidden_from = models.ManyToManyField(User, related_name="hidden_videos")
    directions_requested_by = models.ManyToManyField(
        User, related_name="directions_requested_videos"
    )
    location_purpose = models.CharField(
        max_length=255, choices=LOCATION_PURPOSE_CHOICES, blank=True
    )
