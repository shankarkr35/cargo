from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
import json
 
from cargo_user_app.models import *
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from cargo_driver_app.models import Driver,VehicleType,Vehicle
from apps.api.models import *
from apps.contract_files.models import *
from apps.delivery_charge.models import DeliveryCharge
from middlewares.auth import auth_middleware 
from django.utils.text import slugify
from apps.color.models import *
from apps.banners.models import Banners
from apps.about_us.models import About_us
from apps.pages.models import Pages
from apps.support.models import Support
from apps.wallet.models import Wallet,Transaction
from django.db.models import Sum
import random
from collections import defaultdict
from django.core.mail import send_mail,EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

class AuthAdminCheck:
    def index(request):
        if request.user.is_authenticated and request.user.is_admin:
            return redirect("/auth/admin-dashboard")
        else:
            return render(request,"backend/admin-login.html")
        
    # Check if session is saved correctly after login
    def login_check(request):
        if request.method == 'POST':
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')

            user = authenticate(request, username=username, password=password, backend='apps.authentication.backends.admin_backend.AdminBackend')
            if user is not None:
                if user.is_active and user.is_admin:
                    login(request, user, backend='apps.authentication.backends.admin_backend.AdminBackend')
                    request.session['_auth_admin_user_id'] = user.pk
                    request.session['_auth_admin_backend'] = 'apps.authentication.backends.admin_backend.AdminBackend'
                    request.session.save()  # Ensure session is saved
                    print(f"Session keys after login: {request.session['_auth_admin_user_id']}")
                    print(f"Session keys after login: {list(request.session.keys())}")
                    return JsonResponse({'success': True, 'msg': 'logginSCS', 'redirect_url': '/auth/admin-dashboard/'})
                return JsonResponse({'success': False, 'msg': 'NotAdmin'})
            return JsonResponse({'success': False, 'msg': 'account404'})
        return JsonResponse({'success': False, 'msg': 'Swrong'})



    
    def signout(request):
        if request.user.is_authenticated and request.user.is_admin:
            logout(request)
            request.session.pop('_auth_admin_user_id', None)
            request.session.pop('_auth_admin_backend', None)
        return redirect('/auth/admin-login')

    # def login_check(request):
    #     if request.method == 'POST': 
    #         data = json.loads(request.body) 
    #         username = data.get('username')
    #         password = data.get('password')
                
    #         user = authenticate(username=username,password=password)
    #         if user is not None:
    #             if(user.is_active == 1):
    #                 if(user.is_admin == 1):
    #                     login(request, user)
    #                     return JsonResponse({'success': True,'msg':'logginSCS'})
    #                 else:
    #                     return JsonResponse({'success': False,'msg':'NotAdmin'})
    #             else:
    #                 return JsonResponse({'success': False,'msg':'ACC0'})
    #         else:
    #             return JsonResponse({'success': False, 'msg': 'account404'})
    #     else:
    #         return JsonResponse({'success': False, 'msg': 'Swrong'})
        
    # def signout(request):
    #     if request.user.is_authenticated and request.user.is_admin:
    #         logout(request)
    #         return redirect('/auth/admin-login')
    #     else: 
    #         return redirect('/auth/admin-login') 
    
    def admin_dashboard(request):
        print(f"Session keys at dashboard view entry: {list(request.session.keys())}")
        if request.user.is_authenticated and request.user.is_admin:
            order_count = Orders.objects.count()
            driver_count = Driver.objects.count()
            user_count = User.objects.filter( Q(is_admin=False) & Q(is_courier=False)).count()
            print(f"Session keys after login dashboard: {request.session.get('_auth_admin_user_id', 'Key not found')}")
            # Calculate the total delivery amount using the Sum aggregation function
            total_delivery_amount = Orders.objects.filter(status=5).aggregate(Sum('delivery_price'))['delivery_price__sum'] or 0
            records = {
                'orders': order_count,
                'drivers': driver_count,
                'users': user_count,
                'total_delivery_amount': total_delivery_amount,
            }
            return render(request,"backend/dashboard.html", {'records': records})
        else:
            return redirect("/auth/admin-login")
        
    
class Drivers:
    @auth_middleware 
    def index(request):
        try:
            if request.user.is_authenticated and request.user.is_admin:
                admin_id = request.user.id
                supplier_code = request.user.supplier_code
            data = Driver.objects.select_related('user').order_by('-id')
            #data = Driver.objects.all().order_by('-id')
            records = {
                'list':data,
            }
            return render(request,"backend/driver/index.html",records)
        except Exception as e:
            return JsonResponse({"status":False,"msg":str(e)})
        
        
    @auth_middleware
    def add(request):
        return render(request,'backend/driver/add.html')
    
    @auth_middleware
    def create(request):
        if request.method == 'POST': 
            if request.user.is_authenticated and request.user.is_admin:
                admin_id = request.user.id
                supplier_code = request.user.supplier_code

            name = request.POST.get('name')
            name_ar = request.POST.get('name_ar')
            email = request.POST.get('email')
            country_code = request.POST.get('country_code')
            phone = request.POST.get('phone')
            password = request.POST.get('password')
            #dob = request.POST.get('dob')
            address = request.POST.get('address')
            address_ar = request.POST.get('address_ar')
            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')
            city = request.POST.get('city')
            city_ar = request.POST.get('city_ar')
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
                obj = Driver(name=name,email=email,mobile_number=phone,password=password,address=address,latitude=latitude,longitude=longitude,city=city,driving_licence=file,user_id=admin_id,country_code=country_code,name_ar=name_ar,address_ar=address_ar,city_ar=city_ar,supplier_code=supplier_code,civil_id=civil_id)
                obj.save()
                return JsonResponse({'status': True,'msg':'Added'})
        else:
            return JsonResponse({'status': False,'msg':'Something Went Wrong'})
        
    @auth_middleware  
    def edit(request,id):
        try:
            record = Driver.objects.get(id=id)
            data = {
                'list':record,
            }
            return render(request,'backend/driver/edit.html',data)
        except Exception as e:
            return JsonResponse({'status': False,'msg':str(e)})

    @auth_middleware  
    def update(request):
        try:
            if request.method == 'POST':
                if request.user.is_authenticated and request.user.is_admin:
                    admin_id = request.user.id
                    supplier_code = request.user.supplier_code

                name = request.POST.get('name')
                name_ar = request.POST.get('name_ar')
                email = request.POST.get('email')
                country_code = request.POST.get('country_code')
                phone = request.POST.get('phone')
                password = request.POST.get('password')
                #dob = request.POST.get('dob')
                address = request.POST.get('address')
                address_ar = request.POST.get('address_ar')
                latitude = request.POST.get('latitude')
                longitude = request.POST.get('longitude')
                city = request.POST.get('city')
                city_ar = request.POST.get('city_ar')
                files = request.FILES.get('files')
                id = request.POST.get('id')
                civil_id = request.POST.get('civil_id')
                
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
                    updated = Driver.objects.filter(id=id).update(name=name,email=email,mobile_number=phone,password=password,address=address,latitude=latitude,longitude=longitude,city=city,driving_licence=files,country_code=country_code,address_ar=address_ar,city_ar=city_ar,name_ar=name_ar,supplier_code=supplier_code,civil_id=civil_id)
                    if updated:
                        return JsonResponse({'status': True,'msg':'Updated'})

        except Exception as e:
            return JsonResponse({'status': False,'msg':str(e)})
        
    
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

