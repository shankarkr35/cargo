from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
#from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
User = get_user_model()
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from apps.profiles.models import Profiles
from cargo_user_app.models import *
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
#from .models import *
from django.db.models import Sum
from apps.api.models import *


from cargo_driver_app.models import Driver
import json
 
class AuthCourierCheck:
    def index(request):
        if request.user.is_authenticated and request.user.is_courier:
            return redirect("/courier-dashboard/")
        else:
            return render(request,"courier/courier-login.html")
    def login_check(request):
        if request.method == 'POST':
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')

            user = authenticate(request, username=username, password=password, backend='apps.authentication.backends.courier_backend.CourierBackend')
            if user is not None:
                if user.is_active and user.is_courier:
                    login(request, user, backend='apps.authentication.backends.courier_backend.CourierBackend')
                    request.session['_auth_courier_user_id'] = user.pk
                    request.session['_auth_courier_backend'] = user.backend
                    print(f"Session keys after login: {request.session['_auth_courier_user_id']}")
                    print(f"Session keys after login: {list(request.session.keys())}")
                    return JsonResponse({'success': True, 'msg': 'logginSCS', 'redirect_url': '/courier-dashboard/'})
                return JsonResponse({'success': False, 'msg': 'NotCourier'})
            return JsonResponse({'success': False, 'msg': 'account404'})
        return JsonResponse({'success': False, 'msg': 'Swrong'})
    def signout(request):
        if request.user.is_authenticated and request.user.is_courier:
            logout(request)
            request.session.pop('_auth_courier_user_id', None)
            request.session.pop('_auth_courier_backend', None)
        return redirect('/courier-login/')
    # def login_check(request):
    #     if request.method == 'POST':
    #         data = json.loads(request.body)
    #         email = data.get('username')
    #         password = data.get('password')
    #         user = authenticate(email=email,password=password)
            
    #         if user is not None:
    #             if(user.is_active == 1):
    #                 if(user.is_courier):
    #                     login(request, user)
    #                     return JsonResponse({'success': True,'msg':'logginSCS'})
    #                 else:
    #                     return JsonResponse({'success': False,'msg':'NotCourier'})
    #             else:
    #                 return JsonResponse({'success': False,'msg':'ACC0'})
    #         else:
    #             return JsonResponse({'success': False, 'msg': 'account404'})
    #     else:
    #         return JsonResponse({'success': False, 'msg': 'Swrong'})
        
    # def signout(request):
    #     if request.user.is_authenticated and request.user.is_courier:
    #         logout(request)
    #         return redirect('/courier-login/')
    #     else: 
    #         return redirect('/courier-dashboard/')

    def courier_dashboard(request):
        courier_id = request.user.id
        if request.user.is_authenticated and request.user.is_courier:
            order_count = DriverOrders.objects.filter( Q(company_id=courier_id)).count()
            driver_count = Driver.objects.filter( Q(user_id=courier_id)).count()
            user_count = User.objects.filter( Q(is_admin=False) & Q(is_courier=False)).count()

            # Calculate the total delivery amount using the Sum aggregation function
            total_delivery_amount = DriverOrders.objects.filter(company_id=courier_id).aggregate(Sum('delivery_price'))['delivery_price__sum'] or 0
            #total_delivery_amount = DriverOrders.objects.aggregate(Sum('delivery_price'))['delivery_price__sum'] or 0
            records = {
                'orders': order_count,
                'drivers': driver_count,
                'users': user_count,
                'total_delivery_amount': total_delivery_amount,
            }
            return render(request,"courier/dashboard.html",{'records': records})
        else:
            return redirect("/courier-login/")
        














        