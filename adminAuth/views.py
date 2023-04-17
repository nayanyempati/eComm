from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth.models import User
from django.views.generic import View
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
import urllib.request
import urllib
import json
import requests
import urllib3
from eComm import settings
from .utils import TokenGenerator,generate_token
from django.utils.encoding import force_bytes,force_str,DjangoUnicodeDecodeError
from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives
from django.core.mail import send_mail
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import authenticate,login,logout
# Create your views here.

# Signup Page
def signup(request):
    if request.method=="POST":
        email=request.POST['email']
        password=request.POST['pass1']
        first_name=request.POST['firstname']
        last_name=request.POST['lastname']
        confirm_password=request.POST['pass2']
        if password!=confirm_password:
            messages.warning(request,"Password is Not Matching")
            return render(request,'signup.html') 
        recaptcha_response = request.POST.get('g-recaptcha-response')
        values = {'secret': settings.RECAPTCHA_PRIVATE_KEY,'response': recaptcha_response}
        resp = requests.post('https://www.google.com/recaptcha/api/siteverify', data=values)
        result_json = resp.json()
        if not result_json.get('success'):      
            messages.info(request,"Invalid Captcha")
            return render(request,'signup.html')             
        try:
            if User.objects.get(username=email):
                messages.info(request,"Email not available")
                return render(request,'signup.html')
        except Exception as identifier:
            pass
        user = User.objects.create_user(email, email,password,first_name=first_name,last_name=last_name,)
        user.is_active=True
        user.save()       
        message=render_to_string('activate.html',{})
        messages.success(request,f"User registration successfull. Please login")
        return redirect('/auth/login/')
    return render(request,"signup.html")

# User Login
def handlelogin(request):
    if request.method=="POST":
        print(list(request.POST.items()))
        username=request.POST['email']
        userpassword=request.POST['pass1'] 
        recaptcha_response = request.POST.get('g-recaptcha-response')
        values = {'secret': settings.RECAPTCHA_PRIVATE_KEY,'response': recaptcha_response}
        resp = requests.post('https://www.google.com/recaptcha/api/siteverify', data=values)
        result_json = resp.json()
        if result_json.get('success'): 
            myuser=authenticate(username=username,password=userpassword)
            if myuser is not None:
                login(request,myuser)
                messages.success(request,"Login Success")
                return redirect('/')
            else:
                messages.error(request,"Invalid Credentials")
                return redirect('/auth/login')

        else:
             messages.error(request,"Invalid Captcha")
             return redirect('/auth/login')
    return render(request,'login.html')  

# User Logout
def handlelogout(request):
    logout(request)
    messages.info(request,"Logout Success")
    return redirect('/auth/login')

