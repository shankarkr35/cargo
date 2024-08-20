from django.contrib import admin
from django.urls import path,include
from . import views
from .views import *

urlpatterns = [
    path('process_payment', PaymentView.as_view(), name='process_payment'),
    
]