from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()
from datetime import datetime
from django.utils.text import slugify
from apps.color.models import *

# Create your models here.


class Driver(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,default="")
    name = models.CharField(max_length=255) 
    name_ar = models.CharField(max_length=255,default="")
    supplier_code = models.CharField(max_length=50,default="")
    #date_of_birth = models.DateField(null=True) 
    email = models.EmailField(default="")
    country_code = models.CharField(max_length=4,default="+965")
    mobile_number = models.CharField(max_length=20,unique=True)
    password = models.CharField(max_length=255,default="") 
    civil_id = models.CharField(max_length=255,default="")
    city = models.CharField(max_length=255,default="")
    city_ar = models.CharField(max_length=255,default="")
    address = models.CharField(max_length=255,default="")
    address_ar = models.CharField(max_length=255,default="")
    latitude = models.CharField(max_length=255,default="")
    longitude = models.CharField(max_length=255,default="")
    driving_licence = models.FileField(upload_to='documents/',default="")
    status = models.BooleanField(default=False)
    otp = models.CharField(max_length=15,default="")
    islogged = models.BooleanField(default=False)
    fcm_token = models.CharField(max_length=255,null=True)
    session_token = models.CharField(max_length=255,null=True)
    token_version = models.IntegerField(blank=True,null=True)

    def __str__(self):
        return self.name


class VehicleType(models.Model):
    title = models.CharField(max_length=255,default="")
    title_ar = models.CharField(max_length=255,default="")
    slug = models.SlugField(max_length=100, unique=True,default="")
    image = models.FileField(upload_to='vehicle',default="")
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=datetime.now)
    updated_at = models.DateTimeField(auto_now=True) 

    class Meta:
        db_table = 'vehicleType'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Vehicle(models.Model):
    # VEHICLE_TYPE_CHOICES = [
    #     ('car', 'Car'),
    #     ('truck', 'Truck'),
    #     ('van', 'Van'),
    #     ('bike', 'Bike'),
    # ]
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE,default="")
    color = models.ForeignKey(Color, on_delete=models.CASCADE,default="")
    #vehicle_type = models.CharField(max_length=10, choices=VEHICLE_TYPE_CHOICES)
    #vehicle_type = models.CharField(max_length=150,default="")
    vehicle_type = models.ForeignKey(VehicleType,on_delete=models.CASCADE,null=True)
    #color = models.CharField(max_length=120,default='')
    vehicle_number = models.CharField(max_length=255,default='')
    image = models.FileField(upload_to='vehicle/',default="")
    user = models.ForeignKey(User, on_delete=models.CASCADE,default="")
    status = models.BooleanField(default=False)