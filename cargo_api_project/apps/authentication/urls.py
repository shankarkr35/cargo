from django.urls import path,include
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin-login',views.AuthAdminCheck.index,name="admin-login"), 
    path('login-auth/',views.AuthAdminCheck.login_check,name="login-auth"),
    path('signout/',views.AuthAdminCheck.signout,name="signout"), 
    path('admin-dashboard/', views.AuthAdminCheck.admin_dashboard, name="admin-dashboard"),

    path('driver-management/',views.Drivers.index,name="driver-management"),
    path('add-driver/',views.Drivers.add,name="add-driver"), 
    path('create-driver/',views.Drivers.create, name="create-driver"),
    path('edit-driver/<int:id>',views.Drivers.edit,name="edit-driver"), 
    path('update-driver/',views.Drivers.update, name="update-driver"), 
    path('delete-driver/',views.Drivers.delete, name="delete-driver"),
    path('update-status/',views.Drivers.update_status, name="update-status"),

    # ----------------- Courier manage ------------------- 
    path('courier-management/',views.CourierCompany.index,name="courier-management"),
    path('add-courier/',views.CourierCompany.add,name="add-courier"),
    path('create-courier/',views.CourierCompany.create, name="create-courier"),
    path('edit-courier/<int:id>',views.CourierCompany.edit,name="edit-courier"),
    path('update-courier/',views.CourierCompany.update, name="update-courier"), 
    path('courier-details/<int:id>',views.CourierCompany.view,name="courier-details"),
    path('delete-courier/',views.CourierCompany.delete, name="delete-courier"),
    path('update-courier-status/',views.CourierCompany.update_status, name="update-courier-status"),

    # ------------------ Vehicle type---------------------------
    path('vehicle-type-management/',views.VehicleTypes.index,name="vehicle-type-management"),
    path('add-vehicle-type/',views.VehicleTypes.add,name="add-vehicle-type"),
    path('create-vehicle-type/',views.VehicleTypes.create, name="create-vehicle-type"),
    path('edit-vehicle-type/<int:id>',views.VehicleTypes.edit,name="edit-vehicle-type"),
    path('update-vehicle-type/',views.VehicleTypes.update, name="update-vehicle-type"), 
    path('delete-vehicle-type/',views.VehicleTypes.delete, name="delete-vehicle-type"),
    path('update-vehicle-type-status/',views.VehicleTypes.update_status, name="update-vehicle-type-status"),

    # ------------ Vehicles Route ------------
    path('vehicle-management/',views.Vehicles.index, name='vehicle-management'),
    path('add-vehicle/',views.Vehicles.add,name="add-vehicle"),
    path('create-vehicle/',views.Vehicles.create, name="create-vehicle"),
    path('edit-vehicle/<int:id>',views.Vehicles.edit,name="edit-vehicle"),
    path('update-vehicle/',views.Vehicles.update, name="update-vehicle"), 
    path('delete-vehicle/',views.Vehicles.delete, name="delete-vehicle"),
    path('update-vehicle-status/',views.Vehicles.update_status, name="update-vehicle-status"),

    # ---------- Package Route ------------
    path('package-management/',views.Package.index, name='package-management'),
    path('add-package/',views.Package.add,name="add-package"),
    path('create-package/',views.Package.create, name="create-package"), 
    path('edit-package/<int:id>',views.Package.edit,name="edit-package"),
    path('update-package/',views.Package.update, name="update-package"),   
    path('delete-package/',views.Package.delete, name="delete-package"),
    path('update-package-status/',views.Package.update_status, name="update-package-status"),

    #----- Orders -------- 
    path('orders-management/<int:id>',views.Order.index, name='orders-management'),
    path('order-details/<int:id>',views.Order.order_details, name='order-details'),
    path('delete-orders/',views.Order.delete, name="delete-vehicle"),
    path('update-orders-status/',views.Order.update_status, name="update-orders-status"),
    path('load_order_items',views.Order.load_order_items,name="load_order_items"),

    #----- Users --------
    path('user-management/',views.Users.index, name='user-management'),
    path('transaction-history/<int:id>',views.TransacionHistory.index, name='transaction-history'),
 
    # ------  Contract Url manage ----
    path('contact-files/',views.Contract.index,name="contact-files"),
    path('update-contact-files/',views.Contract.update, name="update-contact-files"), 
    

    # ------ Delivery Charge Url manage ----
    path('delivery-charge/',views.DeliveryCharges.index,name="delivery-charge"),
    path('update-delivery-charge/',views.DeliveryCharges.update, name="update-delivery-charge"), 

    # -------- Color management ---------
    path('color-management/',views.Colors.index,name="color-management"),
    path('add-color/',views.Colors.add,name="add-color"),
    path('create-color/',views.Colors.create, name="create-color"),
    path('edit-color/<int:id>',views.Colors.edit,name="edit-color"),
    path('update-color/',views.Colors.update, name="update-color"), 
    path('delete-color/',views.Colors.delete, name="delete-color"),
    path('update-color-status/',views.Colors.update_status, name="update-color-status"),

    # --------- BAnners ----------------
    path('banner-management/',views.Banner.index,name="banner-management"),
    path('add-banner/',views.Banner.add,name="add-banner"),
    path('create-banner/',views.Banner.create, name="create-banner"),
    path('edit-banner/<int:id>',views.Banner.edit,name="edit-banner"),
    path('update-banner/',views.Banner.update, name="update-banner"),
    path('delete-banner/',views.Banner.delete, name="delete-banner"),
    path('update-banner-status/',views.Banner.update_status, name="update-banner-status"),

    path('about-management/',views.AboutUs.edit,name="about-management"),
    path('update-about-us/',views.AboutUs.update, name="update-about-us"),

    # -------- Pages management --------- 
    path('page-management/',views.Page.index,name="page-management"),
    path('add-page/',views.Page.add,name="add-page"),
    path('create-page/',views.Page.create, name="create-page"),
    path('edit-page/<int:id>',views.Page.edit,name="edit-page"),
    path('update-page/',views.Page.update, name="update-page"), 
    path('delete-page/',views.Page.delete, name="delete-page"),
    path('update-page-status/',views.Page.update_status, name="update-page-status"),

    #========== Support Page ==========
    path('support-management/',views.SupportPage.edit,name="support-management"),
    path('update-support/',views.SupportPage.update, name="update-support"),
    
    # ========== Business Page ============
    path('business-management/',views.Business.index,name="business-management"),
    path('add-business/',views.Business.add,name="add-business"),
    path('create-business/',views.Business.create, name="create-business"),
    path('edit-business/<int:id>',views.Business.edit,name="edit-business"),
    path('update-business/',views.Business.update, name="update-business"), 
    path('delete-business/',views.Business.delete, name="delete-business"),
    path('update-business-status/',views.Business.update_status, name="update-business-status"),

    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 
 