from django.db import models
from datetime import datetime

class Banners(models.Model):
    title = models.CharField(max_length=255,default='')
    title_ar = models.CharField(max_length=255,default='')
    image = models.FileField(upload_to="banners",default='')
    status = models.IntegerField(default=1)
    created_at = models.DateTimeField(default=datetime.now)
    updated_at = models.DateTimeField(auto_now=True) 
        

    class Meta:
        db_table = 'Banners' 