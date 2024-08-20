


from django.urls import path
from .views import DriverSignUpView
from . import views

urlpatterns = [
    path('signup/', DriverSignUpView.as_view(), name='driver-signup'),
    #path('admin/auth/', AdminAuthenticationView.as_view(), name='admin-auth'),
 
    path('driver-management/',views.Drivers.index,name="driver-management"), 
    path('add-driver/',views.Drivers.add,name="add-driver"), 
    path('create-driver/',views.Drivers.create, name="create-driver"),
    path('edit-driver/<int:id>',views.Drivers.edit,name="edit-driver"),  
    path('update-driver/',views.Drivers.update, name="update-driver"),   
    path('delete-driver/',views.Drivers.delete, name="delete-driver"),
    path('update-status/',views.Drivers.update_status, name="update-status"),

    #----- Driver Orders --------  
    path('driver-orders-management/<int:id>',views.DriverOrder.index, name='driver-orders-management'),
    # path('delete-driver-orders/',views.DriverOrder.delete, name="delete-driver-orders"),
    # path('update-driver-orders-status/',views.DriverOrder.update_status, name="update-driver-orders-status"),
 
    # ---- Vehicles Route ---- 
    path('vehicle-management/',views.Vehicles.index, name='vehicle-management'),
    path('add-vehicle/',views.Vehicles.add,name="add-vehicle"),
    path('create-vehicle/',views.Vehicles.create, name="create-vehicle"),
    path('edit-vehicle/<int:id>',views.Vehicles.edit,name="edit-vehicle"),
    path('update-vehicle/',views.Vehicles.update, name="update-vehicle"),  
    path('delete-vehicle/',views.Vehicles.delete, name="delete-vehicle"),
    path('update-vehicle-status/',views.Vehicles.update_status, name="update-vehicle-status"), 

    #-----Orders--------  
    path('orders-management/',views.Order.index, name='orders-management'),
    path('delete-orders/',views.Order.delete, name="delete-vehicle"),
    path('update-orders-status/',views.Order.update_status, name="update-orders-status"),

    # ---------- Company Delivery Charge Route ------------
    path('delivery-charge-management/',views.Delivery.index, name='delivery-management'),
    path('add-delivery-charge/',views.Delivery.add,name="add-delivery-charge"), 
    path('create-charge/',views.Delivery.create, name="create-charge"), 
    path('edit-delivery-charge/<int:id>',views.Delivery.edit,name="edit-delivery-charge"),
    path('update-charge/',views.Delivery.update, name="update-charge"),  
    path('delete-charge/',views.Delivery.delete, name="delete-charge"),
    path('update-delivery-status/',views.Delivery.update_status, name="update-delivery-status"),

    # ------- Forgot Password -----
    path('forgot-password/',views.ResetPassword.index, name='forgot-password'),
    path('courier-email-check/',views.ResetPassword.courier_email_check, name='courier-email-check'),
    path('reset-password/',views.ResetPassword.resetPass, name='reset-password'),
    path('verify-otp-and-reset-password/', views.ResetPassword.verify_otp_and_reset_password, name='verify_otp_and_reset_password'),

]












