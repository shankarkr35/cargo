from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import DriverSerializer
from django.contrib.auth import get_user_model
User = get_user_model()
#from cargo_driver_app.serializers import *
from rest_framework.parsers import MultiPartParser
from .models import * 
from django.http import HttpResponse,JsonResponse
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required 
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from cargo_driver_app.models import Driver
from apps.api.models import *
from apps.company_delivery_charge.models import CompanyDeliveryCharge
from middlewares.auth import auth_courier_middleware
import json
import random
from django.core.mail import send_mail,EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.hashers import make_password

class DriverSignUpView(APIView):
    #parser_classes = [MultiPartParser] 
    def post(self, request):
        serializer = DriverSerializer(data=request.data)
        if serializer.is_valid():
            driver = serializer.save()
            # Perform any additional actions or validations here
            return Response({'message': 'Driver created successfully'}, status=201)
        return Response(serializer.errors, status=400)
    
class Drivers:
    @auth_courier_middleware
    def index(request):
        try:
            if request.user.is_authenticated and request.user.is_courier:
                courier_id = request.user.id
            data = Driver.objects.filter(user_id=courier_id).order_by('-id')
            records = {
                'list':data,  
            }
            return render(request,"courier/driver/index.html",records)
        except:
            return render(request,"courier/error.html")
        
        
    @auth_courier_middleware
    def add(request):
        return render(request,'courier/driver/add.html')

    @auth_courier_middleware
    def create(request):
        if request.method == 'POST':
            if request.user.is_authenticated and request.user.is_courier:
                courier_id = request.user.id
                supplier_code = request.user.supplier_code
            name = request.POST.get('name')
            email = request.POST.get('email')
            country_code = request.POST.get('country_code')
            phone = request.POST.get('phone')
            password = request.POST.get('password')
            #dob = request.POST.get('dob')
            address = request.POST.get('address')
            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')
            city = request.POST.get('city')
            file = request.FILES.get('files')
            civil_id = request.POST.get('civil_id')
    
            if file is not None:
                fss = FileSystemStorage()
                filename = fss.save(file.name, file)
                url = fss.url(filename)
            else:
                file = None
            
            if Driver.objects.filter(mobile_number = phone).exists():
                return JsonResponse({'status':False,'msg':'phone already exist'})

            # if Driver.objects.filter(email = email).exists():
            #     return JsonResponse({'status':False,'msg':'already exist'})
            else:
                obj = Driver(name=name,email=email,mobile_number=phone,password=password,address=address,latitude=latitude,longitude=longitude,city=city,driving_licence=file,user_id=courier_id,country_code=country_code,supplier_code=supplier_code,civil_id=civil_id)
                obj.save()
                return JsonResponse({'status': True,'msg':'Added'})
        else:
            return JsonResponse({'status': False,'msg':'Something Went Wrong'})
        
    @auth_courier_middleware   
    def edit(request,id):
        try:
            record = Driver.objects.get(id=id)
            data = {
                'list':record,
            }
            return render(request,'courier/driver/edit.html',data)
        except:
            return JsonResponse({'status': False,'msg':'Something Went Wrong'})

    @auth_courier_middleware   
    def update(request):
        try:
            if request.method == 'POST':
                if request.user.is_authenticated and request.user.is_courier:
                    courier_id = request.user.id
                    supplier_code = request.user.supplier_code

                name = request.POST.get('name')
                email = request.POST.get('email')
                country_code = request.POST.get('country_code')
                phone = request.POST.get('phone')
                password = request.POST.get('password')
                #dob = request.POST.get('dob')
                address = request.POST.get('address')
                latitude = request.POST.get('latitude')
                longitude = request.POST.get('longitude')
                city = request.POST.get('city')
                civil_id = request.POST.get('civil_id')
                files = request.FILES.get('files')
                id = request.POST.get('id')
                
                record = Driver.objects.get(id=id)
                
                if files is not None:
                    fss = FileSystemStorage()
                    filename = fss.save(files.name,files)
                    url = fss.url(filename)
                else:
                    files = record.driving_licence 
                
                if Driver.objects.filter(Q(mobile_number=phone) & ~Q(id=id)).exists():
                    return JsonResponse({'status':False,'msg':'phone already exist'})
            
                else:
                    updated = Driver.objects.filter(id=id).update(name=name,email=email,mobile_number=phone,password=password,address=address,latitude=latitude,longitude=longitude,city=city,driving_licence=files,country_code=country_code,supplier_code=supplier_code,civil_id=civil_id)
                    if updated:
                        return JsonResponse({'status': True,'msg':'Updated'})

        except Exception as e:
            return JsonResponse({'status': False,'msg':str(e)})
        
    @auth_courier_middleware
    def delete(request):
        try:
            if request.method == 'POST':
                id = request.POST.get('id')
                deleteRecord = Driver.objects.filter(id=id).delete()
                if deleteRecord is not None:
                    return JsonResponse({'status': True,'msg':'Deleted'})
                else:
                    return JsonResponse({'status': False,'msg':'Not Deleted'})
        except:
            return JsonResponse({'status': False,'msg':'Something Went Wrong'})

    @auth_courier_middleware
    def update_status(request):
        try:
            if request.method == 'POST':
                id = request.POST.get('id')
                status = request.POST.get('status')
                deleteRecord = Driver.objects.filter(id=id).update(status=status)
                if deleteRecord is not None:
                    return JsonResponse({'status': True,'msg':'Updated'})
                else:
                    return JsonResponse({'status': False,'msg':'Not Updated'})
        except:
            return JsonResponse({'status': False,'msg':'Something Went Wrong'})


