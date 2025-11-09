from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    bio = models.TextField(null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    x_link = models.CharField(max_length=255, null=True, blank=True) 
    linkedin_link = models.CharField(max_length=255, null=True, blank=True)
    github_link = models.CharField(max_length=255, null=True, blank=True)
    website_link = models.CharField(max_length=255, null=True, blank=True)

