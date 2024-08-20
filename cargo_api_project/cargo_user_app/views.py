from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from .renderers import UserRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
#from datetime import timedelta
from .models import *
from rest_framework.decorators import api_view
import requests
from .serializers import *
from rest_framework import viewsets 
from django.conf import settings
from decimal import Decimal
import googlemaps
from geopy.geocoders import Nominatim
import jwt
from datetime import datetime,timedelta,timezone
import json
import os
from django.db.models import Q
from apps.wallet.models import *

# Generate Token Manually
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }



class UserRegistrationView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        try:
            serializer = UserRegistrationSerializer(data=request.data)
            fcm_token = request.data.get('fcm_token')
            if serializer.is_valid():
                user = serializer.save() 
                updatedUser = User.objects.filter(id=user.id).update(fcm_token=fcm_token)
                #token = get_tokens_for_user(user)
                expiry = datetime.utcnow() + timedelta(minutes=60)
                current_time = datetime.now(timezone.utc)
                issued_time = int(current_time.timestamp())
                payload = {
                    'user_id': user.id,
                    'expiry': expiry.strftime('%Y-%m-%d %H:%M:%S'),
                    'iat': issued_time
                }

                # Encode the payload as a JWT
                jwt_token = jwt.encode(payload, os.getenv('SECRET_KEY'), algorithm='HS256')
                #token = jwt.encode(json_payload, 'secret_key', algorithm='HS256').decode('utf-8')
                response = Response()
                response.set_cookie(key='jwt',value=jwt_token,httponly=True)
                response.data = {
                    'success': True,
                    # 'error': False,
                    'msg': 'Login Success',
                    'status': status.HTTP_200_OK,
                    'token': jwt_token,
                    'responseData': {
                        'id': user.id,
                        'email': user.email,
                        'phone': user.phone,  
                        'name': user.fullname,
                        'country_code': user.country_code
                    }
                }
                
                return response
                
            else:
                errors = {}
                for field, field_errors in serializer.errors.items():
                    field_errors = [str(error) for error in field_errors]
                    errors[field] = field_errors

                response_data = {
                    'success': False,
                    'responseMessage': errors,
                    'status': '400'
                }
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            response_data = {
                'success': False,
                'responseMessage': f'Registration Failed: {str(e)}',
                'status': '500'
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserLoginView(APIView):
    renderer_classes = [UserRenderer]
    def post(self, request, format=None): 
        try:
            fcm_token = request.data.get('fcm_token')
            #session_token = request.data.get('session_token')
            serializer = UserLoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            email = serializer.validated_data.get('email') 
            password = serializer.validated_data.get('password')
            user = authenticate(email=email, password=password)
 
            if user is not None:
                if user.token_version is None:
                    user.token_version = 0
                # Update the token_version
                user.token_version += 1
                user.save()
                # token = get_tokens_for_user(user)
                expiry = datetime.utcnow() + timedelta(minutes=60)
                current_time = datetime.now(timezone.utc)
                issued_time = int(current_time.timestamp())
                payload = {
                    'user_id': user.id,
                    'expiry': expiry.strftime('%Y-%m-%d %H:%M:%S'),
                    'iat': issued_time,
                    'token_version': user.token_version,  # Include token_version in the payload
                }

                # Encode the payload as a JWT
                jwt_token = jwt.encode(payload, os.getenv('SECRET_KEY'), algorithm='HS256')
                # Save FCM Token and Session Token in a single query
                user.fcm_token = fcm_token
                user.session_token = jwt_token
                user.save()

                # Check if the user has a wallet, create one if not
                wallet, created = Wallet.objects.get_or_create(user=user, defaults={'balance': 0})
                #updatedUser = User.objects.filter(id=user.id).update(fcm_token=fcm_token,session_token=jwt_token)
               
                response = Response()
                response.set_cookie(key='user_token',value=jwt_token,httponly=True)
                 
                response.data = {
                    'success': True,
                    # 'error': False,
                    'msg': 'Login Success',
                    'status': status.HTTP_200_OK,
                    'token': jwt_token,
                    'responseData': {
                        'id': user.id,
                        'email': user.email,
                        'phone': user.phone,  
                        'name': user.fullname,
                        'country_code': user.country_code,
                        'wallet_balance': float(wallet.balance)  # Include wallet balance in response
                    }
                }
                return response
            else:
                response_data = {
                    'success': False,
                    # 'error': True,
                    'msg': 'Login Failed',
                    'errors': "Incorrect login credentials email or password!",
                    #'responseData': None       
                }
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            response_data = {
                'success': False,
                # 'error': True,
                'msg': f'Login Failed: {str(e)}',
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class SendPasswordResetEmailView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        try:
            serializer = SendPasswordResetEmailSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            email = serializer.validated_data.get('email')
            user = User.objects.filter(email=email).first()

            if user is None:
                response_data = {
                    'success': False,
                    # 'error': True,
                    'msg': 'Email not registered',
                }
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)

            # Logic to send password reset email

            return Response({'msg': 'Password Reset link sent. Please check your email'}, status=status.HTTP_200_OK)

        except serializers.ValidationError as e:
            response_data = {
                'success': False,
                # 'error': True,
                'msg':  e.detail,
                # 'errors': e.detail,
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            response_data = {
                # 'success': False,
                'error': True,
                'msg': f'Failed to send password reset email: {str(e)}',
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserPasswordResetView(APIView):
    renderer_classes = [UserRenderer] 

    def post(self, request, uid, token, format=None): 
        try:
            serializer = UserPasswordResetSerializer(data=request.data, context={'uid': uid, 'token': token})
            serializer.is_valid(raise_exception=True)

            new_password = serializer.validated_data.get('new_password')
            confirm_password = serializer.validated_data.get('confirm_password')

            if new_password != confirm_password:
                response_data = {
                    'success': False,
                    # 'error': True,
                    'msg': 'New password and confirm password do not match',
                }
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

            # Logic to reset user password

            return Response({'msg': 'Password Reset Successfully'}, status=status.HTTP_200_OK)

        except serializers.ValidationError as e:
            response_data = {
                'success': False,
                # 'error': True,
                'msg': e.detail,
                # 'errors': e.detail,
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            response_data = {
                'success': False,
                # 'error': True,
                'msg': f'Failed to reset password: {str(e)}',
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)








class UserProfileView(APIView):
  renderer_classes = [UserRenderer]
#   permission_classes = [IsAuthenticated]
  def get(self, request, format=None):
    serializer = UserProfileSerializer(request.user)
    print("user profile details:::",serializer)
    return Response(serializer.data, status=status.HTTP_200_OK)

'''class UserChangePasswordView(APIView):
  renderer_classes = [UserRenderer]
#   permission_classes = [IsAuthenticated]
  def post(self, request, format=None):
    serializer = UserChangePasswordSerializer(data=request.data, context={'user':request.user})
    serializer.is_valid(raise_exception=True)
    return Response({'msg':'Password Changed Successfully'}, status=status.HTTP_200_OK)
'''


#pickup location api
#pickup location api 
class PickLocationViewSet(APIView):
    def get(self, request):
        pickup_locations = PickupLocation.objects.all()
        serializer = PickupLocationSerializer(pickup_locations, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        try:
            serializer = PickupLocationSerializer(data=request.data)
            if serializer.is_valid():
                instance = serializer.save()
                response_data = {
                    'success': True,
                    'responseMessage': 'Location created successfully',
                    'status': '201',
                    'responseData': [{
                        'id': instance.id,
                        'address': instance.address,
                        'area_street_block': instance.area_street_block,
                        'house_building': instance.house_building,
                        'floor': instance.floor,
                        'apartment': instance.apartment,
                        'latitude': instance.latitude,
                        'longitude': instance.longitude
                    }]
                }

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                errors = serializer.errors

                response_data = {
                    'success': False,
                    'responseMessage': errors,
                    'status': '400'
                }

                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            response_data = {
                'success': False,
                'responseMessage': f'Location creation failed: {str(e)}',
                'status': '500'
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

'''

    def post(self, request, format=None):
            try:
                serializer = PickupLocationSerializer(data=request.data)
                if serializer.is_valid():
                    # Retrieve latitude and longitude from the request data
                    latitude = serializer.validated_data['latitude']
                    longitude = serializer.validated_data['longitude']

                    # Perform reverse geocoding
                    geolocator = Nominatim(user_agent="geoapiExercises")
                    location = geolocator.reverse(f"{latitude}, {longitude}")
                    address = location.raw['address']
                    print("full address",address)
                    # Save the PickupLocation instance
                    instance = serializer.save()

                    response_data = {
                        'success': True,
                        'responseMessage': 'Location created successfully',
                        'status': '201',
                        'responseData': [{
                            'id': instance.id,
                            'address': address,
                        }]
                    }

                    return Response(response_data, status=status.HTTP_201_CREATED)
                else:
                    errors = serializer.errors

                    response_data = {
                        'success': False,
                        'responseMessage': errors,
                        'status': '400'
                    }

                    return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                response_data = {
                    'success': False,
                    'responseMessage': f'Location creation failed: {str(e)}',
                    'status': '500'
                }
                return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

'''



#DROP LOCATION API


# package info class
class PackageSizeAPIView(APIView):
    def post(self, request):
        try:
            serializer = PackageSerializer(data=request.data)
            if serializer.is_valid():
                package_size = serializer.validated_data['size']
                weight_range = ''

                if package_size == 'small':
                    weight_range = '0-3kg'
                elif package_size == 'medium':
                    weight_range = '3-6kg'
                elif package_size == 'large':
                    weight_range = '6-9kg'
                else:
                    response_data = {
                        'success': False,
                        'message': 'Invalid package size'
                    }
                    return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

                serializer.validated_data['weight_range'] = weight_range
                serializer.save()

                response_data = {
                    'success': True,
                    'message': 'Data saved successfully.',
                    'package_id': serializer.instance.package_id,
                    'package_size': serializer.instance.size,
                    'weight_range': serializer.instance.weight_range,
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
            else:
                response_data = {
                    'success': False,
                    'errors': serializer.errors
                }
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            response_data = {
                'success': False,
                'message': 'Something went wrong',
                'error': str(e)
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        try:
            package_size = request.query_params.get('size', None)
            if package_size:
                packages = Cargo_package.objects.filter(size=package_size)
            else:
                packages = Cargo_package.objects.all()

            serializer = PackageSerializer(packages, many=True)
            response_data = {
                'success': True,
                'responsedata': serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            response_data = {
                'success': False,
                'message': 'Something went wrong',
                'error': str(e)
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




           

class VehicleAPIView(APIView):
    def get(self, request): 
        try:
            vehicles = Vehicle.objects.filter(Q(status=1)).select_related('driver').prefetch_related('color', 'vehicle_type').order_by('-id')
            #vehicles = Vehicle.objects.all()
            serializer = VehicleSerializer(vehicles, many=True)
            response_data = {
                'success': True,
                'responseData': serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            response_data = {
                'success': False,
                'message': str(e)
            }
            
    
    def post(self, request):
        serializer = VehicleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response_data = {
                'success': True,
                'message': 'Data saved successfully.'
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        response_data = {
            'success': False,
            'errors': serializer.errors
        }
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)