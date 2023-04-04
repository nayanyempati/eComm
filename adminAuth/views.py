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
from app import keys
from eComm import settings
from .utils import TokenGenerator,generate_token
from django.utils.encoding import force_bytes,force_str,DjangoUnicodeDecodeError
from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives
from django.core.mail import send_mail
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import authenticate,login,logout

# Create your views here.
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
        user.is_active=False
        user.save()
        subject = 'Activate Your Account'
        link=keys.DOMAIN+"/auth/activate/"+urlsafe_base64_encode(force_bytes(user.pk))+'/'+generate_token.make_token(user);
        message = f'Hi {first_name},<br><br> Thank you for registering in eComn.<br><br> Activate your account by clicking the below link<br><br>'+link+"<br><br>";
        email_from = keys.EMAIL_HOST_USER
        recipient_list = [user.email, ]
        msg = EmailMultiAlternatives(subject, message, email_from, recipient_list)
        msg.attach_alternative(message, "text/html")
        msg.send()
        message=render_to_string('activate.html',{})
        messages.success(request,f"Activate your account by clicking the link sent to your registered email address")
        return redirect('/auth/login/')
    return render(request,"signup.html")


class ActivateAccountView(View):
    def get(self,request,uidb64,token):
        try:
            uid=force_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(pk=uid)
        except Exception as identifier:
            user=None
        if user is not None and generate_token.check_token(user,token):
            user.is_active=True
            user.save()
            messages.info(request,"Account Activated Successfully")
            return redirect('/auth/login')
        return render(request,'activatefail.html')

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






def handlelogout(request):
    logout(request)
    messages.info(request,"Logout Success")
    return redirect('/auth/login')


class RequestResetEmailView(View):
    def get(self,request):
        return render(request,'request-reset-email.html')
    
    def post(self,request):
        email=request.POST['email']
        recaptcha_response = request.POST.get('g-recaptcha-response')
        values = {'secret': settings.RECAPTCHA_PRIVATE_KEY,'response': recaptcha_response}
        resp = requests.post('https://www.google.com/recaptcha/api/siteverify', data=values)
        result_json = resp.json()
        if result_json.get('success'): 
            user=User.objects.filter(email=email)
            if user.exists():
            # current_site=get_current_site(request)
                subject = 'Reset Your Password'
                link=keys.DOMAIN+"/auth/set-new-password/"+urlsafe_base64_encode(force_bytes(user[0].pk))+'/'+PasswordResetTokenGenerator().make_token(user[0]);
                message = f'Hi,<br><br> A request has been made to reset the password of Reporting Platform account associated with this email address. <br><br>'+link;
                email_from = keys.EMAIL_HOST_USER
                recipient_list = [email ]
                msg = EmailMultiAlternatives(subject, message, email_from, recipient_list)
                msg.attach_alternative(message, "text/html")
                msg.send()
                messages.info(request,f"We have sent you an email with instructions on how to reset the password" )
                return render(request,'request-reset-email.html')
        else:
             messages.info(request,f"Invalid Captcha" )
             return render(request,'request-reset-email.html')

class SetNewPasswordView(View):
    def get(self,request,uidb64,token):
        context = {
            'uidb64':uidb64,
            'token':token
        }
        try:
            user_id=force_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(pk=user_id)

            if  not PasswordResetTokenGenerator().check_token(user,token):
                messages.warning(request,"Password Reset Link is Invalid")
                return render(request,'request-reset-email.html')

        except DjangoUnicodeDecodeError as identifier:
            pass

        return render(request,'set-new-password.html',context)

    def post(self,request,uidb64,token):
        context={
            'uidb64':uidb64,
            'token':token
        }
        password=request.POST['pass1']
        confirm_password=request.POST['pass2']
        if password!=confirm_password:
            messages.warning(request,"Password is Not Matching")
            return render(request,'set-new-password.html',context)
        
        try:
            user_id=force_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(pk=user_id)
            user.set_password(password)
            user.save()
            messages.success(request,"Password Reset Success Please Login with New Password")
            return redirect('/auth/login/')

        except DjangoUnicodeDecodeError as identifier:
            messages.error(request,"Something Went Wrong")
            return render(request,'set-new-password.html',context)
        return render(request,'set-new-password.html',context)
