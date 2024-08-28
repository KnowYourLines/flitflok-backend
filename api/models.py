import decimal
import uuid

from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models
from moneyed import list_all_currencies

CURRENCY_CHOICES = [
    (str(currency), str(currency)) for currency in list_all_currencies()
]


class User(AbstractUser):
    agreed_to_eula = models.BooleanField(default=False)
    blocked_users = models.ManyToManyField("self", blank=True)
    points = models.PositiveBigIntegerField(default=0)
    display_name = models.CharField(max_length=28, null=True, blank=True, unique=True)
    buddies = models.ManyToManyField("self", blank=True)


class BuddyRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_buddy_requests"
    )
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="received_buddy_requests"
    )


class Video(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uploaded_at = models.DateTimeField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    starring = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="videos_starring"
    )
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
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default="GBP")
    money_spent = models.DecimalField(
        max_digits=14, decimal_places=2, default=decimal.Decimal("0.00")
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="currency_valid",
                check=models.Q(
                    currency__in=[str(currency) for currency in list_all_currencies()]
                ),
            )
        ]