class VehicleTypes:
    @auth_middleware
    def index(request):
        try:
            if request.user.is_authenticated and request.user.is_admin:
                admin_id = request.user.id
            data = VehicleType.objects.all().order_by('-id')
            records = {
                'list':data,
            }
            return render(request,"backend/vehicle_types/index.html",records)
        except Exception as e:
            return JsonResponse({"status":False,"msg":str(e)})
        
        
    @auth_middleware
    def add(request):
        return render(request,'backend/vehicle_types/add.html')
    
    @auth_middleware
    def create(request):
        if request.method == 'POST':
            if request.user.is_authenticated and request.user.is_admin:
                admin_id = request.user.id

            title = request.POST.get('title')
            title_ar = request.POST.get('title_ar')
            file = request.FILES.get('files')
    
            if file is not None:
                fss = FileSystemStorage()
                filename = fss.save(file.name, file)
                url = fss.url(filename)
            else:
                file = None
            slug = slugify(title)
            if VehicleType.objects.filter(Q(slug = slug)).exists():
                return JsonResponse({'status':False,'msg':'already exist'})
            
            else:
                obj = VehicleType(title=title,title_ar=title_ar,image=file)
                obj.save()
                return JsonResponse({'status': True,'msg':'Added'})
        else:
            return JsonResponse({'status': False,'msg':'Something Went Wrong'})
        
   
    def edit(request,id):
        try:
            record = VehicleType.objects.get(id=id)
            data = {
                'list':record,
            }
            return render(request,'backend/vehicle_types/edit.html',data)
        except Exception as e:
            return JsonResponse({'status': False,'msg':str(e)})

    @auth_middleware  
    def update(request):
        try:
            if request.method == 'POST':
                title = request.POST.get('title')
                title_ar = request.POST.get('title_ar')
                files = request.FILES.get('files')
                id = request.POST.get('id')
                slug = slugify(title)

                record = VehicleType.objects.get(id=id)
                
                if files is not None:
                    fss = FileSystemStorage()
                    filename = fss.save(files.name,files)
                    url = fss.url(filename)
                else:
                    files = record.image 
                
                
                if VehicleType.objects.filter(Q(slug = slug) & ~Q(id=id)).exists():
                    return JsonResponse({'status':False,'msg':'already exist'})
                else:
                    updated = VehicleType.objects.filter(id=id).update(title=title,title_ar=title_ar,slug=slug,image=files)
                    if updated:
                        return JsonResponse({'status': True,'msg':'Updated'})

        except Exception as e:
            return JsonResponse({'status': False,'msg':str(e)})
        
    
    def delete(request):
        try:
            if request.method == 'POST':
                id = request.POST.get('id')
                deleteRecord = VehicleType.objects.filter(id=id).delete()
                if deleteRecord is not None:
                    return JsonResponse({'status': True,'msg':'Deleted'})
                else:
                    return JsonResponse({'status': False,'msg':'Not Deleted'})
        except:
            return JsonResponse({'status': False,'msg':'Something Went Wrong'})

    
    def update_status(request):
        try:
            if request.method == 'POST':
                id = request.POST.get('id')
                status = request.POST.get('status')
                deleteRecord = VehicleType.objects.filter(id=id).update(status=status)
                if deleteRecord is not None:
                    return JsonResponse({'status': True,'msg':'Updated'})
                else:
                    return JsonResponse({'status': False,'msg':'Not Updated'})
        except:
            return JsonResponse({'status': False,'msg':'Something Went Wrong'})

# ====================  Vehicles manage=============
 
