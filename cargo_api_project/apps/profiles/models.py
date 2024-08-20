#from django.contrib.auth.models import User
from django.conf import settings
from django.db import models
from datetime import datetime

class Profiles(models.Model):
    USER_TYPE_CHOICES = [
        ('1', 'Admin'),
        ('2', 'Agent'),
        ('3', 'User'),
    ]
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    created_at = models.DateTimeField(default=datetime.now)
    updated_at = models.DateTimeField(auto_now=True) 
        

    class Meta:
        db_table = 'profiles'