class Vehicles():
    @auth_courier_middleware
    def index(request):
        try:
            if request.user.is_authenticated and request.user.is_courier:
                courier_id = request.user.id
            data = Vehicle.objects.select_related('vehicle_type','driver','color').filter(user_id=courier_id).order_by('-id')
            records = {
                'list':data,
            }
            return render(request,"courier/vehicles/index.html",records)
        except Exception as e:
            return JsonResponse({'status':False,'msg':str(e)})
        
        
    @auth_courier_middleware
    def add(request):
        if request.user.is_authenticated and request.user.is_courier:
            courier_id = request.user.id
        
        drivers = Driver.objects.filter(Q(user_id = courier_id) & Q(status = 1) )
        vehicle_type = VehicleType.objects.filter(status=1).order_by('-id')
        colors = Color.objects.filter(status=1).order_by('-id')
       
        records = {
            'drivers':drivers,
            'vehicle_types':vehicle_type,
            'colors':colors,
        }
        return render(request,'courier/vehicles/add.html',records)
    @auth_courier_middleware
    def create(request):
        if request.method == 'POST':
            if request.user.is_authenticated and request.user.is_courier:
                courier_id = request.user.id
                
            vehicle_type = request.POST.get('vehicle_type')
            driver = request.POST.get('driver')
            vehicle_number = request.POST.get('vehicle_number')
            color_id = request.POST.get('color_id')
            file = request.FILES.get('files')
    
            if file is not None:
                fss = FileSystemStorage()
                filename = fss.save(file.name, file)
                url = fss.url(filename)
            else:
                file = None

            if Vehicle.objects.filter(vehicle_number = vehicle_number).exists():
                return JsonResponse({'status':False,'msg':'already exist'})
            else:
                obj = Vehicle(vehicle_type_id=vehicle_type,vehicle_number=vehicle_number,color_id=color_id,image=file,user_id=courier_id,driver_id=driver)
                obj.save()
                return JsonResponse({'status': True,'msg':'Added'})
        else:
            return JsonResponse({'status': False,'msg':'Something Went Wrong'})
        
    @auth_courier_middleware   
    def edit(request,id):
        try:
            if request.user.is_authenticated and request.user.is_courier:
                courier_id = request.user.id
            drivers = Driver.objects.filter(Q(user_id = courier_id) & Q(status = 1))
            vehicle_type = VehicleType.objects.filter(status=1).order_by('-id')
            colors = Color.objects.filter(status=1).order_by('-id')

            record = Vehicle.objects.get(id=id)
            data = {
                'list':record,
                'drivers':drivers,
                'vehicle_types':vehicle_type,
                'colors':colors
            }
            return render(request,'courier/vehicles/edit.html',data)
        except Exception as e:
            return JsonResponse({'status': False,'msg':str(e)})

    @auth_courier_middleware   
    def update(request):
        try:
            if request.method == 'POST':
                if request.user.is_authenticated and request.user.is_courier:
                    courier_id = request.user.id

                vehicle_type = request.POST.get('vehicle_type')
                driver = request.POST.get('driver')
                vehicle_number = request.POST.get('vehicle_number')
                color_id = request.POST.get('color_id')
                files = request.FILES.get('files')
                id = request.POST.get('id')
                
                record = Vehicle.objects.get(id=id)
                
                if files is not None:
                    fss = FileSystemStorage()
                    filename = fss.save(files.name,files)
                    url = fss.url(filename)
                else:
                    files = record.image 
            
                if Vehicle.objects.filter(Q(vehicle_number=vehicle_number) & ~Q(id=id)).exists():
                    return JsonResponse({'status':False,'msg':'already exist'})
                else:
                    updated = Vehicle.objects.filter(id=id).update(vehicle_type_id=vehicle_type,vehicle_number=vehicle_number,color_id=color_id,image=files,user_id=courier_id,driver_id=driver)
                    if updated:
                        return JsonResponse({'status': True,'msg':'Updated'})

        except Exception as e:
            return JsonResponse({'status': False,'msg':str(e)})
        
    @auth_courier_middleware
    def delete(request):
        try:
            if request.method == 'POST':
                id = request.POST.get('id')
                deleteRecord = Vehicle.objects.filter(id=id).delete()
                if deleteRecord is not None:
                    return JsonResponse({'status': True,'msg':'Deleted'})
                else:
                    return JsonResponse({'status': False,'msg':'Not Deleted'})
        except:
            return JsonResponse({'status': False,'msg':'Something Went Wrong'})

    @auth_courier_middleware
    def update_status(request):
        try:
            if request.method == 'POST':
                id = request.POST.get('id')
                status = request.POST.get('status')
                deleteRecord = Vehicle.objects.filter(id=id).update(status=status)
                if deleteRecord is not None:
                    return JsonResponse({'status': True,'msg':'Updated'})
                else:
                    return JsonResponse({'status': False,'msg':'Not Updated'})
        except:
            return JsonResponse({'status': False,'msg':'Something Went Wrong'})


