from django.db import models
from datetime import datetime
from django.utils.text import slugify

class Support(models.Model):
    email = models.CharField(max_length=255,default='')
    phone = models.CharField(max_length=255,default='')
    address = models.TextField(max_length=255,default="")
    facebook_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    youtube_url = models.URLField(blank=True, null=True)
    whatsapp_url = models.URLField(blank=True, null=True)
    # whatsapp_url =  models.CharField(max_length=255,default='')
    # instagram_url =  models.CharField(max_length=255,default='')
    # facebook_url =  models.CharField(max_length=255,default='')
    # youtube_url =  models.CharField(max_length=255,default='')
    # twitter_url =  models.CharField(max_length=255,default='')
    status = models.IntegerField(default=1)
    created_at = models.DateTimeField(default=datetime.now)
    updated_at = models.DateTimeField(auto_now=True) 
        

    class Meta:
        db_table = 'support' 

    