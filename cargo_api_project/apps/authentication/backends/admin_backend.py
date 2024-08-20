from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class AdminBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Retrieve the user based on the username
            user = User.objects.get(email=username)
            # Check if the password is correct and if the user is an admin
            if user.check_password(password) and user.is_admin:
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            # Retrieve the user based on user_id and check if they are an admin
            return User.objects.get(pk=user_id, is_admin=True)
        except User.DoesNotExist:
            return None
