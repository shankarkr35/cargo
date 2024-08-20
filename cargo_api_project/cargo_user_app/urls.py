from django.urls import path,include
from .views import *
# from .views import PickLocationSearchAPIView
# from rest_framework import routers
# router = routers.DefaultRouter()
# router.register(r'pickup-locations-search', LocationViewSet, basename='pickup-locations-search')

urlpatterns = [ 
    path('register/', UserRegistrationView.as_view(), name='register'), 
    path('login/', UserLoginView.as_view(), name='login'),    
    # path('profile/', UserProfileView.as_view(), name='profile'),
    # path('changepassword/', UserChangePasswordView.as_view(), name='changepassword'),
    path('send-reset-password-email/', SendPasswordResetEmailView.as_view(), name='send-reset-password-email'),
    path('reset-password/confirm/<uid>/<token>/', UserPasswordResetView.as_view(), name='reset-password'),
 
    path('search-pickup-location/', PickLocationViewSet.as_view(), name='pickup-location-search'),
    # path('pickup-locations/', PickLocationViewSet.as_view(), name='pick-location-list'),
    # path('pickup-locations/<int:pk>/', PickLocationViewSet.as_view(), name='pick-location-detail'),
    # path('package-location/', PackageListCreateAPIView.as_view(), name='droplocation-search'),
     
    path('package-size/', PackageSizeAPIView.as_view(), name='package-detail'),
    path('vehicle-type/', VehicleAPIView.as_view(), name='vehicle-type'),
    
]

 











    #path('remember-me/', RememberMeView.as_view(), name='user-login-remember-me'),
   
    #  path('api/Drop-locations/', DropLocationListCreateAPIView.as_view(), name='pickup-location-list'),
    # path('api/Drop-locations/<int:pk>/', DropLocationRetrieveUpdateDeleteAPIView.as_view(), name='pickup-location-detail'),