class Vehicles():
    @auth_middleware 
    def index(request): 
        try:
            data = Vehicle.objects.select_related('vehicle_type','driver','color').order_by('-id')
            records = {
                'list':data,
            }
            return render(request,"backend/vehicles/index.html",records)
        except Exception as e:
            return JsonResponse({'status':False,'msg':str(e)})
        
        
    @auth_middleware  
    def add(request):
        if request.user.is_authenticated and request.user.is_admin:
            admin_id = request.user.id
        
        drivers = Driver.objects.filter(Q(user_id = admin_id) & Q(status = 1) )
        vehicle_type = VehicleType.objects.filter(status=1).order_by('-id')
        colors = Color.objects.filter(status=1).order_by('-id')
    
        records = {
            'drivers':drivers,
            'vehicle_types':vehicle_type,
            'colors':colors,
        }
        return render(request,'backend/vehicles/add.html',records)
    
    @auth_middleware  
    def create(request):
        if request.method == 'POST':
            if request.user.is_authenticated and request.user.is_admin:
                admin_id = request.user.id
                
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
                obj = Vehicle(vehicle_type_id=vehicle_type,vehicle_number=vehicle_number,color_id=color_id,image=file,user_id=admin_id,driver_id=driver)
                obj.save()
                return JsonResponse({'status': True,'msg':'Added'})
        else:
            return JsonResponse({'status': False,'msg':'Something Went Wrong'})
        
    @auth_middleware     
    def edit(request,id):
        try:
            if request.user.is_authenticated and request.user.is_admin:
                admin_id = request.user.id
        
            drivers = Driver.objects.filter(Q(user_id = admin_id) & Q(status = 1))
            vehicle_type = VehicleType.objects.filter(status=1).order_by('-id')
            colors = Color.objects.filter(status=1).order_by('-id')
            record = Vehicle.objects.get(id=id)
            data = {
                'list':record,
                'drivers':drivers,
                'vehicle_types':vehicle_type,
                'colors':colors,
            }
            return render(request,'backend/vehicles/edit.html',data)
        except Exception as e:
            return JsonResponse({'status': False,'msg':str(e)})

    @auth_middleware 
    def update(request):
        try:
            if request.method == 'POST':
                if request.user.is_authenticated and request.user.is_admin:
                    admin_id = request.user.id

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
                    updated = Vehicle.objects.filter(id=id).update(vehicle_type_id=vehicle_type,vehicle_number=vehicle_number,color_id=color_id,image=files,user_id=admin_id,driver_id=driver)
                    if updated:
                        return JsonResponse({'status': True,'msg':'Updated'})

        except Exception as e:
            return JsonResponse({'status': False,'msg':str(e)})
        
    
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
    @auth_middleware
    def index(request,id): 
        try:
            full_path = request.path
            # Split the path into segments
            path_segments = full_path.strip('/').split('/')
            # Get the last segment
            last_segment = path_segments[-1] if path_segments else ''
            user_data = User.objects.filter(Q(user_type='business'))
            orders = Orders.objects.select_related('driver').prefetch_related('package', 'vehicle_type', 'pickup', 'user').order_by('-id')
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
                 
            context = {
                'list': records,
                'businesses':user_data,
                'last_segment': int(last_segment),
            }
            return render(request, "backend/orders/index.html", context)
        except Exception as e:
            return JsonResponse({'status':False,'msg':str(e)}) 

    def load_order_items(request):
        try:
            if request.method == 'POST':
                user_id = request.POST.get('user_id')
                if user_id:
                    orders = Orders.objects.filter(Q(user=user_id)).select_related('driver').prefetch_related('package', 'vehicle_type', 'pickup', 'user').order_by('-id')
                else:
                    orders = Orders.objects.select_related('driver').prefetch_related('package', 'vehicle_type', 'pickup', 'user').order_by('-id')
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
                    
                context = {
                    'list': records,
                }
                records = render_to_string('backend/ajax/ajax_order_list.html',context)
            
                return JsonResponse({'status':True,'msg':'Success','items':records})
        except Exception as e:
            return JsonResponse({'status':False,'msg':str(e)})   

    @auth_middleware
    def order_details(request,id):
        try:
            #data = Orders.objects.select_related('driver','package','vehicle_type','user').order_by('-id')
            orders = Orders.objects.select_related('driver').prefetch_related('package', 'vehicle_type','pickup','user').get(id=id)
            records = {
                'data':orders,
            } 
            return render(request,"backend/orders/order_details.html",records)
        except Exception as e:
            return JsonResponse({'status':False,'msg':str(e)})   
         
    @auth_middleware
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

    @auth_middleware
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
            

# ====================  Package manage=============
 
class Package():
    @auth_middleware 
    def index(request):
        try:
            data = Cargo_package.objects.all().order_by('order')
            records = {
                'list':data,
            }
            return render(request,"backend/packages/index.html",records)
        except Exception as e:
            return JsonResponse({'status':False,'msg':str(e)})
        
        
    @auth_middleware  
    def add(request):
        if request.user.is_authenticated and request.user.is_admin:
            admin_id = request.user.id
            return render(request,'backend/packages/add.html')
    
    @auth_middleware  
    def create(request):
        if request.method == 'POST':
            if request.user.is_authenticated and request.user.is_admin:
                admin_id = request.user.id
                
            size = request.POST.get('size')
            size_ar = request.POST.get('size_ar')
            weight_range = request.POST.get('weight_range')
            order = request.POST.get('order')
            
            if Cargo_package.objects.filter(size = size).exists():
                return JsonResponse({'status':False,'msg':'already exist'})
            else:
                obj = Cargo_package(size=size,weight_range=weight_range,order=order,size_ar=size_ar)
                obj.save()
                return JsonResponse({'status': True,'msg':'Added'})
        else:
            return JsonResponse({'status': False,'msg':'Something Went Wrong'})
        
    @auth_middleware     
    def edit(request,id):
        try:
            if request.user.is_authenticated and request.user.is_admin:
                admin_id = request.user.id
            record = Cargo_package.objects.get(package_id=id)
            data = {
                'list':record,
            }
            return render(request,'backend/packages/edit.html',data)
        except Exception as e:
            return JsonResponse({'status': False,'msg':str(e)})
        
    def update(request):
        try:
            if request.method == 'POST':
                if request.user.is_authenticated and request.user.is_admin:
                    admin_id = request.user.id

                size = request.POST.get('size')
                size_ar = request.POST.get('size_ar')
                weight_range = request.POST.get('weight_range')
                order = request.POST.get('order')
                id = request.POST.get('id')
                
                if Cargo_package.objects.filter(Q(size=size) & ~Q(package_id=id)).exists():
                    return JsonResponse({'status':False,'msg':'already exist'})
                else:
                    updated = Cargo_package.objects.filter(package_id=id).update(size=size,weight_range=weight_range,order=order,size_ar=size_ar)
                    if updated:
                        return JsonResponse({'status': True,'msg':'Updated'})

        except Exception as e:
            return JsonResponse({'status': False,'msg':str(e)})
        
    
    def delete(request):
        try:
            if request.method == 'POST':
                id = request.POST.get('id')
                deleteRecord = Cargo_package.objects.filter(package_id=id).delete()
                if deleteRecord is not None:
                    return JsonResponse({'status': True,'msg':'Deleted'})
                else:
                    return JsonResponse({'status': False,'msg':'Not Deleted'})
        except:
            return JsonResponse({'status': False,'msg':'Something Went Wrong'})

    
    def update_status(request):
        try:
            if request.method == 'POST':
                id = request.POST.get('id')
                status = request.POST.get('status')
                deleteRecord = Cargo_package.objects.filter(package_id=id).update(status=status)
                if deleteRecord is not None:
                    return JsonResponse({'status': True,'msg':'Updated'})
                else:
                    return JsonResponse({'status': False,'msg':'Not Updated'})
        except:
            return JsonResponse({'status': False,'msg':'Something Went Wrong'})

