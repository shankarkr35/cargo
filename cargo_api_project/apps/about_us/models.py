from django.db import models
from datetime import datetime

class About_us(models.Model):
    title = models.CharField(max_length=255,default='')
    title_ar = models.CharField(max_length=255,default='')
    title1 = models.CharField(max_length=255,default='')
    title1_ar = models.CharField(max_length=255,default='')
    description = models.TextField(default="")
    description_ar = models.TextField(default="")

    experience_desc = models.CharField(max_length=255,default='')
    experience_desc_ar = models.CharField(max_length=255,default='')
    experience_year = models.CharField(max_length=255,default='')
    experience_title = models.CharField(max_length=255,default='')
    experience_title_ar = models.CharField(max_length=255,default='')

    image = models.FileField(upload_to="about_us",default='')
    status = models.IntegerField(default=1)
    created_at = models.DateTimeField(default=datetime.now)
    updated_at = models.DateTimeField(auto_now=True) 
        

    class Meta:
        db_table = 'About_us' 