class Order():
    @auth_courier_middleware
    def index(request):
        try:
            courier_id = ""
            if request.user.is_authenticated and request.user.is_courier:
                courier_id = request.user.id
            orders = DriverOrders.objects.filter(Q(company_id=courier_id)).select_related('driver').prefetch_related('package', 'vehicle_type','pickup').order_by('-id')
            records = []
            for order in orders:
                driver = order.driver
                if driver:
                    company_name = driver.user.fullname if driver.user else None
                else:
                    company_name = None
 
                record = {
                    'order': order,
                    'company_name': company_name,
                    # Add other related data here if needed
                }
                records.append(record)
            records = {
                'list':records,
            }
            return render(request,"courier/orders/index.html",records)
        except Exception as e:
            return JsonResponse({'status':False,'msg':str(e)})   
    @auth_courier_middleware
    def delete(request):
        try:
            if request.method == 'POST':
                id = request.POST.get('id')
                deleteRecord = Orders.objects.filter(id=id).delete()
                if deleteRecord is not None:
                    return JsonResponse({'status': True,'msg':'Deleted'})
                else:
                    return JsonResponse({'status': False,'msg':'Not Deleted'})
        except:
            return JsonResponse({'status': False,'msg':'Something Went Wrong'})

    @auth_courier_middleware
    def update_status(request):
        try:
            if request.method == 'POST':
                id = request.POST.get('id')
                status = request.POST.get('status')
                deleteRecord = Orders.objects.filter(id=id).update(status=status)
                if deleteRecord is not None:
                    return JsonResponse({'status': True,'msg':'Updated'})
                else:
                    return JsonResponse({'status': False,'msg':'Not Updated'})
        except:
            return JsonResponse({'status': False,'msg':'Something Went Wrong'})
        


