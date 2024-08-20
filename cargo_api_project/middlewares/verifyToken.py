# from django.shortcuts import render
# import jwt
# # Load environment variables from .env file
# import os
# from dotenv import load_dotenv
# # Load environment variables from .env file 
# load_dotenv()
 
# def verify(token):
#     SECRET_KEY = os.getenv('SECRET_KEY')
#     payload = jwt.decode(token,SECRET_KEY, algorithms=['HS256'])
#     return payload


# your_app_name/middleware.py
import jwt
import os
from dotenv import load_dotenv
load_dotenv()
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
User = get_user_model() 

def user_token_required(view_func):
    def wrapper(self, request, *args, **kwargs):
        #token = self.request.COOKIES.get('user_token')
        token = request.data.get('user_token');  
        provided_user_id = request.data.get('user')  # Assuming you send user_id in the request data

        if not token or not provided_user_id:
            response_data = {
                'success': False,
                'msg': 'Token or user_id not provided',
                'status': status.HTTP_401_UNAUTHORIZED,
            }
            return Response(response_data, status=status.HTTP_401_UNAUTHORIZED)

        try:
            payload = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=['HS256'])
            user_id = payload['user_id']

            # Check if the provided user_id matches the user_id in the token payload
            if user_id != int(provided_user_id):
                response_data = {
                    'success': False,
                    'msg': 'Invalid user_id',
                    'status': status.HTTP_401_UNAUTHORIZED,
                }
                return Response(response_data, status=status.HTTP_401_UNAUTHORIZED)

            # Assuming you have a User model
            user = User.objects.filter(id=user_id).first()
            
            if not user:
                response_data = {
                    'success': False,
                    'msg': 'User not found',
                    'status': status.HTTP_401_UNAUTHORIZED,
                }
                return Response(response_data, status=status.HTTP_401_UNAUTHORIZED)

            # Check if the token version in the payload matches the user's current token version
            if user.token_version != payload.get('token_version'):
                response_data = {
                    'success': False,
                    'msg': 'Invalid token version',
                    'status': status.HTTP_401_UNAUTHORIZED,
                }
                return Response(response_data, status=status.HTTP_401_UNAUTHORIZED)

            self.user_id = user_id
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