class CourierCompany:
    @auth_middleware
    def index(request):
        try:
            if request.user.is_authenticated and request.user.is_admin:
                admin_id = request.user.id
            data = User.objects.filter(is_courier=1).order_by('-id')
            records = {
                'list':data,
            }
            return render(request,"backend/courier/index.html",records)
        except Exception as e:
            return JsonResponse({"status":False,"msg":str(e)})
        
        
    @auth_middleware
    def add(request): 
        return render(request,'backend/courier/add.html')
    
    @auth_middleware
    def create(request): 
        try:
            if request.method == 'POST':
                fullname = request.POST.get('name')
                email = request.POST.get('email')
                phone = request.POST.get('phone')
                country_code = request.POST.get('country_code')
                password = request.POST.get('password')
                file = request.FILES.get('files')
                file1 = request.FILES.get('files1')
                file2 = request.FILES.get('files2')
                file3 = request.FILES.get('files3') 
                file4 = request.FILES.get('files4')
                file5 = request.FILES.get('files5')
                
                supplier_code = random.randint(100000, 999999)
                if file is not None:
                    fss = FileSystemStorage()
                    filename = fss.save(file.name, file)
                    url = fss.url(filename)
                else:
                    file = None

                if file1 is not None:
                    fss1 = FileSystemStorage()
                    filename1 = fss1.save(file1.name, file1)
                    url1 = fss1.url(filename1)
                else:
                    file1 = None
                
                if file2 is not None:
                    fss2 = FileSystemStorage()
                    filename2 = fss2.save(file2.name, file2)
                    url2 = fss2.url(filename2)
                else:
                    file2 = None
                
                if file3 is not None:
                    fss3 = FileSystemStorage()
                    filename3 = fss3.save(file3.name, file3)
                    url3 = fss3.url(filename3)
                else:
                    file3 = None
                
                if file4 is not None:
                    fss4 = FileSystemStorage()
                    filename4 = fss4.save(file4.name, file4)
                    url4 = fss4.url(filename4)
                else:
                    file4 = None

                if file5 is not None:
                    fss5 = FileSystemStorage()
                    filename5 = fss5.save(file5.name, file5)
                    url5 = fss5.url(filename5)
                else:
                    file5 = None
 
                if User.objects.filter(Q(fullname=fullname) & Q(is_courier=1)).exists():
                    return JsonResponse({'status':False,'msg':'name already exist'})
                if User.objects.filter(email = email).exists():
                    return JsonResponse({'status':False,'msg':'already exist'})
                else:
                    obj = User.objects.create_user(password=password,is_courier=1,country_code=country_code,fullname=fullname,email=email,phone=phone,is_active=0,courier_certificate=file,courier_file1=file1,courier_file2=file2,courier_file3=file3,contract_file=file4,owners_civil_id=file5,supplier_code=supplier_code)
                    obj.save()
                    user_id = obj.id
                    if user_id:
                        return JsonResponse({"status":True,'msg':"Added"})
                    else:
                        return JsonResponse({"status":True,'msg':"Not Added"})
            else:
                return JsonResponse({"status":True,'msg':"Something Went Wrong!"})
        except Exception as e:
            return JsonResponse({"status":False,'msg':str(e)})
    
        
    @auth_middleware  
    def edit(request,id):
        try:
            record = User.objects.get(id=id)
            data = {
                'list':record,
            }
            return render(request,'backend/courier/edit.html',data)
        except Exception as e:
            return JsonResponse({'status': False,'msg':str(e)})

    @auth_middleware  
    def update(request):
        try:
            if request.method == 'POST':
                fullname = request.POST.get('name')
                email = request.POST.get('email')
                phone = request.POST.get('phone')
                country_code = request.POST.get('country_code')
                password = request.POST.get('password')
                
                id = request.POST.get('id')
                
                record = User.objects.get(id=id)
                file = request.FILES.get('files')
                file1 = request.FILES.get('files1')
                file2 = request.FILES.get('files2')
                file3 = request.FILES.get('files3') 
                file4 = request.FILES.get('files4')
                file5 = request.FILES.get('files5')
                
                supplier_code = random.randint(100000, 999999)
                if file is not None:
                    fss = FileSystemStorage()
                    filename = fss.save(file.name, file)
                    url = fss.url(filename)
                else:
                    file = record.courier_certificate
                    
                if file1 is not None:
                    fss1 = FileSystemStorage()
                    filename1 = fss1.save(file1.name, file1)
                    url1 = fss1.url(filename1)
                else:
                    file1 = record.courier_file1
                
                if file2 is not None:
                    fss2 = FileSystemStorage()
                    filename2 = fss2.save(file2.name, file2)
                    url2 = fss2.url(filename2)
                else:
                    file2 = record.courier_file2
                
                if file3 is not None:
                    fss3 = FileSystemStorage()
                    filename3 = fss3.save(file3.name, file3)
                    url3 = fss3.url(filename3)
                else:
                    file3 = record.courier_file3
                
                if file4 is not None:
                    fss4 = FileSystemStorage()
                    filename4 = fss4.save(file4.name, file4)
                    url4 = fss4.url(filename4)
                else:
                    file4 = record.contract_file

                if file5 is not None:
                    fss5 = FileSystemStorage()
                    filename5 = fss5.save(file5.name, file5)
                    url5 = fss5.url(filename5)
                else:
                    file5 = record.owners_civil_id

                if User.objects.filter(Q(fullname=fullname) & Q(is_courier=1) & ~Q(id=id)).exists():
                    return JsonResponse({'status':False,'msg':'name already exist'})
                if User.objects.filter(Q(email=email) & ~Q(id=id)).exists():
                    return JsonResponse({'status':False,'msg':'already exist'})
                else:
                    updated = User.objects.filter(id=id).update(password=password,is_courier=1,country_code=country_code,fullname=fullname,email=email,phone=phone,is_active=0,courier_certificate=file,courier_file1=file1,courier_file2=file2,courier_file3=file3,contract_file=file4,owners_civil_id=file5,supplier_code=supplier_code)
                    if updated:
                        return JsonResponse({'status': True,'msg':'Updated'})
                    else:
                        return JsonResponse({'status': True,'msg':'Not Updated'})

        except Exception as e:
            return JsonResponse({'status': False,'msg':str(e)})
        
    @auth_middleware  
    def view(request,id):
        try:
            record = User.objects.get(id=id)
            data = {
                'list':record,
            }
            return render(request,'backend/courier/view.html',data)
        except Exception as e:
            return JsonResponse({'status': False,'msg':str(e)})

    def delete(request):
        try:
            if request.method == 'POST':
                id = request.POST.get('id')
                deleteRecord = User.objects.filter(id=id).delete()
                if deleteRecord is not None:
                    return JsonResponse({'status': True,'msg':'Deleted'})
                else:
                    return JsonResponse({'status': False,'msg':'Not Deleted'})
        except:
            return JsonResponse({'status': False,'msg':'Something Went Wrong'})

    
    def update_status(request):
        try:
            if request.method == 'POST':
                id = request.POST.get('id')
                status = request.POST.get('status')
                updateRecord = User.objects.filter(id=id).update(is_active=status)
                if updateRecord is not None:
                    if int(status) == 1:
                        record = User.objects.get(id=id)
                        subject, from_email, to = 'Activation Account', settings.DEFAULT_FROM_EMAIL, record.email
                        html_content = render_to_string('emails/publish_email.html', {'fullname': record.fullname})
                        text_content = strip_tags(html_content)
                        msg1 = EmailMultiAlternatives(subject, text_content, from_email, [to])
                        msg1.attach_alternative(html_content, "text/html")
                        msg1.send()
                    
                    return JsonResponse({'status': True,'msg':'Updated'})
                else:
                    return JsonResponse({'status': False,'msg':'Not Updated'})
        except:
            return JsonResponse({'status': False,'msg':'Something Went Wrong'})
        

