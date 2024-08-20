"""cargo_api_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import couriers
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.conf.urls.i18n import i18n_patterns
# from rest_framework import routers
# from cargo_user_app.views import LocationViewSet

# router = routers.DefaultRouter()
# router.register(r'locations', LocationViewSet, basename='locations')

urlpatterns = [
    path('admin/', admin.site.urls), 
    path('api/user/', include('cargo_user_app.urls')), 

    #------Admin-----  
    path('auth/', include('apps.authentication.urls')),
    
    # ----- Home route----
    path('',include('apps.home.urls')),
    

    
    # path('api/', include(router.urls)),
     path('api1/driver/', include('cargo_driver_app.urls')), 

    #  ----Courier-------- 
    #---Agent Dashboard-----  
    path('courier-login/',couriers.AuthCourierCheck.index, name='courier-login'),
    path('courier-login-auth/',couriers.AuthCourierCheck.login_check, name='courier-login-auth'),
    path('courier-dashboard/',couriers.AuthCourierCheck.courier_dashboard, name='courier-dashboard'),
    path('courier-logout/',couriers.AuthCourierCheck.signout, name='courier-logout'),

    path('courier/', include('cargo_driver_app.urls')),
 
    # API's By Shankar
    path('api/',include('apps.api.urls')),

    # ----- MyFatoorah  route----
    path('myfatoorah/',include('apps.myfaturaah.urls')),
    #path('forget-password1',views.ForgotPassword1.as_view(),name="forget-password1"),

]+ static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)


urlpatterns += i18n_patterns (
    path('',include('apps.home.urls')),
)
    