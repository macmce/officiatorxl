from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """Custom user model that extends Django's built-in User model."""
    bio = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='profile_pics', blank=True, null=True)
    
    def __str__(self):
        return self.username