# ====================  user Manage =============
class Users():
    @auth_middleware 
    def index(request):
        try:
            data = User.objects.filter(Q(is_admin=False) & Q(is_courier=False)).prefetch_related('wallet').order_by('-id')
            
            records = { 
                'list':data, 
            }
            return render(request,"backend/users/index.html",records)
        except Exception as e:
            return JsonResponse({'status':False,'msg':str(e)})

class TransacionHistory:
    @auth_middleware 
    def index(request, id):
        try:
            wallet = Wallet.objects.get(user=id)
            transactions = Transaction.objects.filter(wallet=wallet)
           
            records = {
                'transactions': transactions,
                'wallet': wallet,
            }
        except Wallet.DoesNotExist:
            records = {
                'transactions': None,
                'wallet': None,
            }
        return render(request, "backend/users/transaction_history.html", records)
       
class Contract:
    @auth_middleware  
    def index(request):
        try:
            record = ContractFile.objects.get(id=1)
            data = {
                'list':record,
            }
            return render(request,'backend/contracts/index.html',data)
        except Exception as e:
            return JsonResponse({'status': False,'msg':str(e)})

    @auth_middleware  
    def update(request):
        try:
            if request.method == 'POST':
                files = request.FILES.get('files')
                id = request.POST.get('id')
                
                record = ContractFile.objects.get(id=id)
                
                if files is not None: 
                    fss = FileSystemStorage()
                    filename = fss.save(files.name,files)
                    url = fss.url(filename)
                else:
                    files = record.contract_file

                updated = ContractFile.objects.filter(id=id).update(contract_file=files)
                if updated:
                    return JsonResponse({'status': True,'msg':'Updated'})
                else:
                    return JsonResponse({'status': True,'msg':'Not Updated'})

        except Exception as e:
            return JsonResponse({'status': False,'msg':str(e)})
    
class DeliveryCharges:
    @auth_middleware  
    def index(request):
        try:
            record = DeliveryCharge.objects.get(id=1)
            data = {
                'list':record,
            }
            return render(request,'backend/delivery_charge/index.html',data)
        except Exception as e:
            return JsonResponse({'status': False,'msg':str(e)})

    @auth_middleware  
    def update(request):
        try:
            if request.method == 'POST':
                delivery_charge = request.POST.get('delivery_charge')
                id = request.POST.get('id')
                
                updated = DeliveryCharge.objects.filter(id=id).update(delivery_charge=delivery_charge)
                if updated:
                    return JsonResponse({'status': True,'msg':'Updated'})
                else:
                    return JsonResponse({'status': True,'msg':'Not Updated'})

        except Exception as e:
            return JsonResponse({'status': False,'msg':str(e)})

