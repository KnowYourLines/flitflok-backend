import uuid

from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models


class User(AbstractUser):
    agreed_to_eula = models.BooleanField(default=False)


class Video(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    place_name = models.TextField(blank=True)
    address = models.TextField(blank=True)
    location = models.PointField()
    file_id = models.UUIDField()
