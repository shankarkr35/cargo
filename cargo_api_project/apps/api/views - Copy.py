from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from cargo_user_app.models import *
from .serializers import *
from rest_framework import status
from django.contrib.auth import get_user_model
User = get_user_model() 
from apps.wallet.models import *; 
import jwt 
from datetime import timedelta
from rest_framework.exceptions import AuthenticationFailed
from jwt import decode, ExpiredSignatureError
#from middlewares.verifyToken import verify
from middlewares.verifyToken import user_token_required
from middlewares.driverVerifyToken import driver_token_required
from middlewares.pushNotification import send_fcm_notification

from datetime import datetime,timedelta,timezone
from cargo_driver_app.models import *
#from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from math import radians, sin, cos, sqrt, atan2
from django.db.models import F
from cargo_user_app.models import PickupLocation
import json
import os 
from django.db.models import Q
from .models import DriverOrders,TrackOrder
from apps.delivery_charge.models import DeliveryCharge
from decimal import Decimal
import random
from django.utils.timezone import make_aware
from firebase_admin import messaging
from django.core.files.storage import FileSystemStorage
#from cargo_driver_app.models import Driver
from cargo_driver_app.models import Driver
from apps.pages.models import Pages
from apps.company_delivery_charge.models import CompanyDeliveryCharge
from django.core.mail import send_mail,EmailMultiAlternatives
from django.contrib.auth.hashers import make_password
import math