# ------------ COLOR MANAGE----------   
class Colors:
    @auth_middleware
    def index(request):
        try:
            if request.user.is_authenticated and request.user.is_admin:
                admin_id = request.user.id
            data = Color.objects.all().order_by('-id')
            records = {
                'list':data,
            }
            return render(request,"backend/color/index.html",records)
        except Exception as e:
            return JsonResponse({"status":False,"msg":str(e)})
        
        
    @auth_middleware
    def add(request):
        return render(request,'backend/color/add.html')
    
    @auth_middleware
    def create(request):
        if request.method == 'POST':
            if request.user.is_authenticated and request.user.is_admin:
                admin_id = request.user.id

            name = request.POST.get('name')
            name_ar = request.POST.get('name_ar')
            color_code = request.POST.get('color_code')
            
            slug = slugify(name)
            if Color.objects.filter(Q(slug = slug)).exists():
                return JsonResponse({'status':False,'msg':'already exist'})
            
            else:
                obj = Color(name=name,name_ar=name_ar,color_code=color_code)
                obj.save()
                return JsonResponse({'status': True,'msg':'Added'})
        else:
            return JsonResponse({'status': False,'msg':'Something Went Wrong'})
        
   
    def edit(request,id):
        try:
            record = Color.objects.get(id=id)
            data = {
                'list':record,
            }
            return render(request,'backend/color/edit.html',data)
        except Exception as e:
            return JsonResponse({'status': False,'msg':str(e)})

    @auth_middleware  
    def update(request):
        try:
            if request.method == 'POST':
                name = request.POST.get('name')
                name_ar = request.POST.get('name_ar')
                color_code = request.POST.get('color_code')
                id = request.POST.get('id')
                slug = slugify(name)
       
                if Color.objects.filter(Q(slug = slug) & ~Q(id=id)).exists():
                    return JsonResponse({'status':False,'msg':'already exist'})
                else:
                    updated = Color.objects.filter(id=id).update(name=name,name_ar=name_ar,color_code=color_code,slug=slug)
                    if updated:
                        return JsonResponse({'status': True,'msg':'Updated'})

        except Exception as e:
            return JsonResponse({'status': False,'msg':str(e)})
        
    
    def delete(request):
        try:
            if request.method == 'POST':
                id = request.POST.get('id')
                deleteRecord = Color.objects.filter(id=id).delete()
                if deleteRecord is not None:
                    return JsonResponse({'status': True,'msg':'Deleted'})
                else:
                    return JsonResponse({'status': False,'msg':'Not Deleted'})
        except:
            return JsonResponse({'status': False,'msg':'Something Went Wrong'})

    
    def update_status(request):
        try:
            if request.method == 'POST':
                id = request.POST.get('id')
                status = request.POST.get('status')
                deleteRecord = Color.objects.filter(id=id).update(status=status)
                if deleteRecord is not None:
                    return JsonResponse({'status': True,'msg':'Updated'})
                else:
                    return JsonResponse({'status': False,'msg':'Not Updated'})
        except:
            return JsonResponse({'status': False,'msg':'Something Went Wrong'})

# ====================  END Color manage=============   

class Banner:
    @auth_middleware
    def index(request):
        try:
            data = Banners.objects.all().order_by('-id')
            records = {
                'list':data,
            }
            return render(request,"backend/banners/index.html",records)
        except:
            return render(request,"backend/error.html")
        
        

    def add(request):
        return render(request,'backend/banners/add.html')

    def create(request):
        if request.method == 'POST':
            title = request.POST.get('title')
            title_ar = request.POST.get('title_ar')
            file = request.FILES.get('files')
           
            if file is not None:
                fss = FileSystemStorage()
                filename = fss.save(file.name, file)
                url = fss.url(filename)
            else:
                file = None

            if Banners.objects.filter(title = title).exists():
                return JsonResponse({'status':False,'msg':'already exist'})
            else:
                obj = Banners(title=title,title_ar=title_ar,image=file,status=1)
                obj.save()
                return JsonResponse({'status': True,'msg':'Added'})
        else:
            return JsonResponse({'status': False,'msg':'Something Went Wrong'})
        
        
    def edit(request,id):
        try:
            record = Banners.objects.get(id=id)
            data = {
                'list':record,
            }
            return render(request,'backend/banners/edit.html',data)
        except Exception as e:
            return JsonResponse({'status': False,'msg':str(e)})
        
    
    def update(request):
        try:
            if request.method == 'POST':
                title = request.POST.get('title')
                title_ar = request.POST.get('title_ar')
                id = request.POST.get('id')
                files = request.FILES.get('files')

                record = Banners.objects.get(id=id)
                
                if files is not None:
                    fss = FileSystemStorage()
                    filename = fss.save(files.name,files)
                    url = fss.url(filename)
                else:
                    files = record.image
                
                if Banners.objects.filter(Q(title=title) & ~Q(id=id)).exists():
                    return JsonResponse({'status':False,'msg':'already exist'})
                else:
                    updated = Banners.objects.filter(id=id).update(title=title,title_ar=title_ar,image=files)
                    if updated:
                        return JsonResponse({'status': True,'msg':'Updated'})

        except Exception as e:
            return JsonResponse({'status': False,'msg':str(e)})
        
    
    def delete(request):
        try:
            if request.method == 'POST':
                id = request.POST.get('id')
                deleteRecord = Banners.objects.filter(id=id).delete()
                if deleteRecord is not None:
                    return JsonResponse({'status': True,'msg':'Deleted'})
                else:
                    return JsonResponse({'status': False,'msg':'Not Deleted'})
        except:
            return JsonResponse({'status': False,'msg':'Something Went Wrong'})

    
    def update_status(request):
        try:
            if request.method == 'POST':
                id = request.POST.get('id')
                status = request.POST.get('status')
                deleteRecord = Banners.objects.filter(id=id).update(status=status)
                if deleteRecord is not None:
                    return JsonResponse({'status': True,'msg':'Updated'})
                else:
                    return JsonResponse({'status': False,'msg':'Not Updated'})
        except:
            return JsonResponse({'status': False,'msg':'Something Went Wrong'})


