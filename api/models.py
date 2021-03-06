from django.db import models
from django.db.models.deletion import CASCADE
from django.contrib.auth.models import User
import uuid


# Create your models here.
class AppUser(models.Model):
    AVATAR_CHOICES = (("male", "male"), ("female", "female"), ("human", "human"))
    user = models.OneToOneField(User, on_delete=CASCADE, null=True, blank=True)
    auth_token = models.CharField(max_length=256, blank=True, default="", null=True)
    username = models.CharField(max_length=256)
    email = models.EmailField(max_length=256, unique=True)
    password = models.CharField(max_length=64, blank=True, null=True)
    stats_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    are_stats_generated = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    avatar = models.CharField(
        choices=AVATAR_CHOICES, default="human", blank=True, null=True, max_length=10
    )

    def __str__(self) -> str:
        return self.username