class HomeAPIView(APIView):
    def get(self, request):
        try:
            lang = request.META.get('HTTP_LANG', None) 
            packages = Cargo_package.objects.filter(status=1).order_by('order')
            if packages.exists():
                packages_array = []

                for pack in packages:
                    size = pack.size if lang == 'en' else pack.size_ar
                    #return Response({"msg":"Success","data":size})
                    my_object = {"package_id": pack.package_id, "size":size, "weight_range":pack.weight_range, "order":pack.order }
                    packages_array.append(my_object)
                
                serializer = PackagesSerializer(packages_array, many=True)

            time_slot = Time_Slot.objects.all()
            time_list = []
            for time in time_slot:
                
                my_obj = {'id':time.id,'start_time':time.start_time.strftime("%I:%M %p"),'end_time':time.end_time.strftime("%I:%M %p"),'status':time.status}
                time_list.append(my_obj)
            time_serializer = TimeSlotSerializer(time_list, many=True)

            response_data = {
                'msg':"Successfully",
                'success': True,
                'package': serializer.data,
                'time_slot': time_serializer.data,
                'status':status.HTTP_200_OK
            }
            return Response(response_data, status=status.HTTP_200_OK)
           
        except Exception as e:
            response_data = {
                'success': False,
                'msg': f'Something Went Wrong: {str(e)}',
                'status':status.HTTP_500_INTERNAL_SERVER_ERROR
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class UserAuthView(APIView):
    def post(self, request):
        try:
            email = request.data.get('email')
            phone = request.data.get('phone')
            password = request.data.get('password')
            password2 = request.data.get('password2')
            
            if User.objects.filter(email = email).exists():
                response_data = {
                    'msg':"email already exist",
                    'success': False,
                    'status':status.HTTP_400_BAD_REQUEST
                }
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            if User.objects.filter(phone = phone).exists():
                response_data = {
                    'msg':"phone already exist",
                    'success': False,
                    'status':status.HTTP_400_BAD_REQUEST
                }
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            if password !=password2:
                response_data = {
                    'msg':"Confirm password not matched!",
                    'success': False,
                    'status':status.HTTP_400_BAD_REQUEST
                }
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            
            serializerdata = UserAuthSerializer(data=request.data) 
            if serializerdata.is_valid(): 
                user = serializerdata.save()
                if user:
                    wallet = Wallet.objects.create(user=user,balance=0)
                    expiry = datetime.utcnow() + timedelta(minutes=60)
                    current_time = datetime.now(timezone.utc)
                    issued_time = int(current_time.timestamp())
                    payload = {
                        'user_id': user.id,
                        'expiry': expiry.strftime('%Y-%m-%d %H:%M:%S'),
                        'iat': issued_time,
                        
                    }
                    # Encode the payload as a JWT
                    jwt_token = jwt.encode(payload, os.getenv('SECRET_KEY'), algorithm='HS256')
                    response = Response()
                    response.set_cookie(key='user_token',value=jwt_token,httponly=True)
                    response.data = {
                        'success': True,
                        # 'error': False,
                        'msg': 'User created successfully',
                        'status': status.HTTP_200_OK,
                        'token': jwt_token,
                        'responseData': {
                            'id': user.id,
                            'email': user.email,
                            'phone': user.phone,
                            'name': user.fullname,
                            'country_code': user.country_code,
                            'wallet_balance': float(wallet.balance)  # Pass wallet balance in response
                        
                        },
                    }
                    return response
            else:
                return Response({"error":serializerdata.errors})
            
        except Exception as e:
            response_data = {
                'success': False,
                'msg': f'Something Went Wrong: {str(e)}',
                'status':status.HTTP_500_INTERNAL_SERVER_ERROR
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserView(APIView):
    @user_token_required
    def post(self, request):
        try:
            user_id = int(request.data.get('user_id'))
            singledata = User.objects.get(id=user_id)
            serialdata = UserSerializer(singledata, many =False)
            current_site = get_current_site(request)
            current_url = f"{request.scheme}://{current_site.domain}"
            return Response({'msg':"Data Found",'status':True,current_url:current_url,'data':serialdata.data})
            
        except Exception as e:
            response_data = {
                'success': False,
                'msg': f'{str(e)}',
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
               
# class UserView(APIView):
#     def get(self, request):
#         try:
#             token = request.COOKIES.get('jwt')
#             if not token:
#                raise AuthenticationFailed('Unauthenticated !')
#             try:
#                #payload = jwt.decode(token, 'your_secret_key', algorithms=['HS256'], options={"verify_iat": False})
#                #-- verify token
#                 payload = verify(token)

#                 singledata = User.objects.get(id=payload['user_id'])
#                 serialdata = UserAuthSerializer(singledata, many =False)
#                 return Response({'msg':"Data Found",'status':True,'jwt_token':token,'data':serialdata.data})
#             except jwt.ExpiredSignatureError:
#                raise AuthenticationFailed("Unauthenticated !")
            
#         except Exception as e:
#             response_data = {
#                 'success': False,
#                 'msg': f'{str(e)}',
#             }
#             return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class DriverLoginView(APIView):
    def post(self,request):
        try:
            phone = request.data.get('mobile_number')
            fcm_token = request.data.get('fcm_token')
            driver = Driver.objects.filter(mobile_number=phone).first()
            if driver is not None:
                #updatedDriver = Driver.objects.filter(id=driver.id).update(fcm_token=fcm_token)
                expiry = datetime.utcnow() + timedelta(minutes=60)
                current_time = datetime.now(timezone.utc)
                issued_time = int(current_time.timestamp())
                payload = {
                    'driver_id': driver.id,
                    'expiry': expiry.strftime('%Y-%m-%d %H:%M:%S'),
                    'iat': issued_time,
                    'token_version': driver.token_version,  # Include token_version in the payload
                }

                # Encode the payload as a JWT
                jwt_token = jwt.encode(payload, os.getenv('SECRET_KEY'), algorithm='HS256')

                if driver.status == True:
                    otp = random.randint(1000, 9999)
                    Driver.objects.filter(id=driver.id).update(otp=otp,fcm_token=fcm_token)
                    courier_id = driver.user_id
                    
                    driverInfo = User.objects.filter(id=courier_id).first()
                    #print("User IDS",driverInfo.supplier_code) 
                    notifications = {
                        "message": {
                            "topic": "Driver OTP",
                            "notification": {
                                "title": "Driver OTP",
                                "body": f"Your OTP is {otp}."
                            },
                            "data": {
                                "driver_id": "driver.id"
                            }
                        }
                    }
                    response = self.send_fcm_notification(fcm_token, notifications)
                    response = Response()
                    response.data = {
                        'success': True,
                        'msg': 'OTP has been sent!',
                        'status': status.HTTP_200_OK,
                        'responseData': {
                            'driver_id': driver.id,
                            'name': driver.name,
                            'mobile_number': driver.mobile_number,
                            'email': driver.email,
                            'city': driver.city,
                            'otp':driver.otp,
                            'supplier_code': driverInfo.supplier_code,
                            
                        }
                    }
                    return response
                else:
                    response_data = {
                        'success': False,
                        'msg': 'Login Failed',
                        'errors': "Account is not active please contact to admin!",
                        'status': status.HTTP_404_NOT_FOUND,
                    }
                    return Response(response_data, status=status.HTTP_404_NOT_FOUND) 
            else:
                response_data = {
                    'success': False,
                    'msg': 'Login Failed',
                    'errors': "Incorrect Mobile Number!",
                    'status': status.HTTP_404_NOT_FOUND,
                }
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            response_data = {
                'success': False,
                'msg': f'Login Failed: {str(e)}',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def send_fcm_notification(self, device_token, notifications):
        # Convert all values to strings in the 'data' dictionary
        for key, value in notifications["message"]["data"].items():
            notifications["message"]["data"][key] = str(value)

        message = messaging.Message(
            data=notifications["message"]["data"],  # Use the 'data' parameter with 'data' dictionary
            notification=messaging.Notification(
                title=notifications["message"]["notification"]["title"],
                body=notifications["message"]["notification"]["body"],
                #data=notifications["message"]["data"]["order_id"],
            ),
            token=device_token,
        )
        response = messaging.send(message)
        return response
        
class VerifyDriverOtpView(APIView):
    def post(self,request):
        try:
            phone = request.data.get('mobile_number')
            otp = request.data.get('otp')
            
            driver = Driver.objects.filter(mobile_number=phone).first()
            #return Response({'driver_id':driver.id,'password':password})
            if driver is not None: 
                if driver.otp == otp:
                    Driver.objects.filter(id=driver.id).update(otp='',islogged=True)
                    vehicles = Vehicle.objects.select_related('vehicle_type').filter(Q(driver=driver.id) & Q(status=1))
                    # ------------
                    if driver.token_version is None:
                        driver.token_version = 0
                    # Update the token_version
                    driver.token_version += 1
                    driver.save()
                    # token = get_tokens_for_user(user)
                    expiry = datetime.utcnow() + timedelta(minutes=60)
                    current_time = datetime.now(timezone.utc)
                    issued_time = int(current_time.timestamp())
                    payload = {
                        'driver_id': driver.id,
                        'expiry': expiry.strftime('%Y-%m-%d %H:%M:%S'),
                        'iat': issued_time,
                        'token_version': driver.token_version,  # Include token_version in the payload
                    }

                    # Encode the payload as a JWT
                    jwt_token = jwt.encode(payload, os.getenv('SECRET_KEY'), algorithm='HS256')
                    
                    updatedDriver = Driver.objects.filter(id=driver.id).update(session_token=jwt_token)
                    
                    # -------------
                    response = Response()
                    response.set_cookie(key='driver_token',value=jwt_token,httponly=True)

                    driver_vehicle = None
                    if vehicles.exists():
                        serializer = DriverVehicleSerializer(vehicles, many=True)
                        driver_vehicle = serializer.data
                    else:
                        driver_vehicle = driver_vehicle
                    
                    current_site = get_current_site(request)
                    current_url = f"{request.scheme}://{current_site.domain}"
                    response.data = {
                        'success': True,
                        # 'error': False,
                        'msg': 'Driver Login Success',
                        'status': status.HTTP_200_OK,
                        'token': jwt_token,
                        'current_url':current_url,
                        'driver_vehicle':driver_vehicle,
                        'responseData': {
                            'driver_id': driver.id,
                            'name': driver.name,
                            'mobile_number': driver.mobile_number,
                            'email': driver.email,
                            'city': driver.city,
                            'islogged': driver.islogged,
                            'supplier_code': driver.supplier_code,
                        }
                    }
                    return response
                else:
                    response_data = {
                        'success': False,
                        # 'error': True,
                        'msg': 'OTP Not Matched!',
                        'errors': "Incorrect OTP!",
                        'status': status.HTTP_404_NOT_FOUND,
                    }
                    return Response(response_data, status=status.HTTP_404_NOT_FOUND)
                
            else:
                response_data = {
                    'success': False,
                    # 'error': True,
                    'msg': 'Login Failed',
                    'errors': "Incorrect Mobile Number!",
                    'status': status.HTTP_404_NOT_FOUND,
                }
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            response_data = {
                'success': False,
                #'error': True,
                'msg': f'Login Failed: {str(e)}',
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            

class AvailableVehicleView(APIView):
    def post(self,request):
        try:
            vehicle_type = request.data.get('vehicle_type')
            # Assuming latitude and longitude are provided
            driver_latitude = float(request.data.get('driver_latitude'))
            driver_longitude = float(request.data.get('driver_longitude'))
            
            # Convert latitude and longitude to radians
            # Calculate the distance in kilometers (assuming your coordinates are in decimal degrees)
            driver_lat_radians = radians(driver_latitude)
            driver_lon_radians = radians(driver_longitude)
            distance_km = 10.0

            # Calculate the minimum and maximum latitude and longitude values for the bounding box
            lat_distance = distance_km / 111  # 1 degree latitude is approximately 111 kilometers
            lon_distance = distance_km / (111 * cos(driver_lat_radians))
            min_lat = driver_latitude - lat_distance
            max_lat = driver_latitude + lat_distance
            min_lon = driver_longitude - lon_distance
            max_lon = driver_longitude + lon_distance 

            # Filter the available vehicles within the specified distance and vehicle type
            available_vehicles = Vehicle.objects.filter(
                vehicle_type=vehicle_type,
                driver__latitude__range=(min_lat, max_lat),
                driver__longitude__range=(min_lon, max_lon),
                status=True
            )

            # Serialize the available vehicles
            serializer = VehiclesSerializer(available_vehicles, many=True)
            # Access the serialized vehicle data
            serialized_vehicle_data = serializer.data

            # Include serialized driver data within the vehicle data
            for i, vehicle_data in enumerate(serialized_vehicle_data):
                vehicle_data['driver'] = DriverSerializer(available_vehicles[i].driver).data

            # current_url = request.build_absolute_uri()
            current_site = get_current_site(request)
            current_url = f"{request.scheme}://{current_site.domain}"
            
            response_data = {
                'success': True,
                'base_url': current_url,
                'msg': 'Data Found!',
                'responseData': serialized_vehicle_data,
                'status':status.HTTP_200_OK
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            response_data = {
                'success': False,
                #'error': True,
                'msg': f'{str(e)}',
                'status':status.HTTP_500_INTERNAL_SERVER_ERROR
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class PickupLocationView(APIView):
    def post(self,request):
        try:
            if request.method =='POST':
                serializerdata = PickupSerializer(data=request.data)
            if serializerdata.is_valid(): 
                serializerdata.save()
            else:
                return Response({"error":serializerdata.errors})
            
            response_data = {
                'success': True,
                'msg': 'Data Added Successfully!',
                'responseData': serializerdata.data,
                'status':status.HTTP_200_OK
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            response_data = {
                'success': False,
                #'error': True,
                'msg': f'{str(e)}',
                'status':status.HTTP_500_INTERNAL_SERVER_ERROR
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    def get(self,request,user_id):
        try:
            
            records = PickupLocation.objects.filter(user_id=user_id)
            if records.exists():
                serialdata = PickupSerializer(records, many =True)
                response_data = {
                    'success': True,
                    'msg': 'Data Found!',
                    'responseData': serialdata.data,
                    'status':status.HTTP_200_OK
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {
                    'success': False,
                    'msg': 'Data Not Found!',
                    'responseData': None,
                    'status':status.HTTP_404_NOT_FOUND
                }
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)
           
        except Exception as e:
            response_data = {
                'success': False,
                #'error': True,
                'msg': f'{str(e)}',
                'status':status.HTTP_500_INTERNAL_SERVER_ERROR
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def put(self,request):
        try:
            id = request.data.get('id')
            try:
                locationObj = PickupLocation.objects.get(id=id)
                serializeObj = PickupSerializer(locationObj,data=request.data)
                if serializeObj.is_valid():
                    serializeObj.save()
                    response_data = {
                        'success': True,
                        'msg': 'Data updated successfully!',
                        'responseData': serializeObj.data,
                        'status':status.HTTP_200_OK
                    }
                    return Response(response_data, status=status.HTTP_200_OK)
                    
                else:
                    return Response({"error":serializeObj.errors})
            except PickupLocation.DoesNotExist:
                return Response({"msg":"Data Not Found in DB!",'status':False})
            
        except Exception as e:
            response_data = {
                'success': False,
                #'error': True,
                'msg': f'{str(e)}',
                'status':status.HTTP_500_INTERNAL_SERVER_ERROR
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def delete(self,request,id):
        try:
            deleteData = PickupLocation.objects.filter(id=id).delete()
            if deleteData:
                response_data = {
                    'success': True,
                    'msg': 'Record has been deleted!',
                    'status':status.HTTP_200_OK
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {
                    'success': True,
                    'msg': 'Record not deleted!',
                    'status':status.HTTP_400_BAD_REQUEST
                }
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
           
        except Exception as e:
            response_data = {
                'success': False,
                'msg': f'{str(e)}',
                'status':status.HTTP_500_INTERNAL_SERVER_ERROR
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

          
        

class GetPickupLocation(APIView):
    def post(self,request):
        try:
            user_id = request.data.get('user_id')
            id = request.data.get('id')
            records = PickupLocation.objects.filter(Q(user_id=user_id) & Q(status=1) & Q(id=id))
            if records.exists():
                serialdata = PickupSerializer(records, many =True)
                response_data = {
                    'success': True,
                    'msg': 'Data Found!',
                    'responseData': serialdata.data,
                    'status':status.HTTP_200_OK
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {
                    'success': False,
                    'msg': 'Data Not Found!',
                    'responseData': None,
                    'status':status.HTTP_404_NOT_FOUND
                }
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)
           
        except Exception as e:
            response_data = {
                'success': False,
                #'error': True,
                'msg': f'{str(e)}',
                'status':status.HTTP_500_INTERNAL_SERVER_ERROR
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ------------- Order Api -------
# ------------- Order Api -------

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from firebase_admin import messaging

class PushNotification(APIView):
    def post(self, request):
        try:
            if request.method == 'POST':
                device_token = request.data.get('device_token')
                notifications = {
                    "message": {
                        "topic": "news",
                        "notification": {
                            "title": "Breaking News",
                            "body": "New news story available."
                        },
                        "data": {
                            "order_id": "story_12345"
                        }
                    }
                }
                response = self.send_fcm_notification(device_token, notifications)
                # Handle the response if needed

                response_data = {
                    'success': True,
                    'msg': 'Notification sent successfully!',
                    'response':response,
                    'status':status.HTTP_200_OK
                }
                return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            response_data = {
                'success': False,
                'msg': str(e),
                'status':status.HTTP_500_INTERNAL_SERVER_ERROR
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def send_fcm_notification(self, device_token, notifications):
        # Convert all values to strings in the 'data' dictionary
        for key, value in notifications["message"]["data"].items():
            notifications["message"]["data"][key] = str(value)

        message = messaging.Message(
            data=notifications["message"]["data"],  # Use the 'data' parameter with 'data' dictionary
            notification=messaging.Notification(
                title=notifications["message"]["notification"]["title"],
                body=notifications["message"]["notification"]["body"],
                #data=notifications["message"]["data"]["order_id"],
            ),
            token=device_token,
        )
        response = messaging.send(message)
        return response


# class PushNotification(APIView):
#     def post(self, request):
#         try:
#             if request.method == 'POST':
#                 device_token = request.data.get('device_token')
#                 notifications = {
#                     "title": "Breaking News",
#                     "body": "New news story available.",
#                     "story_id": "story_12345"
#                 }
#                 response = self.send_fcm_notification(device_token, notifications)

#                 response_data = {
#                     'success': True,
#                     'msg': 'Notification sent successfully!',
#                     'response':response,
#                 }
#                 return Response(response_data, status=status.HTTP_200_OK)

#         except Exception as e:
#             response_data = {
#                 'success': False,
#                 'msg': str(e),
#             }
#             return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def send_fcm_notification(self, device_token, notifications):
#         message = messaging.Message(
#             data=notifications,  # Use the 'data' parameter with the updated 'notifications' dictionary
#             notification=messaging.Notification(
#                 title=notifications["title"],
#                 body=notifications["body"],
#             ),
#             token=device_token,
#         )
#         response = messaging.send(message)
#         return response


class OrderView(APIView):
    @user_token_required
    def post(self, request):
        try:
            if request.method == 'POST':
                user_id = request.data.get('user')
                today = datetime.now()
                serializerdata = OrderSerializer(data=request.data)
                if serializerdata.is_valid():
                    res = serializerdata.save()
                    userData = User.objects.get(id=user_id)
                    drivers = Driver.objects.filter(status=1).order_by('id')
                    # Save the order into TrackOrder model
                    track_order = TrackOrder(user_id=user_id,order_unique_id=res.order_id,status=res.status,created_at=today)
                    res1 = track_order.save()
                    
                    fcm_token = ''
                    order_unique_id = res.order_id
                    
                    notifications = {
                        "message": {
                            "token": fcm_token,
                            "notification": {
                                "title": "Order Placed",
                                "body": "You have new request."
                            },
                            "data": {
                                "type": 'new',
                                "order_id": order_unique_id
                            }
                        } 
                    }
                    for driver in drivers:
                        if driver.fcm_token:
                            fcm_token1 = driver.fcm_token
                            #return Response({"msg":"Api Called",'data':fcm_token1, 'status':True})
                            notifications["message"]["token"] = fcm_token1
                            self.send_fcm_notification(fcm_token1, notifications)
                        else:
                            continue

                    
                else:
                    return Response({"error": serializerdata.errors})
                
                response_data = {
                    'success': True,
                    'msg': 'Order Placed Successfully!',
                    'responseData': serializerdata.data,
                    'status':status.HTTP_200_OK
                }
                return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            response_data = {
                'success': False,
                'msg': str(e),
                'status':status.HTTP_500_INTERNAL_SERVER_ERROR
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def send_fcm_notification(self, device_token, notifications):
        try:
            if not device_token:
                # Skip sending notification if FCM token is empty
                return

            # Convert all values to strings in the 'data' dictionary
            for key, value in notifications["message"]["data"].items():
                notifications["message"]["data"][key] = str(value)

            message = messaging.Message(
                data=notifications["message"]["data"],
                notification=messaging.Notification(
                    title=notifications["message"]["notification"]["title"],
                    body=notifications["message"]["notification"]["body"],
                ),
                token=device_token,
            )
            response = messaging.send(message)
            return response

        except Exception as e:
            # Log or print the exception for further debugging
            print(f"Error sending FCM notification: {str(e)}")

        
class OrderListView(APIView):
    @user_token_required
    def post(self, request):
        try:
            user_id = int(request.data.get('user'))
            order_status = int(request.data.get('status'))
            
            if order_status in [5, 6]:
                orders = Orders.objects.filter(Q(status=order_status) & Q(user=user_id)).select_related('driver').prefetch_related('package', 'vehicle_type', 'pickup').order_by('-id')
            else:
                orders = Orders.objects.filter((Q(status=1) | Q(status=2) | Q(status=4)) & Q(user=user_id)).select_related('driver').prefetch_related('package', 'vehicle_type', 'pickup').order_by('-id')

            if orders.exists():
                serializer = OrderListSerializer(orders, many=True)

                current_site = get_current_site(request)
                current_url = f"{request.scheme}://{current_site.domain}"
                
                response_data = {
                    'success': True,
                    'base_url': current_url, 
                    'msg': 'Data Found!',
                    'responseData': serializer.data,
                    'status':status.HTTP_200_OK
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {
                    'success': False,
                    'msg': 'Data Not Found!',
                    'responseData': None,
                    'status':status.HTTP_404_NOT_FOUND
                }
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            response_data = {
                'success': False,
                'msg': f'Something Went Wrong: {str(e)}',
                'status':status.HTTP_500_INTERNAL_SERVER_ERROR
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class OrderDetailsView(APIView):
    @user_token_required
    def post(self, request):
        try:
            order_unique_id = request.data.get('order_unique_id')
            user_id = request.data.get('user')
            
            # Use filter to create a queryset
            order_qs = Orders.objects.select_related('driver').prefetch_related('package', 'vehicle_type', 'pickup').filter(order_id=order_unique_id, user=user_id)
            
            # Check if the order exists
            if order_qs.exists():
                order = order_qs.get()
                serializer = OrderListSerializer(order)

                current_site = get_current_site(request)
                current_url = f"{request.scheme}://{current_site.domain}"
                
                if order.driver:
                    driverObj = Driver.objects.get(id=order.driver.id)  # Ensure driver_id is properly referenced
                    company_id = driverObj.user_id
                    distance = int(math.floor(float(serializer.data.get('distance', 0))))  # Adjust indexing if needed
                    delivery_charge_obj = None

                    if company_id:
                        delivery_charge_obj = CompanyDeliveryCharge.objects.filter(
                            Q(user_id=company_id) &
                            Q(start_distance__lte=distance) &
                            Q(end_distance__gte=distance)
                        ).first()

                    charge_serializer = DeliveryChargeSerializer(delivery_charge_obj) if delivery_charge_obj else None

                    response_data = {
                        'success': True,
                        'base_url': current_url, 
                        'msg': 'Data Found!',
                        'responseData': serializer.data,
                        'deliveryCharge': charge_serializer.data if charge_serializer else None,
                        'status': status.HTTP_200_OK
                    }
                else:
                    response_data = {
                        'success': True,
                        'msg': 'Driver Not Found for the Order!',
                        'responseData': serializer.data,
                        'deliveryCharge': None,
                        'status': status.HTTP_200_OK
                    }

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {
                    'success': False,
                    'msg': 'Data Not Found!',
                    'responseData': None,
                    'status': status.HTTP_404_NOT_FOUND
                }
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)

        except Orders.DoesNotExist:
            response_data = {
                'success': False,
                'msg': 'Data Not Found!',
                'responseData': None,
                'status': status.HTTP_404_NOT_FOUND
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            response_data = {
                'success': False,
                'msg': f'Something Went Wrong: {str(e)}',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
class VehicleTypeAPIView(APIView):
    def get(self, request):
        try:
            lang = request.META.get('HTTP_LANG', None) 
           
            #lang = request.data.get('lang')
            vehicles_type = VehicleType.objects.filter(status=1)
            if vehicles_type.exists():
                
                vehicles_type_array = []

                for vtype in vehicles_type:
                    title = vtype.title if lang == 'en' else vtype.title_ar
                    my_object = {"id": vtype.id, "title":title, "slug":vtype.slug, "image":vtype.image }
                    vehicles_type_array.append(my_object)
                serializer = VehiTypeSerializer(vehicles_type_array, many=True)

                # current_url = request.build_absolute_uri()
                current_site = get_current_site(request)
                current_url = f"{request.scheme}://{current_site.domain}"
                
                response_data = {
                    'success': True,
                    'base_url': current_url, 
                    'msg': 'Data Found!',
                    'responseData': serializer.data,
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {
                    'success': False,
                    'msg': 'Data Not Found!',
                    'responseData': None,
                }
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            response_data = {
                'success': False,
                'msg': f'Something Went Wrong: {str(e)}',
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class DriverOrderStatusView(APIView):
    @driver_token_required
    def put(self, request):
        #return Response({"msg": "Api Called!", 'status': True})
        try:
            id = int(request.data.get('id'))
            
            driver_id = int(request.data.get('driver'))
            today = datetime.now()
            today_start = datetime.combine(today, datetime.min.time())
            today_end = datetime.combine(today, datetime.max.time())
            orders = Orders.objects.filter(Q(id=id) & Q(driver_id__isnull=True) | Q(driver_id=driver_id))
            if orders.exists():
                driver_orders = DriverOrders.objects.filter(
                     ((Q(status=2) | Q(status=4))  & Q(driver_id=driver_id) & (Q(created_at__gte=today_start) & Q(created_at__lte=today_end)))
                )
                #driver_orders = DriverOrders.objects.filter(Q(driver_id=driver_id)  & Q(status=2) | Q(status=4) & Q(created_at=today))
                #return Response({'msg':"Already",'data':len(driver_orders),'date':today_end})
                
                if not driver_orders.exists():
                    try:
                        orderObj = Orders.objects.get(id=id)
                        serializeObj = UpdateOrderSerializer(orderObj, data=request.data)
                        if serializeObj.is_valid():
                            updated_order = serializeObj.save()
                            # Update Delivery Charge---
                            driver_id = updated_order.driver.id  # Assuming driver is updated in the order
                            driverObj = Driver.objects.get(id=driver_id)
                            company_id = driverObj.user_id
                            distance = int(math.floor(float(updated_order.distance)))

                            delivery_charge = 0
                            if company_id:
                                delivery_charge_obj = CompanyDeliveryCharge.objects.filter(
                                    Q(user_id=company_id) &
                                    Q(start_distance__lte=distance) &
                                    Q(end_distance__gte=distance)
                                ).first()

                                if delivery_charge_obj:
                                    delivery_charge = delivery_charge_obj.delivery_charge

                            # Update the delivery charge in the order
                            updated_order.delivery_price = updated_order.distance*delivery_charge
                            updated_order.save()
                            #  Endd
                            driver_order = DriverOrders.objects.filter(Q(driver_id=driver_id) & Q(order_id=id))
                            user_id = ""
                            order_unique_id = ""
                            if not driver_order.exists():
                                # driverObj = Driver.objects.get(id=driver_id)
                                # company_id = driverObj.user_id
                                # distance = int(math.floor(float(updated_order.distance)))
                                # if company_id:
                                #     delivery_charge_obj = CompanyDeliveryCharge.objects.filter(
                                #         Q(user_id=company_id) &
                                #         Q(start_distance__lte=distance) &
                                #         Q(end_distance__gte=distance)
                                #     ).first()

                                #     if delivery_charge_obj:
                                #         delivery_charge = delivery_charge_obj.delivery_charge
                                #     else:
                                #         delivery_charge = DeliveryChargeSerializer(delivery_charge_obj)
                                # Get the user associated with the order (assuming there is a user field in the Orders model)
                                user_id = updated_order.user_id
                                package_id = updated_order.package_id
                                pickup_id = updated_order.pickup_id
                                vehicle_type_id = updated_order.vehicle_type_id
                                order_unique_id = updated_order.order_id
                                pickup_time = updated_order.pickup_time
                                pickup_otp_verification = updated_order.pickup_otp_verification
                                destination_address = updated_order.destination_address
                                destination_latitude = updated_order.destination_latitude

                                country_code = updated_order.country_code
                                destination_mobile = updated_order.destination_mobile

                                destination_longitude = updated_order.destination_longitude
                                destination_apartment = updated_order.destination_apartment
                                destination_area_street_block = updated_order.destination_area_street_block
                                destination_floor = updated_order.destination_floor
                                destination_house_building = updated_order.destination_house_building
                                order_status = updated_order.status
                                delivery_price = updated_order.delivery_price
                                paymentId = updated_order.paymentId
                                paymentStatus = updated_order.paymentStatus
                                paymentMethod = updated_order.paymentMethod
                                distance = updated_order.distance
                                
                                driver_id = request.data.get('driver')

                                driverObj = Driver.objects.get(id = driver_id)
                                company_id = driverObj.user_id


                                # Save the order into DriverOrders model
                                driver_order = DriverOrders(order_id=id,user_id=user_id,package_id=package_id,vehicle_type_id=vehicle_type_id,pickup_id=pickup_id,order_unique_id=order_unique_id,pickup_time= pickup_time,destination_address=destination_address,country_code=country_code,destination_mobile=destination_mobile, destination_latitude=destination_latitude,destination_longitude=destination_longitude,destination_apartment=destination_apartment,destination_area_street_block=destination_area_street_block,destination_floor=destination_floor,destination_house_building=destination_house_building,status=order_status,driver_id=driver_id,pickup_otp_verification=pickup_otp_verification,delivery_price=delivery_price,company_id=company_id,paymentId=paymentId,paymentStatus=paymentStatus,paymentMethod=paymentMethod,distance=distance)
                                res = driver_order.save()

                                # Save the order into TrackOrder model
                                track_order = TrackOrder(driver_id=driver_id,user_id=user_id,order_unique_id=order_unique_id,status=order_status)
                                res1 = track_order.save()
                            else: 
                                driver_order = DriverOrders.objects.filter(Q(driver_id=driver_id) & Q(order_id=id)).update(status=updated_order.status)
                                
                            #device_token = request.data.get('device_token')
                            
                            userData = User.objects.get(id=user_id)
                            if userData.fcm_token:
                                notifications = {
                                    "message": {
                                        "token": userData.fcm_token,
                                        "notification": {
                                            "title": "Order Status",
                                            "body": "Your Order Has Been Accepted."
                                        },
                                        "data": {
                                            "type": 'status',
                                            "order_id": order_unique_id
                                        }
                                    }
                                }
                                fcm_token = userData.fcm_token
                                notifications["message"]["token"] = fcm_token
                                self.send_fcm_notification(fcm_token, notifications)
                            

                            response_data = {
                                'success': True,
                                'msg': 'Order status updated successfully!',
                                'responseData': serializeObj.data,
                                'status':status.HTTP_200_OK
                            }
                            return Response(response_data, status=status.HTTP_200_OK)

                        else:
                            return Response({"error": serializeObj.errors})
                    except Orders.DoesNotExist:
                        return Response({"msg": "Data Not Found in DB!", 'status': False})
                else:
                    return Response({'msg':"You have already an order!",'status':False})
                
            else:
                return Response({'msg':"Order all ready taken By Other Driver",'status':False})

        except Exception as e:
            response_data = {
                'success': False,
                'msg': f'{str(e)}',
                'status':status.HTTP_500_INTERNAL_SERVER_ERROR
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    
    def send_fcm_notification(self, device_token, notifications):
        # Convert all values to strings in the 'data' dictionary
        for key, value in notifications["message"]["data"].items():
            notifications["message"]["data"][key] = str(value)

        message = messaging.Message(
            data=notifications["message"]["data"],  # Use the 'data' parameter with 'data' dictionary
            notification=messaging.Notification(
                title=notifications["message"]["notification"]["title"],
                body=notifications["message"]["notification"]["body"],
                #data=notifications["message"]["data"]["order_id"],
            ),
            token=device_token,
        )
        response = messaging.send(message)
        return response
    
class DriverPickupDeliverStatus(APIView):
    @driver_token_required
    def put(self, request):
        try:
            # Extract and validate request data
            order_id = int(request.data.get('id'))
            driver_id = int(request.data.get('driver'))
            order_status = int(request.data.get('status'))
            current_time = datetime.now()

            try:
                # Fetch the order object
                order_obj = Orders.objects.get(id=order_id)
                serialize_obj = UpdateOrderSerializer(order_obj, data=request.data)

                if serialize_obj.is_valid():
                    updated_order = serialize_obj.save()
                    
                    # Update driver order status
                    DriverOrders.objects.filter(
                        Q(driver_id=driver_id) & Q(order_id=order_id)
                    ).update(status=updated_order.status)
                    
                    # Save the order into TrackOrder model
                    track_order = TrackOrder(
                        driver_id=driver_id,
                        user_id=updated_order.user_id,
                        order_unique_id=updated_order.order_id,
                        status=order_status,
                        created_at=current_time
                    )
                    track_order.save()

                    # Fetch user data
                    user_data = User.objects.get(id=order_obj.user_id)
                    msg = "Order Pickup By Driver!" if order_status == 4 else "Order Delivered Successfully To Destination!"

                    # Construct URLs for notifications
                    current_site = get_current_site(request)
                    current_url = f"{request.scheme}://{current_site.domain}"
                    tracking_url = f"{current_url}/api/track-order"
                    track_msg = f"Order {order_obj.order_id} is out for delivery. Check the status at {tracking_url} or call 22211221"

                    if user_data.fcm_token:
                        notifications = {
                            "message": {
                                "token": user_data.fcm_token,
                                "notification": {
                                    "title": "Order Status",
                                    "body": msg
                                },
                                "data": {
                                    "type": 'status',
                                    "order_id": str(order_obj.order_id)
                                }
                            }
                        }
                        tracking_notifications = {
                            "message": {
                                "token": user_data.fcm_token,
                                "notification": {
                                    "title": "Order Status",
                                    "body": track_msg
                                },
                                "data": {
                                    "type": 'status',
                                    "order_id": str(order_obj.order_id)
                                }
                            }
                        }

                        # Send FCM notifications
                        self.send_fcm_notification(user_data.fcm_token, notifications)
                        if order_status == 4:
                            self.send_fcm_notification(user_data.fcm_token, tracking_notifications)

                    response_data = {
                        'success': True,
                        'msg': 'Order status updated successfully!',
                        'responseData': serialize_obj.data,
                        'status': status.HTTP_200_OK,
                    }
                    return Response(response_data, status=status.HTTP_200_OK)
                else:
                    return Response({"error": serialize_obj.errors}, status=status.HTTP_400_BAD_REQUEST)
            except Orders.DoesNotExist:
                return Response({"msg": "Order not found!", 'status': False}, status=status.HTTP_404_NOT_FOUND)
          
        except Exception as e:
            response_data = {
                'success': False,
                'msg': str(e),
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def send_fcm_notification(self, device_token, notifications):
        # Ensure data values are strings
        for key, value in notifications["message"]["data"].items():
            notifications["message"]["data"][key] = str(value)

        message = messaging.Message(
            data=notifications["message"]["data"],
            notification=messaging.Notification(
                title=notifications["message"]["notification"]["title"],
                body=notifications["message"]["notification"]["body"]
            ),
            token=device_token,
        )
        response = messaging.send(message)
        return response
class DriverOrderListView(APIView):
    #@driver_token_required
    def get(self, request):
        try:
            today = datetime.now().date()
            #print("Okayyyyy  Today date",today)
            next_seven_days = today + timedelta(days=7)
            orders = Orders.objects.filter(Q(status=1) & Q(created_at__range=[today, next_seven_days])).select_related('driver').prefetch_related('package', 'vehicle_type','pickup','user').order_by('-id')
            if orders.exists():
                serializer = OrderListSerializer(orders, many=True)

                current_site = get_current_site(request)
                current_url = f"{request.scheme}://{current_site.domain}"
                
                response_data = {
                    'success': True,
                    'base_url': current_url, 
                    'msg': 'Data Found!',
                    'responseData': serializer.data,
                    'status': status.HTTP_200_OK,
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {
                    'success': False,
                    'msg': 'Data Not Found!',
                    'responseData': None,
                    'status': status.HTTP_404_NOT_FOUND,
                }
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            response_data = {
                'success': False,
                'msg': f'Something Went Wrong: {str(e)}',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        try: 
            driver_id = request.data.get('driver_id')
            orders = DriverOrders.objects.filter(Q(driver=driver_id) & ~Q(status=3)).select_related('driver').prefetch_related('package', 'vehicle_type','pickup').order_by('-id')
            if orders.exists():
                serializer = DriverAcceptedOredersSerializer(orders, many=True)

                current_site = get_current_site(request)
                current_url = f"{request.scheme}://{current_site.domain}"
                
                response_data = {
                    'success': True,
                    'base_url': current_url, 
                    'msg': 'Data Found!',
                    'responseData': serializer.data,
                    'status': status.HTTP_200_OK,
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {
                    'success': False,
                    'msg': 'Data Not Found!',
                    'responseData': None,
                    'status': status.HTTP_404_NOT_FOUND,
                }
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            response_data = {
                'success': False,
                'msg': f'Something Went Wrong: {str(e)}',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class DeliveryCharges(APIView):
    def post(self, request):
        try:
            distance = request.data.get('distance')
            id = 1
            singledata = DeliveryCharge.objects.get(id=id)

            # At this point, singledata should exist if the 'id' is valid
            total_charges = Decimal(Decimal(distance) * singledata.delivery_charge)
            response_data = {
                'success': True,
                'msg': 'Data Found!',
                'responseData': total_charges,
                'status': status.HTTP_200_OK,
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except DeliveryCharge.DoesNotExist:
            response_data = {
                'success': False,
                'msg': 'Data Not Found!',
                'responseData': None,
                'status': status.HTTP_404_NOT_FOUND,
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            response_data = {
                'success': False,
                'msg': f'Something Went Wrong: {str(e)}',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class DriverOrderHomeView(APIView):
#     def post(self, request):
#         try:
#             logger = logging.getLogger(__name__)

#             today = datetime.now()
#             today_start = datetime.combine(today, datetime.min.time())
#             today_end = datetime.combine(today, datetime.max.time())

#             driver_id = request.data.get('driver_id')
#             order_unique_id = request.data.get('order_unique_id')

#             logger.info(f"Received request for driver_id={driver_id}, order_unique_id={order_unique_id}")
#             orders = Orders.objects.none()
#             if not order_unique_id and  driver_id:
#                 orders = Orders.objects.filter(
#                     Q(order_id=order_unique_id) &
#                     ((Q(status=1)) & (Q(created_at__gte=today_start) & Q(created_at__lte=today_end)))
#                 ).select_related('driver').prefetch_related('package', 'vehicle_type', 'pickup').order_by('-id')
#             elif order_unique_id and driver_id:
#                 orders = Orders.objects.filter(
#                     (Q(driver=driver_id) & Q(order_id=order_unique_id)) &
#                     ((Q(status=2) | Q(status=4)) & (Q(created_at__gte=today_start) & Q(created_at__lte=today_end)))
#                 ).select_related('driver').prefetch_related('package', 'vehicle_type', 'pickup').order_by('-id')


#             if orders.exists():
#                 serializer = OrderListSerializer(orders, many=True)

#                 current_site = get_current_site(request)
#                 current_url = f"{request.scheme}://{current_site.domain}"

#                 response_data = {
#                     'success': True,
#                     'base_url': current_url,
#                     'msg': 'Data Found!',
#                     'responseData': serializer.data,
#                 }
#                 return Response(response_data, status=status.HTTP_200_OK)
#             else:
#                 response_data = {
#                     'success': False,
#                     'msg': 'Data Not Found!',
#                     'responseData': None,
#                 }
#                 return Response(response_data, status=status.HTTP_404_NOT_FOUND)

#         except Exception as e:
#             logger.error(f'Something Went Wrong: {str(e)}')
#             response_data = {
#                 'success': False,
#                 'msg': f'Something Went Wrong: {str(e)}',
#             }
#             return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class DriverOrderHomeView(APIView):
    @driver_token_required
    def post(self, request):
        try:
            today = datetime.now()
            today_start = datetime.combine(today, datetime.min.time())
            today_end = datetime.combine(today, datetime.max.time())

            driver_id = request.data.get('driver')
            order_unique_id = request.data.get('order_unique_id')
            distance = 4
            charge_serializer = ''
            
            if order_unique_id:
                orders = Orders.objects.filter(
                    Q(order_id=order_unique_id) &
                    (
                        (Q(status=1)) &
                        (Q(created_at__gte=today_start) & Q(created_at__lte=today_end))
                    )
                ).select_related('driver').prefetch_related('package', 'vehicle_type', 'pickup').order_by('-id')
            else:
                orders = Orders.objects.filter(
                    Q(driver=driver_id) &
                    (
                        (Q(status=2) | Q(status=4)) &
                        (Q(created_at__gte=today_start) & Q(created_at__lte=today_end))
                    )
                ).select_related('driver').prefetch_related('package', 'vehicle_type', 'pickup').order_by('-id')
            # today = datetime.now().date()
            # orders = Orders.objects.filter(Q(driver=driver_id) & Q(status=2) | Q(status=4) & Q(created_at=today)).select_related('driver').prefetch_related('package', 'vehicle_type','pickup').order_by('-id')
            if orders.exists():
                # ----New Logic----
                #---- END -----
                serializer = OrderListSerializer(orders, many=True)
                current_site = get_current_site(request)
                current_url = f"{request.scheme}://{current_site.domain}"

                driverObj = Driver.objects.get(id=driver_id)
                company_id = driverObj.user_id
                distance = int(math.floor(float(serializer.data[0].get('distance', None))))
                delivery_charge_obj = ''
                if company_id:
                    delivery_charge_obj = CompanyDeliveryCharge.objects.filter(
                        Q(user_id=company_id) &
                        Q(start_distance__lte=distance) &
                        Q(end_distance__gte=distance)
                    ).first()

                    if delivery_charge_obj:
                        charge_serializer = DeliveryChargeSerializer(delivery_charge_obj)
                    else:
                        charge_serializer = DeliveryChargeSerializer(delivery_charge_obj)
                    

                        
                #return Response({"data":charge_serializer.data})
                response_data = {
                    'success': True,
                    'base_url': current_url, 
                    'msg': 'Data Found!',
                    'responseData': serializer.data,
                    'deliveryData':charge_serializer.data,
                    'status': status.HTTP_200_OK,
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {
                    'success': False,
                    'msg': 'Data Not Found!',
                    'responseData': None,
                    'status': status.HTTP_404_NOT_FOUND,
                }
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            response_data = {
                'success': False,
                'msg': f'Something Went Wrong: {str(e)}',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

# ----------- User Order Status-------------- 
# ----------- User Order Status--------------
class UserOrderStatus(APIView):
    def put(self, request):
        try:
            id = int(request.data.get('id'))
            user_id = int(request.data.get('user_id'))
            order_status = int(request.data.get('status'))
            
            try:
                singleOrd = Orders.objects.get(id=id)
                
                if singleOrd.status in [4, 5]:  # Check if the status is 4 or 5
                    return Response({'msg': "You cannot cancel the order", 'status': status.HTTP_200_OK})
                
                orderObj = Orders.objects.get(id=id)
                serializeObj = UpdateUserOrderSerializer(orderObj, data=request.data)
                if serializeObj.is_valid():
                    updated_order = serializeObj.save()
                    driver_order = DriverOrders.objects.filter(Q(user_id=user_id) & Q(order_id=id)).update(status=updated_order.status)         
                    
                    # Save the order into TrackOrder model
                    track_order = TrackOrder(driver_id=updated_order.driver_id,user_id=user_id,order_unique_id=updated_order.order_unique_id,status=order_status)
                    res1 = track_order.save()

                    driverData = None
                    if orderObj.driver_id:
                        try:
                            driverData = Driver.objects.get(id=orderObj.driver_id)
                        except Driver.DoesNotExist:
                            pass

                    if driverData and driverData.fcm_token:
                        notifications = {
                            "message": { 
                                "token": driverData.fcm_token,
                                "notification": {
                                    "title": "Order Status",
                                    "body": "Order cancelled by user!."
                                },
                                "data": {
                                    "type": 'status',
                                    "order_id": orderObj.order_id
                                }
                            }
                        }
                        fcm_token = driverData.fcm_token
                        notifications["message"]["token"] = fcm_token
                        if order_status == 6:
                            self.send_fcm_notification(fcm_token, notifications)
                        
                    response_data = {
                        'success': True,
                        'msg': 'Order status updated successfully!',
                        'responseData': serializeObj.data,
                        'status': status.HTTP_200_OK,
                    }
                    return Response(response_data, status=status.HTTP_200_OK)

                else:
                    return Response({"error": serializeObj.errors})
            except Orders.DoesNotExist:
                return Response({"msg": "Data Not Found in DB!", 'status': False})
          
        except Exception as e:
            response_data = {
                'success': False,
                'msg': f'{str(e)}',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def send_fcm_notification(self, device_token, notifications):
        # Convert all values to strings in the 'data' dictionary
        for key, value in notifications["message"]["data"].items():
            notifications["message"]["data"][key] = str(value)

        message = messaging.Message(
            data=notifications["message"]["data"],  # Use the 'data' parameter with 'data' dictionary
            notification=messaging.Notification(
                title = notifications["message"]["notification"]["title"],
                body = notifications["message"]["notification"]["body"],
                #data=notifications["message"]["data"]["order_id"],
            ),
            token=device_token,
        )
        response = messaging.send(message)
        return response

class UpdateUserView(APIView):
    @user_token_required
    def post(self, request):
        try:
            user_id = int(request.data.get('user_id'))
            
            fullname = request.data.get('fullname')
            email = request.data.get('email')
            phone = request.data.get('phone')
            country_code = request.data.get('country_code')
            files = request.FILES.get('profile_pic')

            record = User.objects.get(id=user_id)
                
            if files is not None:
                fss = FileSystemStorage()
                filename = fss.save(files.name,files)
                url = fss.url(filename)
            else:
                files = record.profile_pic 
            
            if User.objects.filter(Q(email=email) & ~Q(id=user_id)).exists():
                response_data = {
                    'msg':"email already exist",
                    'success': False,
                    'status': status.HTTP_400_BAD_REQUEST,
                }
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            if User.objects.filter(Q(phone=phone) & ~Q(id=user_id)).exists():
                response_data = {
                    'msg':"Phone already exist",
                    'success': False,
                    'status': status.HTTP_400_BAD_REQUEST,
                }
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            else:
                updated = User.objects.filter(id=user_id).update(fullname=fullname,email=email,country_code=country_code,phone=phone,profile_pic=files)
                if updated:
                    response = Response()
                    response.data = {
                        'success': True,
                        'msg': 'User profile updated successfully',
                        'status': status.HTTP_200_OK,
                    }
                    return response
                else:
                    return Response({"status":status.HTTP_400_BAD_REQUEST,"msg":"Not Updated!"})
           
        except Exception as e:
            response_data = {
                'success': False,
                'msg': f'Something Went Wrong: {str(e)}',
                'status':status.HTTP_500_INTERNAL_SERVER_ERROR
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class DriverLocationStatus(APIView):
    @driver_token_required
    def put(self, request):
        try:
            driver_id = int(request.data.get('driver_id'))
            latitude = request.data.get('latitude')
            longitude = request.data.get('longitude')
                
            try:
                driverObj = Driver.objects.get(id=driver_id)
                serializeObj = UpdateDriverLocationSerializer(driverObj, data=request.data)
                if serializeObj.is_valid():
                    updated_order = serializeObj.save()
                    
                    response_data = {
                        'success': True,
                        'msg': 'Driver Location updated!',
                        'responseData': serializeObj.data,
                        'status':status.HTTP_200_OK
                    }
                    return Response(response_data, status=status.HTTP_200_OK)

                else:
                    return Response({"error": serializeObj.errors})
            except Driver.DoesNotExist:
                return Response({"msg": "Data Not Found in DB!", 'status': False})
          
        except Exception as e:
            response_data = {
                'success': False,
                'msg': f'{str(e)}',
                'status':status.HTTP_500_INTERNAL_SERVER_ERROR
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class MyfatoorahView(APIView):
    def get(self, request):
        try:
            response_data = {
                'success': True,
                'msg': 'Payment Successfully!',
                'status':status.HTTP_200_OK
                
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            response_data = {
                'success': False,
                'msg': f'Something Went Wrong: {str(e)}',
                'status':status.HTTP_500_INTERNAL_SERVER_ERROR
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class GetPrivacyPolicy(APIView):
    def get(self,request):
        try:
            lang = request.META.get('HTTP_LANG', None) 
            id = 1
            records = Pages.objects.filter(Q(status=1) & Q(id=id))
            if records.exists():
                pages_array = []

                for rec in records:
                    name = rec.name if lang == 'en' else rec.name_ar
                    description = rec.description if lang == 'en' else rec.description_ar
                    #return Response({"msg":"Success","data":size})
                    my_object = {"id": rec.id, "name":name, "description":description }
                    pages_array.append(my_object)
                serialdata = PagesSerializer(pages_array, many =True)
                response_data = {
                    'success': True,
                    'msg': 'Data Found!',
                    'responseData': serialdata.data,
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {
                    'success': False,
                    'msg': 'Data Not Found!',
                    'responseData': None,
                }
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)
           
        except Exception as e:
            response_data = {
                'success': False,
                #'error': True,
                'msg': f'{str(e)}',
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateOrderStatusView(APIView):
    def put(self, request):
        try:
            order_id = int(request.data.get('order_id'))
            paymentId = request.data.get('paymentId')
            paymentStatus = request.data.get('paymentStatus')
            paymentMethod = request.data.get('paymentMethod')
                
            try:
                orderObj = Orders.objects.get(id=order_id)
                serializeObj = UpdateOrderPaySerializer(orderObj, data=request.data)
                if serializeObj.is_valid():
                    updated_order = serializeObj.save()
                    driver_order = DriverOrders.objects.filter(Q(order_id=order_id)).update(paymentId=updated_order.paymentId,paymentStatus=updated_order.paymentStatus,paymentMethod=updated_order.paymentMethod)  


                    # ----- Notification For Driver ------
                    driver_id = orderObj.driver_id
                    if driver_id:
                        driverData = Driver.objects.get(id=driver_id)
                        if driverData.fcm_token:
                            msg = "Payment Successfully !"
                            notifications = {
                                "message": {
                                    "token": driverData.fcm_token,
                                    "notification": {
                                        "title": "Order Status",
                                        "body": str(msg)
                                    },
                                    "data": {
                                        "type": 'status',
                                        "order_id": orderObj.order_id
                                    }
                                }
                            }
                            fcm_token = driverData.fcm_token
                            notifications["message"]["token"] = fcm_token
                            self.send_fcm_notification(fcm_token, notifications) 
                    #------- END ------------
                    
                    userData = User.objects.get(id=orderObj.user_id)
                    msg = "You Paid Successfully !"
                       
                    if userData.fcm_token:
                        notifications = {
                            "message": {
                                "token": userData.fcm_token,
                                "notification": {
                                    "title": "Order Status",
                                    "body": str(msg)
                                },
                                "data": {
                                    "type": 'status',
                                    "order_id": orderObj.order_id
                                }
                            }
                        }
                        fcm_token = userData.fcm_token
                        notifications["message"]["token"] = fcm_token
                        self.send_fcm_notification(fcm_token, notifications)       

                    response_data = {
                        'success': True,
                        'msg': 'You paid successfully!',
                        'responseData': serializeObj.data,
                        'status':status.HTTP_200_OK
                    }
                    return Response(response_data, status=status.HTTP_200_OK)

                else:
                    return Response({"error": serializeObj.errors})
            except Orders.DoesNotExist:
                return Response({"msg": "Data Not Found in DB!", 'status': False})
          
        except Exception as e:
            response_data = {
                'success': False,
                'msg': f'{str(e)}',
                'status':status.HTTP_500_INTERNAL_SERVER_ERROR
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def send_fcm_notification(self, device_token, notifications):
        # Convert all values to strings in the 'data' dictionary
        for key, value in notifications["message"]["data"].items():
            notifications["message"]["data"][key] = str(value)

        message = messaging.Message(
            data=notifications["message"]["data"],  # Use the 'data' parameter with 'data' dictionary
            notification=messaging.Notification(
                title=notifications["message"]["notification"]["title"],
                body=notifications["message"]["notification"]["body"],
                #data=notifications["message"]["data"]["order_id"],
            ),
            token=device_token,
        )
        response = messaging.send(message)
        return response
    


# ----------- Logout User Status--------------
class LogoutUser(APIView):
    def put(self, request):
        try:
            user_id = int(request.data.get('user_id'))
            fcm_token = request.data.get('fcm_token')
            
            try:
                userObj = User.objects.filter(id=user_id).update(fcm_token=fcm_token) 
                if userObj:   
                    response_data = {
                        'success': True,
                        'msg': 'FCM Token Removed!',
                    }
                    return Response(response_data, status=status.HTTP_200_OK)

                
            except Orders.DoesNotExist:
                return Response({"msg": "Something Went Wrong!!", 'status': False})
          
        except Exception as e:
            response_data = {
                'success': False,
                'msg': f'{str(e)}',
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

# ----------- Logout User Status--------------
class DriverUser(APIView):
    def put(self, request):
        try:
            driver_id = int(request.data.get('driver_id'))
            fcm_token = request.data.get('fcm_token')
            
            try:
                userObj = User.objects.filter(id=user_id).update(fcm_token=fcm_token) 
                if userObj:   
                    response_data = {
                        'success': True,
                        'msg': 'FCM Token Removed!',
                        'status':status.HTTP_200_OK
                    }
                    return Response(response_data, status=status.HTTP_200_OK)

                
            except Orders.DoesNotExist:
                return Response({"msg": "Something Went Wrong!!", 'status': False})
          
        except Exception as e:
            response_data = {
                'success': False,
                'msg': f'{str(e)}',
                'status':status.HTTP_500_INTERNAL_SERVER_ERROR
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ----------- Logout User Status--------------
class LogoutDriver(APIView):
    def put(self, request):
        try:
            driver_id = int(request.data.get('driver_id'))
            fcm_token = request.data.get('fcm_token')
            
            try: 
                userObj = Driver.objects.filter(id=driver_id).update(fcm_token=fcm_token) 
                if userObj:   
                    response_data = {
                        'success': True,
                        'msg': 'Driver FCM Token Removed!',
                        'status':status.HTTP_200_OK
                    }
                    return Response(response_data, status=status.HTTP_200_OK)

                
            except Orders.DoesNotExist:
                return Response({"msg": "Something Went Wrong!!", 'status': False})
          
        except Exception as e:
            response_data = {
                'success': False,
                'msg': f'{str(e)}',
                'status':status.HTTP_500_INTERNAL_SERVER_ERROR
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class AllPage(APIView):
    def get(self,request):
        try:
            lang = request.META.get('HTTP_LANG', None) 
            records = Pages.objects.filter(status=1)
            if records.exists():
                pages_array = []

                for rec in records:
                    name = rec.name if lang == 'en' else rec.name_ar
                    description = rec.description if lang == 'en' else rec.description_ar
                    #return Response({"msg":"Success","data":size})
                    my_object = {"id": rec.id, "name":name, "description":description }
                    pages_array.append(my_object)
                serialdata = PagesSerializer(pages_array, many =True)
                response_data = {
                    'success': True,
                    'msg': 'Data Found!',
                    'responseData': serialdata.data,
                    'status':status.HTTP_200_OK
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {
                    'success': False,
                    'msg': 'Data Not Found!',
                    'responseData': None,
                    'status':status.HTTP_404_NOT_FOUND
                }
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)
           
        except Exception as e:
            response_data = {
                'success': False,
                #'error': True,
                'msg': f'{str(e)}',
                'status':status.HTTP_500_INTERNAL_SERVER_ERROR
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

       
        
class SupportData(APIView):
    def get(self,request):
        try:
            records = Support.objects.get(id=1)
            if records:
                serialdata = SupportSerializer(records, many =False)
                response_data = {
                    'success': True,
                    'msg': 'Data Found!',
                    'responseData': serialdata.data,
                    'status':status.HTTP_200_OK
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {
                    'success': False,
                    'msg': 'Data Not Found!',
                    'responseData': None,
                    'status':status.HTTP_404_NOT_FOUND
                }
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)
           
        except Exception as e:
            response_data = {
                'success': False,
                #'error': True,
                'msg': f'{str(e)}',
                'status':status.HTTP_500_INTERNAL_SERVER_ERROR
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ForgotPassword(APIView):
    def post(self,request):
        try:
            email = request.data.get('email')
            user = User.objects.filter(email=email).first()
            if user is None:
                response_data = {
                    'success': False,
                    'status':status.HTTP_404_NOT_FOUND,
                    'msg': 'Email not registered',
                }
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)
            else:
                otp = random.randint(1000, 9999)
                subject, from_email, to = 'Forget Password OTP', 'shankar.wxit@gmail.com', email
                #text_content = 'This is an important message.'
                msg = f'<p>Your OTP is: <strong>{otp}</strong></p>'
                msg1 = EmailMultiAlternatives(subject, msg, from_email, [to])
                msg1.content_subtype = 'html'
                msg1.send()

                User.objects.filter(id=user.id).update(otp=otp)
                response_data = {
                    'success': True,
                    'msg': 'Your OTP sent to your Email!',
                    #'responseData': serialdata.data,
                    'status':status.HTTP_200_OK
                }
                return Response(response_data, status=status.HTTP_200_OK)
           
        except Exception as e:
            response_data = {
                'success': False,
                #'error': True,
                'msg': f'{str(e)}',
                'status':status.HTTP_500_INTERNAL_SERVER_ERROR
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class ResetPassword(APIView):
    def post(self,request):
        try:
            email = request.data.get('email')
            password = request.data.get('password')
            cpassword = request.data.get('cpassword')
            otp = request.data.get('otp')
            user = User.objects.filter(email=email).first()
            
            if user is None:
                response_data = {
                    'success': False,
                    'status':status.HTTP_404_NOT_FOUND,
                    'msg': 'Email not registered',
                }
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)
            if password != cpassword:
                response_data = {
                    'success': False,
                    'status':status.HTTP_404_NOT_FOUND,
                    'msg': 'Confirm Password Not Matched !',
                }
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)
            
            if otp != user.otp:
                response_data = {
                    'success': False,
                    'status':status.HTTP_404_NOT_FOUND,
                    'msg': 'OTP Not Matched !',
                }
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)
            else:
                otp = ''
                User.objects.filter(id=user.id).update(otp=otp)
                # Hash the password
                hashed_password = make_password(password)
                user.password = hashed_password
                # Save the user object
                user.save()
                
                response_data = {
                    'success': True,
                    'msg': 'Your password has been updated !',
                    #'responseData': serialdata.data,
                    'status':status.HTTP_200_OK
                }
                return Response(response_data, status=status.HTTP_200_OK)
           
        except Exception as e:
            response_data = {
                'success': False,
                #'error': True,
                'msg': f'{str(e)}',
                'status':status.HTTP_500_INTERNAL_SERVER_ERROR
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class DepositView(APIView):
    def post(self, request, format=None):
        try:
            serializer = DepositSerializer(data=request.data)
            if serializer.is_valid():
                user_id = int(request.data.get('user'))
                note = request.data.get('note')
                paymentId = request.data.get('paymentId')
                paymentStatus = request.data.get('paymentStatus')
                amount = serializer.validated_data['amount']
                wallet = Wallet.objects.get(user=user_id)
                wallet.balance += amount
                wallet.save()
                Transaction.objects.create(wallet=wallet, amount=amount, transaction_type='credit',paymentId=paymentId,paymentStatus=paymentStatus,note=note)

                response_data = {
                    'success': True,
                    'msg': 'Deposit Successful',
                    'wallet_balance': wallet.balance,
                    'status': status.HTTP_200_OK
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {
                    'success': False,
                    'msg': serializer.errors,
                    'status': status.HTTP_400_BAD_REQUEST
                }
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            response_data = {
                'success': False,
                'msg': f'An error occurred: {str(e)}',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class WithdrawView(APIView):
    def post(self,request,format=None):
        try:
            serializer = WithdrawSerializer(data=request.data)
            if serializer.is_valid():
                user_id = request.data.get('user')
                note = request.data.get('note')
                amount = serializer.validated_data['amount']
                wallet = Wallet.objects.get(user=user_id)
                if wallet.balance >= amount:
                    wallet.balance -= amount
                    wallet.save()
                    Transaction.objects.create(wallet=wallet, amount=amount, transaction_type='debit',note=note)
                    response_data = {
                        'success': True,
                        'msg':"Withdrawal successful",
                        'status': status.HTTP_200_OK
                    }
                    return Response(response_data, status=status.HTTP_200_OK)
                   
                else:
                    response_data = {
                        'success': True,
                        'msg':"Insufficient balance",
                        'status': status.HTTP_400_BAD_REQUEST
                    }
                    return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            else:
                response_data = {
                    'success': True,
                    'msg':serializer.errors,
                    'status': status.HTTP_400_BAD_REQUEST
                }
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            response_data = {
                'success': False,
                'msg': f'An error occurred: {str(e)}',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TransactionHistoryAPIView(APIView):
    def post(self, request):
        try:
            user_id = int(request.data.get('user'))
            wallet = Wallet.objects.get(user=user_id)
            transactions = Transaction.objects.filter(wallet=wallet)
            serializer = TransactionSerializer(transactions, many=True)

            response_data = {
                'success': True,
                'msg':"Data Found!",
                'status': status.HTTP_200_OK,
                'responseData': serializer.data,
                'wallet_balance': wallet.balance
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Wallet.DoesNotExist:
            response_data = {
                'success': True,
                'msg':"Data Not Found!",
                'status': status.HTTP_404_NOT_FOUND,
                'responseData': None
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)

        
class GetCourierCompany(APIView):
    def get(self,request):
        try:
            records = User.objects.filter(Q(is_active=1) & Q(is_courier=1))
            if records.exists():
                serialdata = UserSerializer(records, many =True)
                response_data = {
                    'success': True,
                    'msg': 'Data Found!',
                    'responseData': serialdata.data,
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {
                    'success': False,
                    'msg': 'Data Not Found!',
                    'responseData': None,
                }
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)
           
        except Exception as e:
            response_data = {
                'success': False,
                #'error': True,
                'msg': f'{str(e)}',
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
class GetDriverView(APIView):
    def post(self,request):
        try:
            user_id = request.data.get('company_id')
            records = Driver.objects.filter(Q(status=1) & Q(user_id=user_id))
            if records.exists():
                serialdata = DriverByCompanySerializer(records, many =True)
                response_data = {
                    'success': True,
                    'msg': 'Data Found!',
                    'responseData': serialdata.data,
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {
                    'success': False,
                    'msg': 'Data Not Found!',
                    'responseData': None,
                }
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)
           
        except Exception as e:
            response_data = {
                'success': False,
                #'error': True,
                'msg': f'{str(e)}',
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderPlacedB2B(APIView):
    def post(self, request):
        try:
            if request.method == 'POST':
                user_id = request.data.get('user')
                company_id = request.data.get('company_id')
                
                serializerdata = OrderSerializerB2B(data=request.data)
                if serializerdata.is_valid():
                    res = serializerdata.save()
                    userData = User.objects.get(id=user_id)
                    drivers = Driver.objects.filter(Q(status=1) & Q(user_id=company_id)).order_by('id')
                    
                    fcm_token = ''
                    order_unique_id = res.order_id
                    id = res.id

                    notifications = {
                        "message": {
                            "token": fcm_token,
                            "notification": {
                                "title": "Order Placed",
                                "body": "You have new request."
                            },
                            "data": {
                                "type": 'new',
                                "order_id": order_unique_id
                            }
                        } 
                    }
                    for driver in drivers:
                        if driver.fcm_token:
                            fcm_token1 = driver.fcm_token
                            #return Response({"msg":"Api Called",'data':fcm_token1, 'status':True})
                            notifications["message"]["token"] = fcm_token1
                            self.send_fcm_notification(fcm_token1, notifications)
                        else:
                            continue
                else:
                    return Response({"error": serializerdata.errors})
                
                response_data = {
                    'success': True,
                    'msg': 'Order Placed Successfully!',
                    'responseData': serializerdata.data,
                    'status':status.HTTP_200_OK
                }
                return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            response_data = {
                'success': False,
                'msg': str(e),
                'status':status.HTTP_500_INTERNAL_SERVER_ERROR
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def send_fcm_notification(self, device_token, notifications):
        try:
            if not device_token:
                # Skip sending notification if FCM token is empty
                return

            # Convert all values to strings in the 'data' dictionary
            for key, value in notifications["message"]["data"].items():
                notifications["message"]["data"][key] = str(value)

            message = messaging.Message(
                data=notifications["message"]["data"],
                notification=messaging.Notification(
                    title=notifications["message"]["notification"]["title"],
                    body=notifications["message"]["notification"]["body"],
                ),
                token=device_token,
            )
            response = messaging.send(message)
            return response

        except Exception as e:
            # Log or print the exception for further debugging
            print(f"Error sending FCM notification: {str(e)}")

class TrackOrderAPIView(APIView):
    def post(self, request):
        try:
            order_unique_id = request.data.get('order_unique_id')
            track_orders = TrackOrder.objects.filter(order_unique_id=order_unique_id)
            if track_orders.exists():
                serializer = TrackOrderSerializer(track_orders, many=True)

                current_site = get_current_site(request)
                current_url = f"{request.scheme}://{current_site.domain}"
                
                response_data = {
                    'success': True,
                    'base_url': current_url, 
                    'msg': 'Data Found!',
                    'responseData': serializer.data,
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {
                    'success': False,
                    'msg': 'Data Not Found!',
                    'responseData': None,
                }
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            response_data = {
                'success': False,
                'msg': f'Something Went Wrong: {str(e)}',
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)     


class DriverLocation(APIView):
    def put(self,request):
        try:
            id = request.data.get('driver_id')
            latitude = request.data.get('latitude')
            longitude = request.data.get('longitude')
            try:
                driverObj = Driver.objects.filter(id=id).update(latitude=latitude,longitude=longitude)
                serializeObj = DriverSerializer(driverObj,data=request.data)
                if driverObj:
                    response_data = {
                        'success': True,
                        'msg': 'Data updated successfully!',
                        'status':status.HTTP_200_OK
                    }
                    return Response(response_data, status=status.HTTP_200_OK)
                    
                else:
                    response_data = {
                        'success': False,
                        'msg': 'Data not updated !',
                        'status':status.HTTP_500_INTERNAL_SERVER_ERROR
                    }
                    return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except PickupLocation.DoesNotExist:
                return Response({"msg":"Data Not Found in DB!",'status':False})
            
        except Exception as e:
            response_data = {
                'success': False,
                #'error': True,
                'msg': f'{str(e)}',
                'status':status.HTTP_500_INTERNAL_SERVER_ERROR
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        