class AboutUs:  
        
    def edit(request):
        try:
            id = 1
            record = About_us.objects.get(id=id)
            data = {
                'list':record,
            }
            return render(request,'backend/about_us/edit.html',data)
        except Exception as e:
            return JsonResponse({'status': False,'msg':str(e)})
        
    
    def update(request):
        try:
            if request.method == 'POST':
                title = request.POST.get('title')
                title_ar = request.POST.get('title_ar')
                title1 = request.POST.get('title1')
                title1_ar = request.POST.get('title1_ar')
                description = request.POST.get('description')
                description_ar = request.POST.get('description_ar')

                experience_desc = request.POST.get('experience_desc')
                experience_desc_ar = request.POST.get('experience_desc_ar')
                experience_year = request.POST.get('experience_year')
                experience_title = request.POST.get('experience_title')
                experience_title_ar = request.POST.get('experience_title_ar')
                
                id = request.POST.get('id')
                files = request.FILES.get('files')

                record = About_us.objects.get(id=id)
                
                if files is not None:
                    fss = FileSystemStorage()
                    filename = fss.save(files.name,files)
                    url = fss.url(filename)
                else:
                    files = record.image
                
                if About_us.objects.filter(Q(title=title) & ~Q(id=id)).exists():
                    return JsonResponse({'status':False,'msg':'already exist'})
                else:
                    updated = About_us.objects.filter(id=id).update(title=title,title_ar=title_ar,title1=title1,title1_ar=title1_ar,description=description,description_ar=description_ar,experience_desc=experience_desc,experience_desc_ar=experience_desc_ar,experience_year=experience_year,experience_title=experience_title,experience_title_ar=experience_title_ar,image=files)
                    if updated:
                        return JsonResponse({'status': True,'msg':'Updated'})

        except Exception as e:
            return JsonResponse({'status': False,'msg':str(e)})
      

# ------------ Pages MANAGE----------   
class Page:
    @auth_middleware
    def index(request):
        try:
            if request.user.is_authenticated and request.user.is_admin:
                admin_id = request.user.id
            data = Pages.objects.all().order_by('-id')
            records = {
                'list':data,
            }
            return render(request,"backend/pages/index.html",records)
        except Exception as e:
            return JsonResponse({"status":False,"msg":str(e)})
        
        
    @auth_middleware
    def add(request):
        return render(request,'backend/pages/add.html')
    
    @auth_middleware
    def create(request):
        if request.method == 'POST':
            if request.user.is_authenticated and request.user.is_admin:
                admin_id = request.user.id

            name = request.POST.get('name')
            name_ar = request.POST.get('name_ar')
            description = request.POST.get('description')
            description_ar = request.POST.get('description_ar')
            
            slug = slugify(name)
            if Pages.objects.filter(Q(slug = slug)).exists():
                return JsonResponse({'status':False,'msg':'already exist'})
            
            else:
                obj = Pages(name=name,name_ar=name_ar,description=description,description_ar=description_ar)
                obj.save()
                return JsonResponse({'status': True,'msg':'Added'})
        else:
            return JsonResponse({'status': False,'msg':'Something Went Wrong'})
        
   
    def edit(request,id):
        try:
            record = Pages.objects.get(id=id)
            data = {
                'list':record,
            }
            return render(request,'backend/pages/edit.html',data)
        except Exception as e:
            return JsonResponse({'status': False,'msg':str(e)})

    @auth_middleware  
    def update(request):
        try:
            if request.method == 'POST':
                name = request.POST.get('name')
                name_ar = request.POST.get('name_ar')
                description = request.POST.get('description')
                description_ar = request.POST.get('description_ar')
                id = request.POST.get('id')
                slug = slugify(name)
       
                if Pages.objects.filter(Q(slug = slug) & ~Q(id=id)).exists():
                    return JsonResponse({'status':False,'msg':'already exist'})
                else:
                    updated = Pages.objects.filter(id=id).update(name=name,name_ar=name_ar,description=description,description_ar=description_ar,slug=slug)
                    if updated:
                        return JsonResponse({'status': True,'msg':'Updated'})

        except Exception as e:
            return JsonResponse({'status': False,'msg':str(e)})
        
    
    def delete(request):
        try:
            if request.method == 'POST':
                id = request.POST.get('id')
                deleteRecord = Pages.objects.filter(id=id).delete()
                if deleteRecord is not None:
                    return JsonResponse({'status': True,'msg':'Deleted'})
                else:
                    return JsonResponse({'status': False,'msg':'Not Deleted'})
        except:
            return JsonResponse({'status': False,'msg':'Something Went Wrong'})

    
    def update_status(request):
        try:
            if request.method == 'POST':
                id = request.POST.get('id')
                status = request.POST.get('status')
                deleteRecord = Pages.objects.filter(id=id).update(status=status)
                if deleteRecord is not None:
                    return JsonResponse({'status': True,'msg':'Updated'})
                else:
                    return JsonResponse({'status': False,'msg':'Not Updated'})
        except:
            return JsonResponse({'status': False,'msg':'Something Went Wrong'})


class SupportPage:   
    def edit(request):
        try:
            id = 1
            record = Support.objects.filter(id=id).first()  # Use filter() instead of get() to handle non-existing records
            data = {
                'list': record,
                'url': 'support-management',
            }
            return render(request, 'backend/support/edit.html', data)
        except Exception as e:
            return JsonResponse({'status': False, 'msg': str(e)})

    def update(request):
        try:
            if request.method == 'POST':
                email = request.POST.get('email')
                phone = request.POST.get('phone')
                address = request.POST.get('address')
                facebook_url = request.POST.get('facebook_url')
                youtube_url = request.POST.get('youtube_url')
                twitter_url = request.POST.get('twitter_url')
                whatsapp_url = request.POST.get('whatsapp_url')
                instagram_url = request.POST.get('instagram_url')
                
                #id = request.POST.get('id')
                id = 1
                
                if Support.objects.filter(Q(id = id)).exists():
                    updated = Support.objects.filter(id=id).update(email=email,phone=phone,address=address,facebook_url=facebook_url,youtube_url=youtube_url,twitter_url=twitter_url,whatsapp_url=whatsapp_url,instagram_url=instagram_url)
                    if updated:
                        return JsonResponse({'status': True,'msg':'Updated'})
                else:
                    obj = Support(email=email,phone=phone,address=address,facebook_url=facebook_url,youtube_url=youtube_url,twitter_url=twitter_url,whatsapp_url=whatsapp_url,instagram_url=instagram_url)
                    obj.save()
                    return JsonResponse({'status': True,'msg':'Updated'})  
                 

        except Exception as e:
            return JsonResponse({'status': False,'msg':str(e)})
      

