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

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.mail import send_mail,EmailMultiAlternatives
from rest_framework import status
import random

class Home:
    def index(request):
        return render(request,"front/index.html")
    
    def courier_signup(request):
        record = ContractFile.objects.get(id=1)
        #print(len(record))
        data = {
            'list':record,
        }
        return render(request,"front/signup.html",data)
    
    def signup_process(request):
        try:
            if request.method == 'POST':
                fullname = request.POST.get('name')
                return JsonResponse({'status':False,'msg':'Hii Sir Goog111111111111'})
                email = request.POST.get('email')
                phone = request.POST.get('phone')
                country_code = request.POST.get('country_code') 
                password = request.POST.get('password')
                file = request.FILES.get('files')
                file1 = request.FILES.get('files1')
                file2 = request.FILES.get('files2')
                file3 = request.FILES.get('files3') 
                file4 = request.FILES.get('files4')
                
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
                    
                    
                if User.objects.filter(Q(fullname=fullname) & Q(is_courier=1)).exists():
                    return JsonResponse({'status':False,'msg':'name already exist'})
                if User.objects.filter(email = email).exists():
                    return JsonResponse({'status':False,'msg':'email already exist'})
                if User.objects.filter(phone = phone).exists():
                    return JsonResponse({'status':False,'msg':'phone already exist'})
                else:
                    obj = User.objects.create_user(password=password,is_courier=1,country_code=country_code,fullname=fullname,email=email,phone=phone,is_active=False,courier_certificate=file,courier_file1=file1,courier_file2=file2,courier_file3=file3,contract_file=file4)
                    obj.save()
                    user_id = obj.id
                    if user_id:
                        
                        return JsonResponse({"status":True,'msg':"Signup done"})
                    else:
                        return JsonResponse({"status":True,'msg':"Signup not done"})
            else:
                return JsonResponse({"status":True,'msg':"Something Went Wrong!"})
        except Exception as e:
            return JsonResponse({"status":False,'msg':str(e)})
    