# ---------  Driver Orders -----------
class DriverOrder():
    @auth_courier_middleware
    def index(request,id):
        try:
            if request.user.is_authenticated and request.user.is_courier:
                courier_id = request.user.id
            driver_id = id
            orders = DriverOrders.objects.filter(Q(driver=driver_id) & ~Q(status=3)).select_related('driver').prefetch_related('package', 'vehicle_type','pickup').order_by('-id')
            records = []
            for order in orders:
                driver = order.driver
                if driver:
                    company_name = driver.user.fullname if driver.user else None
                else:
                    company_name = None
 
                record = {
                    'order': order,
                    'company_name': company_name,
                }
                records.append(record)
            records = {
                'list':records,
            }
            return render(request,"courier/driver_orders/index.html",records)
        except Exception as e:
            return JsonResponse({'status':False,'msg':str(e)})
        

# ====================  Comapny Delivery Charge manage=============
 
class Delivery():
    @auth_courier_middleware 
    def index(request):
        try:
            if request.user.is_authenticated and request.user.is_courier:
                courier_id = request.user.id
            data = CompanyDeliveryCharge.objects.filter(user_id=courier_id).order_by('id')
            records = {
                'list':data,
            }
            return render(request,"courier/delivery_charge/index.html",records)
        except Exception as e:
            return JsonResponse({'status':False,'msg':str(e)})
        
        
    @auth_courier_middleware   
    def add(request):
        if request.user.is_authenticated and request.user.is_courier:
            courier_id = request.user.id 
            return render(request,'courier/delivery_charge/add.html')
        
    @auth_courier_middleware 
    def create(request):
        if request.method == 'POST':
            if request.user.is_authenticated and request.user.is_courier:
                courier_id = request.user.id
                
            start_distance = int(request.POST.get('start_distance'))
            end_distance = int(request.POST.get('end_distance'))
            delivery_charge = request.POST.get('delivery_charge')
            
            if CompanyDeliveryCharge.objects.filter(Q(user_id = courier_id) & Q(start_distance__lt=end_distance,end_distance__gt=start_distance)).exists():
                return JsonResponse({'status':False,'msg':'already exist'})
            else:
                obj = CompanyDeliveryCharge(user_id=courier_id,start_distance=start_distance,end_distance=end_distance,delivery_charge=delivery_charge)
                obj.save()
                return JsonResponse({'status': True,'msg':'Added'})
        else:
            return JsonResponse({'status': False,'msg':'Something Went Wrong'})
        
    @auth_courier_middleware 
    def edit(request,id):
        try:
            if request.user.is_authenticated and request.user.is_courier:
                courier_id = request.user.id
            record = CompanyDeliveryCharge.objects.get(id=id)
            data = {
                'list':record,
            }
            return render(request,'courier/delivery_charge/edit.html',data)
        except Exception as e:
            return JsonResponse({'status': False,'msg':str(e)})
    @auth_courier_middleware    
    def update(request):
        try:
            if request.method == 'POST':
                if request.user.is_authenticated and request.user.is_courier:
                    courier_id = request.user.id

                start_distance = int(request.POST.get('start_distance'))
                end_distance = int(request.POST.get('end_distance'))
                delivery_charge = request.POST.get('delivery_charge')
                id = request.POST.get('id')
                
                if CompanyDeliveryCharge.objects.filter(~Q(user_id = courier_id) & Q(start_distance__lt=end_distance,end_distance__gt=start_distance)).exists():
                    return JsonResponse({'status':False,'msg':'already exist'})
                else:
                    updated = CompanyDeliveryCharge.objects.filter(id=id).update(start_distance=start_distance,end_distance=end_distance,delivery_charge=delivery_charge)
                    if updated:
                        return JsonResponse({'status': True,'msg':'Updated'})

        except Exception as e:
            return JsonResponse({'status': False,'msg':str(e)})
        
    @auth_courier_middleware 
    def delete(request):
        try:
            if request.method == 'POST':
                id = request.POST.get('id')
                deleteRecord = CompanyDeliveryCharge.objects.filter(id=id).delete()
                if deleteRecord is not None:
                    return JsonResponse({'status': True,'msg':'Deleted'})
                else:
                    return JsonResponse({'status': False,'msg':'Not Deleted'})
        except:
            return JsonResponse({'status': False,'msg':'Something Went Wrong'})

    @auth_courier_middleware 
    def update_status(request):
        try:
            if request.method == 'POST':
                id = request.POST.get('id')
                status = request.POST.get('status')
                deleteRecord = CompanyDeliveryCharge.objects.filter(id=id).update(status=status)
                if deleteRecord is not None:
                    return JsonResponse({'status': True,'msg':'Updated'})
                else:
                    return JsonResponse({'status': False,'msg':'Not Updated'})
        except:
            return JsonResponse({'status': False,'msg':'Something Went Wrong'})


