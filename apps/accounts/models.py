from django.db import models
from django.contrib.auth.models import AbstractUser

from apps.accounts.managers import UserManager

class User(AbstractUser):
    """
    Default custom user model for Smart Notify.
    """

    username = None
    mobile = models.CharField(
        max_length=16, unique=True, blank=True, null=True
    )
    email = models.EmailField(unique=True)
    first_login = models.BooleanField(default=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()
    

    class Meta:
        db_table = "user"
    
class KnownDevice(models.Model):
    """
    To store known devices information to send information if logged in from unknown devices.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='known_devices')
    device_fingerprint = models.CharField(max_length=512)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    last_used = models.DateTimeField(auto_now=True)