from django.db import models
from datetime import datetime
from django.utils.text import slugify

# Create your models here.
class Color(models.Model):
    name = models.CharField(max_length=150,default="")
    slug = models.SlugField(max_length=100, unique=True,default="")
    name_ar = models.CharField(max_length=150,default="")
    color_code = models.CharField(max_length=150,default="")
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=datetime.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'color'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)