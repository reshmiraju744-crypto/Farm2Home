from django.contrib.auth.models import AbstractUser
from django.db import models

# User Roles
USER_ROLES = (
    ('admin', 'Admin'),
    ('farmer', 'Farmer'),
    ('customer', 'Customer'),
)

class User(AbstractUser):
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    role = models.CharField(max_length=10, choices=USER_ROLES)

    def __str__(self):
        return f"{self.username} ({self.role})"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return self.user.username