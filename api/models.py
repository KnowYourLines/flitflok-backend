from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    agreed_to_eula = models.BooleanField(default=False)
