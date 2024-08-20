from rest_framework import serializers
from cargo_user_app.models import *
from cargo_driver_app.models import *
from apps.api.models import Orders,DriverOrders,TrackOrder
from apps.delivery_charge.models import DeliveryCharge
from apps.company_delivery_charge.models import CompanyDeliveryCharge
from apps.pages.models import Pages
from apps.support.models import Support
from apps.wallet.models import Wallet,Transaction
import uuid
import time
import random

class PackagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cargo_package
        fields = '__all__' 

class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Time_Slot
        fields = '__all__'
class CompanyDeliveryChargeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyDeliveryCharge
        fields = ['id','start_distance','end_distance','delivery_charge']  # Or specify the fields you want to include

class UserSerializer(serializers.ModelSerializer):
    company_delivery_charge = CompanyDeliveryChargeSerializer(many=True, read_only=True, source='company_delivery_charges')

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname', 'phone', 'country_code', 'is_active', 'is_admin', 'profile_pic', 'is_courier', 'created_at', 'company_delivery_charge']
        
class UserAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class AuthLoginSerializer(serializers.ModelSerializer):
  email = serializers.EmailField(max_length=255)
  class Meta:
    model = User
    fields = ['email', 'password']

class DriverLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = ['mobile_number', 'password']

class VehiclesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = '__all__'

class VehicleTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleType
        fields = '__all__'

class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cargo_package
        fields = '__all__'

class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = '__all__'

class PickupSerializer(serializers.ModelSerializer):
    class Meta:
        model = PickupLocation
        fields = '__all__'
        #fields = ['user', 'address','area_street_block','house_building','floor','apartment','latitude','longitude']

class OrderSerializer(serializers.ModelSerializer):
    #ORDER-{str(uuid.uuid4())[:8]}-{int(time.time())} 
    order_id = serializers.SerializerMethodField(read_only=True)
    #pickup_otp_verification = random.random()
    #pickup_date = serializers.DateField(format="%Y-%m-%d")
    def get_pickup_otp_verification(self, obj):
        return random.randint(1000, 9999)  # Generate a 4-digit OTP
    def get_order_id(self, obj):
        return f"ORDER-{str(uuid.uuid4())[:8]}-{int(time.time())}"
    class Meta:
        model = Orders
        #fields = '__all__'
        fields = ['id','order_id', 'user', 'package', 'driver','pickup', 'pickup_time','pickup_otp_verification', 'pickup_address', 'pickup_latitude', 'pickup_longitude', 'destination_address','country_code','destination_mobile', 'destination_area_street_block','destination_house_building','destination_floor','destination_apartment', 'destination_latitude', 'destination_longitude', 'vehicle_type','delivery_price', 'status','device_token','paymentId','paymentStatus','paymentMethod', 'created_at', 'updated_at']

    def create(self, validated_data):
        order_id = self.get_order_id(None)
        validated_data['order_id'] = order_id
        pickup_otp_verification = self.get_pickup_otp_verification(None)
        validated_data['pickup_otp_verification'] = pickup_otp_verification
        return super().create(validated_data)
    
class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Orders
        fields = ['driver','status','distance']

class UpdateUserOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Orders
        fields = ['user','status']

class OrderListSerializer(serializers.ModelSerializer):
    driver = DriverSerializer()  
    package = PackageSerializer()  
    vehicle_type = VehicleTypeSerializer() 
    pickup = PickupSerializer() 
    user = UserSerializer() 

    class Meta:
        model = Orders
        fields = ['id','order_id', 'user', 'package', 'driver','pickup', 'pickup_time','pickup_otp_verification', 'pickup_address', 'pickup_latitude', 'pickup_longitude', 'destination_address','country_code','destination_mobile','destination_area_street_block','destination_house_building','destination_floor','destination_apartment', 'destination_latitude', 'destination_longitude', 'vehicle_type','delivery_price','distance','order_by','device_token','paymentId','paymentStatus','paymentMethod','distance', 'status', 'created_at', 'updated_at']

        
class VehiTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleType
        fields = '__all__'

class DriverVehicleSerializer(serializers.ModelSerializer):
    #driver = DriverSerializer()  
    vehicle_type = VehicleTypeSerializer() 
    class Meta:
        model = Vehicle
        fields = '__all__'
class DriverAcceptedOredersSerializer(serializers.ModelSerializer):
    driver = DriverSerializer()  
    package = PackageSerializer()  
    vehicle_type = VehicleTypeSerializer() 
    pickup = PickupSerializer() 
    user = UserSerializer()

    class Meta:
        model = DriverOrders
        fields = ['id','order_id', 'order_unique_id', 'user', 'package', 'driver','pickup', 'pickup_time','pickup_otp_verification', 'pickup_address', 'pickup_latitude', 'pickup_longitude', 'destination_address','country_code','destination_mobile','destination_area_street_block','destination_house_building','destination_floor','destination_apartment', 'destination_latitude', 'destination_longitude', 'vehicle_type','delivery_price','distance','order_by', 'status','device_token','paymentId','paymentStatus','paymentMethod', 'created_at', 'updated_at']


class DeliveryChargeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryCharge
        fields = '__all__'

class UpdateDriverLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = ['id','latitude','longitude']

class PagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pages
        fields = '__all__'

class UpdateOrderPaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Orders
        fields = ['paymentId','paymentStatus','paymentMethod']

class SupportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Support
        fields = '__all__'

# class DepositSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Wallet
#         fields = '__all__'
        
class DepositSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

class WithdrawSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'wallet', 'amount', 'transaction_type', 'paymentId','note','balance', 'paymentStatus', 'timestamp']

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'fullname', 'phone']

class DriverByCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = fields = ['id', 'name', 'mobile_number']

class OrderSerializerB2B(serializers.ModelSerializer):
    #ORDER-{str(uuid.uuid4())[:8]}-{int(time.time())} 
    order_id = serializers.SerializerMethodField(read_only=True)
    #pickup_otp_verification = random.random()
    #pickup_date = serializers.DateField(format="%Y-%m-%d")
    def get_pickup_otp_verification(self, obj):
        return random.randint(1000, 9999)  # Generate a 4-digit OTP
    def get_order_id(self, obj):
        return f"ORDER-{str(uuid.uuid4())[:8]}-{int(time.time())}"
    class Meta:
        model = Orders
        #fields = '__all__'
        fields = ['id','order_id', 'user', 'package', 'driver','company_id','pickup', 'pickup_time','pickup_otp_verification', 'pickup_address', 'pickup_latitude', 'pickup_longitude', 'destination_address','country_code','destination_mobile', 'destination_area_street_block','destination_house_building','destination_floor','destination_apartment', 'destination_latitude', 'destination_longitude', 'vehicle_type','distance','delivery_price', 'status','device_token','paymentId','paymentStatus','paymentMethod','order_by','created_at', 'updated_at']

    def create(self, validated_data):
        order_id = self.get_order_id(None)
        validated_data['order_id'] = order_id
        pickup_otp_verification = self.get_pickup_otp_verification(None)
        validated_data['pickup_otp_verification'] = pickup_otp_verification
        return super().create(validated_data)
    

class TrackOrderSerializer(serializers.ModelSerializer):
    status_name = serializers.SerializerMethodField()
    class Meta:
        model = TrackOrder
        fields = ['id','order_unique_id','status','status_name','created_at','driver_id','user_id']
        
    def get_status_name(self, obj):
        status_map = {
            1: "Pending",
            2: "Accepted by driver",
            4: "Pickup by driver",
            5: "Delivered by driver",
            5: "Cancelled By user",
            # Add more mappings as needed
        }
        return status_map.get(obj.status, "Unknown")

class DeliveryChargeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyDeliveryCharge
        fields = '__all__'


class OrderListB2BSerializer(serializers.ModelSerializer):
    driver = DriverSerializer()  
    user = UserSerializer() 
    status_name = serializers.SerializerMethodField()
    class Meta:
        model = Orders
        #fields = '__all__'
        fields = [ 'user', 'id','order_id','driver','pickup_time','pickup_otp_verification', 'pickup_address', 'pickup_latitude', 'pickup_longitude', 'destination_address','country_code','destination_mobile','destination_area_street_block','destination_house_building','destination_floor','destination_apartment', 'destination_latitude', 'destination_longitude', 'vehicle_type','delivery_price','due_amount','device_token','paymentId','paymentStatus','paymentMethod','distance', 'status','status_name', 'created_at', 'updated_at']

    
    def get_status_name(self, obj):
        status_map = {
            1: "Pending",
            2: "Accepted by driver",
            4: "Pickup by driver",
            5: "Delivered by driver",
            5: "Cancelled By user",
            # Add more mappings as needed
        }
        return status_map.get(obj.status, "Unknown")
    
class PaymentSerializer(serializers.Serializer):
    customer_name = serializers.CharField(max_length=255)
    notification_option = serializers.ChoiceField(choices=["LNK", "SMS", "EML", "ALL"], required=False)
    invoice_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    mobile_country_code = serializers.CharField(max_length=10, required=False)
    customer_mobile = serializers.CharField(max_length=20, required=False)
    customer_email = serializers.EmailField(required=False)
    display_currency_iso = serializers.CharField(max_length=3, required=False)
    callback_url = serializers.URLField(required=False)
    error_url = serializers.URLField(required=False)
    language = serializers.ChoiceField(choices=["en", "ar"], required=False)
    customer_reference = serializers.CharField(max_length=255, required=False)
    customer_address = serializers.JSONField(required=False)
    invoice_items = serializers.JSONField(required=False)

class BusinessB2BSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    
class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['id', 'balance']

class MainBusinessB2BSerializer(serializers.ModelSerializer):
    wallet = WalletSerializer()

    class Meta:
        model = User
        fields = [ 'id', 'fullname', 'email', 'phone', 'address', 'latitude', 'longitude', 'user_type', 'branch','wallet']


