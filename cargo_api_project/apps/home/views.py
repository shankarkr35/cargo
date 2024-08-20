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
import json
from cargo_driver_app.models import Driver,VehicleType
from apps.api.models import *
from middlewares.auth import auth_middleware
from django.utils.text import slugify
from apps.contract_files.models import ContractFile
#load language translation
from django.utils.translation import gettext as _
from apps.banners.models import Banners
from apps.about_us.models import About_us
from apps.pages.models import Pages
import random
from django.core.mail import send_mail,EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

class Home:
    def index(request):
        banner = Banners.objects.filter(status=1).order_by('id')[:5]
        about = About_us.objects.get(id=1)
        records = {
            'about':about, 
            'banners':banner,
        }
        return render(request,"front/index.html",records)
    
    def courier_signup(request): 
        record = ContractFile.objects.get(id=1)
        data = {
            'list':record,
        }
        return render(request,"front/signup.html",data)
    
    
    def generate_unique_6_digit():
        while True:
            random_number = ''.join([str(random.randint(0, 9)) for _ in range(6)])  # Generate a random 6-digit number

            # Check if the generated number already exists in the database
            if not User.objects.filter(supplier_code=random_number).exists():
                return random_number  # Return the unique number
    def signup_process(request):
        try:
            if request.method == 'POST':
                fullname = request.POST.get('name')
                
                email = request.POST.get('email')
                phone = request.POST.get('phone')
                country_code = request.POST.get('country_code') 
                password = request.POST.get('password')
                supplier_code = request.POST.get('supplier_code')
                file = request.FILES.get('files')
                file1 = request.FILES.get('files1')
                file2 = request.FILES.get('files2')
                file3 = request.FILES.get('files3') 
                file4 = request.FILES.get('files4')
                file5 = request.FILES.get('files5')
                supplier_code = random.randint(100000, 999999)
                #supplier_code = random.randint(100000, 99999)
                
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
                    return JsonResponse({'status':False,'msg':'email already exist'})
                if User.objects.filter(phone = phone).exists():
                    return JsonResponse({'status':False,'msg':'phone already exist'})
                if User.objects.filter(supplier_code = supplier_code).exists():
                    return JsonResponse({'status':False,'msg':'supplier_code already exist'})
                else:
                    obj = User.objects.create_user(password=password,is_courier=1,country_code=country_code,fullname=fullname,email=email,phone=phone,is_active=False,courier_certificate=file,courier_file1=file1,courier_file2=file2,courier_file3=file3,contract_file=file4,owners_civil_id=file5,supplier_code=supplier_code)
                    obj.save()
                    user_id = obj.id
                    if user_id:
                        subject, from_email, to = 'Register', settings.DEFAULT_FROM_EMAIL, email
                        html_content = render_to_string('emails/registration_email.html', {'fullname': fullname})
                        text_content = strip_tags(html_content)
                        msg1 = EmailMultiAlternatives(subject, text_content, from_email, [to])
                        msg1.attach_alternative(html_content, "text/html")
                        msg1.send()
                        return JsonResponse({"status":True,'msg':"Signup done"})
                    else:
                        return JsonResponse({"status":True,'msg':"Signup not done"})
            else:
                return JsonResponse({"status":True,'msg':"Something Went Wrong!"})
        except Exception as e:
            return JsonResponse({"status":False,'msg':str(e)})
        


    def payment_success(request):
        return render(request,"front/success.html")
    
    def payment_failled(request):
        return render(request,"front/failed.html")
    
    def privacy_policy(request):
        record = Pages.objects.get(id=1)
        data = {
            'list':record,
        }
        return render(request,"front/common_page.html",data)
    
    def term_condition(request):
        record = Pages.objects.get(id=2)
        data = {
            'list':record, 
        }
        return render(request,"front/common_page.html",data)
    
    def privacyPolicy(request):
        record = Pages.objects.get(id=1)
        data = {
            'list':record,
        }
        return render(request,"front/pages.html",data)
    
    def termCondition(request):
        record = Pages.objects.get(id=2)
        data = {
            'list':record,
        }
        return render(request,"front/pages.html",data)

