# middleware.py
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user_model

User = get_user_model()

class SeparateSessionMiddleware(MiddlewareMixin):
    def process_request(self, request):
        print("SeparateSessionMiddleware: process_request called")
        print(f"Session Keys at Request: {list(request.session.keys())}")

        # Handle admin user
        if '_auth_admin_user_id' in request.session:
            user_id = request.session['_auth_admin_user_id']
            print(f"Admin User ID Retrieved: {user_id}")
            try:
                request.admin_user = User.objects.get(pk=user_id)
                request.user = request.admin_user  # Optional: Set request.user to admin_user
            except Exception as e:
                print(f"Error retrieving admin user: {e}")
        else:
            request.admin_user = None

        # Handle courier user
        if '_auth_courier_user_id' in request.session:
            user_id = request.session['_auth_courier_user_id']
            print(f"Courier User ID Retrieved: {user_id}")
            try:
                request.courier_user = User.objects.get(pk=user_id)
                request.user = request.courier_user  # Optional: Set request.user to courier_user
            except Exception as e:
                print(f"Error retrieving courier user: {e}")
        else:
            request.courier_user = None

    def process_response(self, request, response):
        print("SeparateSessionMiddleware: process_response called")
        print(f"Session Keys before Response: {list(request.session.keys())}")

        # Ensure session keys are set correctly
        if hasattr(request, 'admin_user') and request.admin_user:
            request.session['_auth_admin_user_id'] = request.admin_user.pk
        else:
            request.session.pop('_auth_admin_user_id', None)

        if hasattr(request, 'courier_user') and request.courier_user:
            request.session['_auth_courier_user_id'] = request.courier_user.pk
        else:
            request.session.pop('_auth_courier_user_id', None)

        print(f"Session Keys after Response: {list(request.session.keys())}")
        return response




