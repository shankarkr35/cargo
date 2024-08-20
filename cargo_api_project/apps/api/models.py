from django.db import models
from datetime import datetime
from django.contrib.auth import get_user_model
User = get_user_model()
from cargo_user_app.models import Cargo_package,PickupLocation
from cargo_driver_app.models import Driver,Vehicle,VehicleType


# Create your models here.
class Orders(models.Model): 
    user = models.ForeignKey(User,on_delete=models.CASCADE,default="")
    package = models.ForeignKey(Cargo_package,on_delete=models.CASCADE,null=True,default="")
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, null=True)
    pickup = models.ForeignKey(PickupLocation,on_delete=models.CASCADE,null=True,default="")
    
    company_id = models.CharField(max_length=15,default="")

    order_id = models.CharField(max_length=250,default="")
    delivery_price = models.DecimalField(max_digits = 10,decimal_places = 2, default=0.00)
    due_amount = models.DecimalField(max_digits = 10,decimal_places = 2, default=0.00)
    pickup_time = models.CharField(max_length=120,default="")
    pickup_otp_verification = models.IntegerField(null=True)
    #pickup_date = models.DateField(blank=True)
 
    pickup_address = models.CharField(max_length=250,blank=True)
    
    pickup_latitude = models.CharField(max_length=50,blank=True)
    pickup_longitude = models.CharField(max_length=50,blank=True)

    destination_address = models.CharField(max_length=250)
    country_code = models.CharField(max_length=20,blank=True)
    destination_mobile = models.CharField(max_length=12,blank=True)
    destination_area_street_block = models.CharField(max_length=100, null=True)
    destination_house_building = models.CharField(max_length=100, null=True)
    destination_floor = models.CharField(max_length=50, blank=True, null=True)
    destination_apartment = models.CharField(max_length=100, blank=True, null=True)

    destination_latitude = models.CharField(max_length=50)
    destination_longitude = models.CharField(max_length=50)
    order_by = models.IntegerField(default=1) 
    vehicle_type = models.ForeignKey(VehicleType,on_delete=models.CASCADE,null=True,default="") 
    paymentId = models.CharField(max_length=250, blank=True, default="")
    paymentStatus = models.CharField(max_length=150, blank=True, default="")
    paymentMethod = models.CharField(max_length=50, blank=True, default="")
    status = models.IntegerField(default=1)
    device_token = models.CharField(max_length=220,null=True)
    distance = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    #fcm_token = models.CharField(max_length=120,null=True)
    #device_name = models.CharField(max_length=120,null=True)
    created_at = models.DateTimeField(default=datetime.now)
    updated_at = models.DateTimeField(auto_now=True) 
    
    class Meta:
        db_table = 'orders'

class DriverOrders(models.Model): 
    user = models.ForeignKey(User,on_delete=models.CASCADE,default="")
    package = models.ForeignKey(Cargo_package,on_delete=models.CASCADE,null=True,default="")
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, null=True)
    pickup = models.ForeignKey(PickupLocation,on_delete=models.CASCADE,null=True,default="")
    order_unique_id = models.CharField(max_length=250,default="")
    company_id = models.CharField(max_length=15,default="")

    order_id = models.CharField(max_length=250,default="")
    delivery_price = models.DecimalField(max_digits = 10,decimal_places = 2, default=0.00)
    due_amount = models.DecimalField(max_digits = 10,decimal_places = 2, default=0.00)
    pickup_time = models.CharField(max_length=120,default="")
    pickup_otp_verification = models.IntegerField(null=True)
    #pickup_date = models.DateField(blank=True)
    pickup_address = models.CharField(max_length=250,blank=True)
    pickup_latitude = models.CharField(max_length=50,blank=True)
    pickup_longitude = models.CharField(max_length=50,blank=True)
    destination_address = models.CharField(max_length=250)
    country_code = models.CharField(max_length=20,blank=True)
    destination_mobile = models.CharField(max_length=12,blank=True)
    destination_area_street_block = models.CharField(max_length=100, null=True)
    destination_house_building = models.CharField(max_length=100, null=True)
    destination_floor = models.CharField(max_length=50, blank=True, null=True)
    destination_apartment = models.CharField(max_length=100, blank=True, null=True)

    destination_latitude = models.CharField(max_length=50)
    destination_longitude = models.CharField(max_length=50)
    #vehicle_type = models.CharField(max_length=120) 
    order_by = models.IntegerField(default=1) 
    device_token = models.CharField(max_length=220,null=True)
    #fcm_token = models.CharField(max_length=120,null=True)
    #device_name = models.CharField(max_length=120,null=True)
    vehicle_type = models.ForeignKey(VehicleType,on_delete=models.CASCADE,null=True,default="") 
    paymentId = models.CharField(max_length=250, blank=True, default="")
    paymentStatus = models.CharField(max_length=150, blank=True, default="")
    paymentMethod = models.CharField(max_length=50, blank=True, default="")
    distance = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    status = models.IntegerField(default=1)
    created_at = models.DateTimeField(default=datetime.now)
    updated_at = models.DateTimeField(auto_now=True) 

    class Meta:
        db_table = 'driver_orders'

class TrackOrder(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,default="")
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, null=True)
    order_unique_id = models.CharField(max_length=250,default="")
    status = models.IntegerField(default=1)
    created_at = models.DateTimeField(default=datetime.now)
    updated_at = models.DateTimeField(auto_now=True) 

    class Meta:
        db_table = 'track_order'

        