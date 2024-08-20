from django.contrib import admin
from django.urls import path,include
from . import views
from .views import *
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [ 
    path('',views.Home.index,name="/"), 
    path('courier-signup/',views.Home.courier_signup,name="courier-signup"),
    path('signup-process',views.Home.signup_process,name="signup-process"),  

    path('privacy-policy',views.Home.privacy_policy,name="privacy-policy"), 
    path('term-condition',views.Home.term_condition,name="term-condition"),
    path('privacy_policy',views.Home.privacyPolicy,name="privacy_policy"), 
    path('term_condition',views.Home.termCondition,name="term_condition"),

    path('payment-success',views.Home.payment_success,name="payment-success"), 
    path('payment-failled',views.Home.payment_failled,name="payment-failled"), 
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 