from django.contrib import admin
from django.urls import path,include
from . import views
from .views import * 
 
urlpatterns = [ 
    path('homepage', HomeAPIView.as_view(), name='homepage'),
    path('user-signup', UserAuthView.as_view(), name='user-signup'), 
    #path('user-login', AuthLoginView.as_view(), name='user-login'), 
    path('user-profile',UserView.as_view(),name="user-profile"),
    path('update-profile',UpdateUserView.as_view(),name="update-profile"),
    path('logout-user', LogoutUser.as_view(), name='logout-user'),
 
    #  --------Driver API --------  
    path('driver-login', DriverLoginView.as_view(), name='driver-login'),
    path('logout-driver', LogoutDriver.as_view(), name='logout-driver'),
    path('verify-driver-otp', VerifyDriverOtpView.as_view(), name='verify-driver-otp'),
    path('available-vehicle', AvailableVehicleView.as_view(), name='available-vehicle'),
    path('driver-order-list', DriverOrderList.as_view(), name='driver-order-list'),
    path('driver-order-status', DriverOrderStatusView.as_view(), name='driver-order-status'),
    path('driver-pickup-deliver-status', DriverPickupDeliverStatus.as_view(), name='driver-pickup-deliver-status'),
    path('driver-accepted-orders', DriverOrderListView.as_view(), name='driver-accepted-orders'),
 
    #  --------Pickup Location API --------
    path('add-pickup-location', PickupLocationView.as_view(), name='add-pickup-location'),
    path('get-all-location/<int:user_id>',PickupLocationView.as_view(),name="get-all-location"),
    path('update-location',PickupLocationView.as_view(),name="update-location"),
    path('delete-single-location/<int:id>',PickupLocationView.as_view(),name="delete-single-location"),
    path('get-single-location',GetPickupLocation.as_view(),name="get-single-location"),

    #--------- Vehicle Type --------
    path('vehicle-type', VehicleTypeAPIView.as_view(), name='vehicle-type'), 
  
    # --------- Orders --------- 
    path('order-request', OrderView.as_view(), name='order-request'),
    path('order-list', OrderListView.as_view(), name='order-list'),
    path('order-details', OrderDetailsView.as_view(), name='order-details'),
    path('user-order-status-change', UserOrderStatus.as_view(), name='user-order-status-change'),
    path('payment-order-request', UpdateOrderStatusView.as_view(), name='payment-order-request'),

    path('test-push-notification', PushNotification.as_view(), name='test-push-notification'),

    path('delivery-charges', DeliveryCharges.as_view(), name='delivery-charges'),
    path('driver-home-data', DriverOrderHomeView.as_view(), name='driver-home-data'),
    path('driver-location-status', DriverLocationStatus.as_view(), name='driver-location-status'),

    path('payment-response', MyfatoorahView.as_view(), name='payment-response'),

    path('privacy-policy',GetPrivacyPolicy.as_view(),name="privacy-policy"),
    path('pages',AllPage.as_view(),name="pages"),
    path('support',SupportData.as_view(),name="support"),

    path('forget-password',ForgotPassword.as_view(),name="forget-password"),
    path('reset-password',ResetPassword.as_view(),name="reset-password"),
    
    # ------ Wallet System -------
    path('withdraw-amount',WithdrawView.as_view(),name="withdraw-amount"),
    path('wallet-deposit',DepositView.as_view(),name="wallet-deposit"),
    path('transaction-history',TransactionHistoryAPIView.as_view(),name="transaction-history"),

    #------- For B2B Api ----------
    path('courier-company',GetCourierCompany.as_view(),name="courier-company"),
    path('driver-list',GetDriverView.as_view(),name="driver-list"),
    path('order-request-b2b',OrderPlacedB2B.as_view(),name="order-request-b2b"),
    path('order-list-b2b',OrderListB2B.as_view(),name="order-list-b2b"),
    path('order-details-b2b', OrderDetailsB2B.as_view(), name='order-details-b2b'),
    path('wallet-deposit-b2b',DepositView.as_view(),name="wallet-deposit-b2b"),
    path('initiate-payment',  InitiatePayment.as_view(), name='initiate-payment'),
    path('confirm-payment', ConfirmPayment.as_view(), name='confirm-payment'),

    path('create-b2b-business',  BusinessPartner.as_view(), name='create-b2b-business'),
    path('main-business-branch', MainBusinessAPIView.as_view(), name='main-business-branch'),
    path('b2b-business-list', BusinessListAPIView.as_view(), name='b2b-business-list'),

    # END

    path('track-order', TrackOrderAPIView.as_view(), name='track-order'), 
    path('update-driver-location', DriverLocation.as_view(), name='update-driver-location'), 
    
]