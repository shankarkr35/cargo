from django.db import models
from datetime import datetime
from django.utils.text import slugify

class Pages(models.Model):
    name = models.CharField(max_length=255,default='')
    name_ar = models.CharField(max_length=255,default='')
    slug = models.SlugField(max_length=100, unique=True,default="")
    description = models.TextField(default="")
    description_ar = models.TextField(default="")
    status = models.IntegerField(default=1)
    created_at = models.DateTimeField(default=datetime.now)
    updated_at = models.DateTimeField(auto_now=True) 
        

    class Meta:
        db_table = 'pages' 

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)