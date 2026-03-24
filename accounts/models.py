from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db import models

def __str__(self):
    return f"{self.user.username} Profile"


