from rest_framework import serializers
from .models import *

class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = ['name', 'date_of_birth', 'email', 'mobile_number', 'password', 'city', 'address']
   