class Business:
    @auth_middleware 
    def index(request):
        try:
            if request.user.is_authenticated and request.user.is_admin:
                admin_id = request.user.id
                supplier_code = request.user.supplier_code
            data = User.objects.filter(user_type='business').prefetch_related('wallet').order_by('-id')
            new_data = []
            # Populate new_data with values from User objects 
            for rec in data:
                wallet_balance = rec.wallet.balance if hasattr(rec, 'wallet') else 0  # Ensure wallet exists

                try:
                    restaurant_id = int(rec.branch)
                    try:
                        restaurant_data = User.objects.get(id=restaurant_id)
                        branch_name = restaurant_data.fullname
                    except User.DoesNotExist:
                        branch_name = ''
                except (ValueError, TypeError):
                    branch_name = '' 
               
                new_data.append({
                    'id': rec.id,
                    'fullname': rec.fullname,
                    'email': rec.email,
                    'phone': rec.phone,
                    'branch_name': branch_name,
                    'is_active': rec.is_active,
                    'wallet_balance': wallet_balance,
                })

            records = {
                'list':new_data,
            }
            return render(request,"backend/business/index.html",records)
        except Exception as e:
            return JsonResponse({"status":False,"msg":str(e)})
        
        
    @auth_middleware
    def add(request):
        main_business = User.objects.filter(Q(is_active=True) & Q(user_type='business') & Q(branch='')).order_by('-id')
        records = {
            'businesses':main_business
        }
        return render(request,'backend/business/add.html',records)
    
    @auth_middleware
    def create(request):
        if request.method == 'POST': 
            if request.user.is_authenticated and request.user.is_admin:
                admin_id = request.user.id
                supplier_code = request.user.supplier_code

            name = request.POST.get('name')
            email = request.POST.get('email')
            country_code = request.POST.get('country_code')
            phone = request.POST.get('phone')
            branch = request.POST.get('branch')
            address = request.POST.get('address')
            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')
           
            if User.objects.filter(phone = phone).exists():
                return JsonResponse({'status':False,'msg':'phone already exist'})
            if User.objects.filter(Q(fullname=name) & Q(user_type='business')).exists():
                    return JsonResponse({'status':False,'msg':'name already exist'})
            if User.objects.filter(email = email).exists():
                    return JsonResponse({'status':False,'msg':'email already exist'})
            else:
                obj = User(fullname=name,email=email,phone=phone,country_code=country_code,user_type='business',branch=branch,address=address,latitude=latitude,longitude=longitude)
                obj.save()
                
                user = User.objects.get(email=email)  # Assuming email is unique
                if user:
                    # Create Wallet object
                    Wallet.objects.create(user=user, balance=0)
                    return JsonResponse({'status': True, 'msg': 'Added', 'user': user.id})
                else:
                    return JsonResponse({'status': False, 'msg': 'Not Added'})
                
        else:
            return JsonResponse({'status': False,'msg':'Something Went Wrong'})
        
    @auth_middleware  
    def edit(request,id):
        try:
            record = User.objects.get(id=id)
            main_business = User.objects.filter(Q(is_active=1) & Q(user_type='business') & Q(branch='') & ~Q(id=id)).order_by('-id')
            data = {
                'list':record,
                'businesses':main_business
            }
            return render(request,'backend/business/edit.html',data)
        except Exception as e:
            return JsonResponse({'status': False,'msg':str(e)})

    @auth_middleware  
    def update(request):
        try:
            if request.method == 'POST':
                if request.user.is_authenticated and request.user.is_admin:
                    admin_id = request.user.id
                    supplier_code = request.user.supplier_code

                name = request.POST.get('name')
                email = request.POST.get('email')
                country_code = request.POST.get('country_code')
                phone = request.POST.get('phone')
                branch = request.POST.get('branch')
                address = request.POST.get('address')
                latitude = request.POST.get('latitude')
                longitude = request.POST.get('longitude')
                id = request.POST.get('id')
                
                record = User.objects.get(id=id)
                if User.objects.filter(Q(fullname=name) & Q(user_type='business') & ~Q(id=id)).exists():
                    return JsonResponse({'status':False,'msg':'name already exist'})
                if User.objects.filter(Q(email=email) & ~Q(id=id)).exists():
                    return JsonResponse({'status':False,'msg':'email already exist'})
                
                if User.objects.filter(Q(phone=phone) & ~Q(id=id)).exists():
                    return JsonResponse({'status':False,'msg':'phone already exist'})

                else:
                    updated = User.objects.filter(id=id).update(fullname=name,email=email,phone=phone,country_code=country_code,user_type='business',branch=branch,address=address,latitude=latitude,longitude=longitude)
                    if updated:
                        return JsonResponse({'status': True,'msg':'Updated'})

        except Exception as e:
            return JsonResponse({'status': False,'msg':str(e)})
        
    
    def delete(request):
        try:
            if request.method == 'POST':
                id = request.POST.get('id')
                deleteRecord = User.objects.filter(id=id).delete()
                if deleteRecord is not None:
                    return JsonResponse({'status': True,'msg':'Deleted'})
                else:
                    return JsonResponse({'status': False,'msg':'Not Deleted'})
        except:
            return JsonResponse({'status': False,'msg':'Something Went Wrong'})

    
    def update_status(request):
        try:
            if request.method == 'POST':
                id = request.POST.get('id')
                status = request.POST.get('status')
                
                deleteRecord = User.objects.filter(id=id).update(is_active=status)
                if deleteRecord is not None:
                    return JsonResponse({'status': True,'msg':'Updated'})
                else:
                    return JsonResponse({'status': False,'msg':'Not Updated'})
        except:
            return JsonResponse({'status': False,'msg':'Something Went Wrong'})







 