# ------- Reset Password Functionality---
class ResetPassword():
    def index(request):
        try:
            return render(request,"courier/forgot-password.html")
        except Exception as e:
            return JsonResponse({'status':False,'msg':str(e)})
        
    def courier_email_check(request):
        if request.method == 'POST':
            data = json.loads(request.body)
            email = data.get('username')
            
            user = User.objects.filter(email=email).first()
            if user is not None:
                if user.is_courier:
                    otp = random.randint(1000, 9999)
                    subject, from_email, to = 'Forget Password OTP', settings.DEFAULT_FROM_EMAIL, email
                    html_content = render_to_string('emails/forgot_password_email.html', {'fullname': user.fullname,'otp':otp})
                    text_content = strip_tags(html_content)
                    msg1 = EmailMultiAlternatives(subject, text_content, from_email, [to])
                    msg1.attach_alternative(html_content, "text/html")
                    msg1.send()
                    # Update the OTP and expiration time
                    user.otp = otp
                    user.expire_otp = timezone.now() + timedelta(minutes=5)
                    user.save(update_fields=['otp', 'expire_otp'])
                    #User.objects.filter(id=user.id).update(otp=otp)
                    return JsonResponse({'success': True, 'msg': 'checkSCS'})
                return JsonResponse({'success': False, 'msg': 'NotCourier'})
            return JsonResponse({'success': False, 'msg': 'account404'})
        return JsonResponse({'success': False, 'msg': 'Swrong'})

    def resetPass(request):
        try:
            return render(request,"courier/reset-password.html")
        except Exception as e:
            return JsonResponse({'status':False,'msg':str(e)})
        
    def verify_otp_and_reset_password(request):
        if request.method == 'POST':
            data = json.loads(request.body)
            email = data.get('username')
            otp = data.get('otp')
            new_password = data.get('password')

            user = User.objects.filter(email=email, otp=otp).first()
            if user is not None:
                if timezone.now() <= user.expire_otp:
                    # OTP is valid and not expired
                    user.password = make_password(new_password)
                    user.otp = None  # Clear the OTP after successful reset
                    user.expire_otp = None  # Clear the expiration time
                    user.save(update_fields=['password', 'otp', 'expire_otp'])
                    return JsonResponse({'success': True, 'msg': 'Password reset successful'})
                else:
                    return JsonResponse({'success': False, 'msg': 'OTP has expired'})
            else:
                return JsonResponse({'success': False, 'msg': 'Invalid OTP or email'})
        return JsonResponse({'success': False, 'msg': 'Invalid request method'})