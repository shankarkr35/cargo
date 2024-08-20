from django.db import models
from django.contrib.auth.models import BaseUserManager,AbstractBaseUser
from django_google_maps import fields as map_fields
from datetime import datetime,timedelta
from django.utils import timezone


#  Custom User Manager
class UserManager(BaseUserManager):
    def create_user(self, email, fullname, phone, country_code,supplier_code=None, is_courier=False, is_admin=False, password=None, password2=None, is_active=True,profile_pic=None, courier_certificate=None, contract_file=None,courier_file1=None,courier_file2=None,courier_file3=None,owners_civil_id=None,fcm_token=None,session_token=None,token_version=None,otp=None,expire_otp=None,user_type=None,branch=None,address=None,latitude=None,longitude=None):
        """
        Creates and saves a User with the given email, fullname, phone, country_code, and password.
        """
        if not email:
            raise ValueError('User must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            fullname=fullname,
            phone=phone,
            country_code=country_code,
            is_courier=is_courier,
            is_admin = is_admin,
            is_active=is_active,
            profile_pic=profile_pic,
            courier_certificate=courier_certificate,
            fcm_token=fcm_token,
            session_token=session_token,
            token_version=token_version,
            otp=otp,
            expire_otp = expire_otp,
            user_type=user_type,
            branch=branch,
            address=address,
            latitude=latitude,
            longitude=longitude,
            supplier_code=supplier_code,
            contract_file = contract_file,
            courier_file1=courier_file1,
            courier_file2=courier_file2,
            courier_file3=courier_file3,
            owners_civil_id=owners_civil_id
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, fullname, phone, country_code, password,is_active=True,):
        """
        Creates and saves a superuser with the given email, fullname, phone, country_code, and password.
        """
        user = self.create_user(
            email=email,
            #is_active=True,  # Provide a default value for 'is_active'
            fullname=fullname,
            phone=phone,
            country_code=country_code,
            password=password,
            is_active = is_active,
            is_courier=False,
            
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    email = models.EmailField(verbose_name='Email', max_length=255, unique=True)
    fullname = models.CharField(max_length=200)
    phone = models.CharField(max_length=13, unique=True)
    country_code = models.CharField(max_length=4)
    fcm_token = models.CharField(max_length=255,null=True)
    session_token = models.CharField(max_length=255,null=True)
    token_version = models.IntegerField(blank=True,null=True)
    otp = models.CharField(max_length=20,null=True)
    expire_otp = models.DateTimeField(default=timezone.now() + timedelta(minutes=5))
    user_type = models.CharField(max_length=20,null=True)
    branch = models.CharField(max_length=100,null=True,blank=True)
    address = models.CharField(max_length=250,null=True)
    latitude = models.CharField(max_length=50,null=True)
    longitude = models.CharField(max_length=50,null=True)
    supplier_code = models.CharField(max_length=50,null=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_courier = models.BooleanField(default=False)
    courier_certificate = models.FileField(upload_to='courier_documents',default="")
    contract_file = models.FileField(upload_to='courier_documents',default="")
    courier_file1  = models.FileField(upload_to='courier_documents',default="")
    courier_file2  = models.FileField(upload_to='courier_documents',default="")
    courier_file3  = models.FileField(upload_to='courier_documents',default="")
    owners_civil_id  = models.FileField(upload_to='courier_documents',default="")
    profile_pic = models.FileField(upload_to='profile_pic',default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['fullname', 'phone', 'country_code']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_admin

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin
    
    def save(self, *args, **kwargs):
        if not self.expire_otp:
            self.expire_otp = timezone.now() + timedelta(minutes=5)
        super().save(*args, **kwargs)



#PICKUP LOCATION model

class PickupLocation(models.Model):#this is new autocomplete model for location 
    user = models.ForeignKey(User,on_delete=models.CASCADE,default="")
    address = models.CharField(max_length=255)
    #full_address= models.CharField(max_length=255) 
    area_street_block = models.CharField(max_length=100)
    house_building = models.CharField(max_length=100)
    floor = models.CharField(max_length=50, blank=True, null=True)
    apartment = models.CharField(max_length=100, blank=True, null=True)
    address_type = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.CharField(max_length=50)
    longitude = models.CharField(max_length=50)
    status = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return self.address

class DropLocation(models.Model):
    address = models.CharField(max_length=255)
    mobile = models.CharField(max_length=12,null=True)
    full_address= models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

        
    def __str__(self):
        return self.address
# packge size locations model
# class Package(models.Model):
#     package_id = models.AutoField(primary_key=True)
#     size = models.CharField(max_length=20)
#     weight_range=models.CharField(max_length=50,null=True,blank=True)

    
    # PACKAGE_SIZE_CHOICES = (
    #     ('small', 'Small (0-3)'),
    #     ('medium', 'Medium (3-6)'),
    #     ('large', 'Large (6-9)')
    # )

    # package_id = models.CharField(max_length=10, unique=True)
    # size = models.CharField(max_length=10, choices=PACKAGE_SIZE_CHOICES)
    # pick_up_time = models.DateTimeField()
    # current_address = models.ForeignKey(PickupLocation, related_name='packages_at_current_address', on_delete=models.CASCADE)
    # destination_address = models.ForeignKey(DropLocation, related_name='packages_at_destination_address', on_delete=models.CASCADE)




class Cargo_package(models.Model): 
    package_id = models.AutoField(primary_key=True)
    size = models.CharField(max_length=20,null=True,blank=True)
    size_ar = models.CharField(max_length=20,null=True,blank=True)
    order = models.IntegerField(blank=True,null=True)
    weight_range=models.CharField(max_length=50,null=True,blank=True)
    status = models.BooleanField(default=False)

    
class Time_Slot(models.Model): 
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.BooleanField(default=False)

    class Meta:
        db_table = 'time_slot'

    