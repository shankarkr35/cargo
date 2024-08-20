
import jwt
import os
from dotenv import load_dotenv
load_dotenv()
from rest_framework.response import Response
from rest_framework import status
from cargo_driver_app.models import *

def driver_token_required(view_func):
    def wrapper(self, request, *args, **kwargs):
        #token = self.request.COOKIES.get('driver_token')  # Use self.request
        token = request.data.get('driver_token')
        provided_driver_id = request.data.get('driver')  # Assuming you send driver_id in the request data

        if not token or not provided_driver_id:
            response_data = {
                'success': False,
                'msg': 'Token or driver_id not provided',
                'status': status.HTTP_401_UNAUTHORIZED,
            }
            return Response(response_data, status=status.HTTP_401_UNAUTHORIZED)

        try:
            payload = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=['HS256'])
            driver_id = payload['driver_id']

            # Check if the provided user_id matches the driver_id in the token payload
            if driver_id != int(provided_driver_id):
                response_data = {
                    'success': False,
                    'msg': 'Invalid driver_id',
                    'status': status.HTTP_401_UNAUTHORIZED,
                }
                return Response(response_data, status=status.HTTP_401_UNAUTHORIZED)

            # Assuming you have a User model
            driver = Driver.objects.filter(id=driver_id).first()
            
            if not driver:
                response_data = {
                    'success': False,
                    'msg': 'Driver not found',
                    'status': status.HTTP_401_UNAUTHORIZED,
                }
                return Response(response_data, status=status.HTTP_401_UNAUTHORIZED)

            # Check if the token version in the payload matches the driver's current token version
            if driver.token_version != payload.get('token_version'):
                response_data = {
                    'success': False,
                    'msg': 'Invalid token version',
                    'status': status.HTTP_401_UNAUTHORIZED,
                }
                return Response(response_data, status=status.HTTP_401_UNAUTHORIZED)

            self.driver_id = driver_id
        except jwt.ExpiredSignatureError:
            response_data = {
                'success': False,
                'msg': 'Token has expired',
                'status': status.HTTP_401_UNAUTHORIZED,
            }
            return Response(response_data, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            response_data = {
                'success': False,
                'msg': 'Invalid token',
                'status': status.HTTP_401_UNAUTHORIZED,
            }
            return Response(response_data, status=status.HTTP_401_UNAUTHORIZED)

        return view_func(self, request, *args, **kwargs)  # Include 'self' in the call

    return wrapper
