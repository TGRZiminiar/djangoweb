from django.http import HttpResponse
from django.shortcuts import redirect, render
from accounts.forms import RegistrationForm
from .models import Account,MyAccountManager
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required
# Create your views here.

#verifycation email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

def create_user(self, first_name, last_name, username, email, password=None):
        if not email:
            raise ValueError('User must have an email address')

        if not username:
            raise ValueError('User must have an username')

        user = self.model(
            email = self.normalize_email(email),
            username = username,
            first_name = first_name,
            last_name = last_name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

def register(request):

    if request.method == 'POST': # ถ้ามีการคลิกเข้ามา
        form = RegistrationForm(request.POST) # request.POST จะมีค่า fields value ทั้งหมด
        if form.is_valid(): # ถ้าค่าฟอมทั้งหมดที่รับมาถูกต้องตามที่ต้องการ
            #ใช้ django form ต้องเรียกcleander_dataมาเพื่อเรียกข้อมูลที่requestมา

            first_name   = form.cleaned_data['first_name'] 
            last_name    = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email        = form.cleaned_data['email']
            password     = form.cleaned_data['password']
            username     = email.split("@")[0]

            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)          
            #ในไฟล์model ไม่มีการใช้เบอร์ในการสมัครเลยต้องใส่เบอร์โทรเข้าไปทีหลัง
            user.phone_number = phone_number
            user.save()

            #User activation
            current_site = get_current_site(request) #เอาค่า domain มาเก็บไว้ในตัวแปล
            email_subject = 'Please activate yout account' # ข้อความหัวเรื่องที่จะส่งไปในเมล์
            message = render_to_string('accounts/account_verification_email.html',{ #ส่ง templates ที่ทำไว้ไปในหน้าemail
                'user'  :   user, #user object เพราะต้องใช้ชื่อของuser.first_name เลยต้องส่งเข้า user เข้ามา
                'domain':   current_site,
                'uid'   :   urlsafe_base64_encode(force_bytes(user.pk)), #encode userid จะได้ไม่มีใครเห็นค่า primary key 
                'token' :   default_token_generator.make_token(user) #เรียก library สร้าง token ของ user
            }) 
            to_email   = email #เอาคำที่จะส่งเก็บไว้ในตัวแร
            send_email = EmailMessage(email_subject, message, to=[to_email]) #เอาของที่จะส่งมาเก็บไว้ในตัวแปรทั้งหมด
            send_email.send() #ส่งอีเมล์
            
            #messages.success(request,'We have already send you a verification email to your email address. Please verify.') #ถ้าสำเร็จให้ขึ้นข้อความนี้
            return redirect('/accounts/login/?command=verification&email='+email) #ทุกอย่างเสร้จแล้วให้กลับไปหน้า register
            

    else:
        form = RegistrationForm()

    context = {
        'form':form,

    }
    return render(request,'accounts/register.html', context)

def login(request):
    if request.method == 'POST':
        email    = request.POST['email'] #เชื่อมไปถึงหน้า Login.html name ที่ชื่อ email
        password = request.POST['password']
        user     = auth.authenticate(email=email,password = password)

        if user is not None:
            auth.login(request,user)
            messages.success(request,'You are now in!')
            return redirect('dashboard')
        else:
            messages.error(request,'Invalid login.')
            return redirect('login')

    return render(request,'accounts/login.html')


@login_required(login_url = "login") #หมายความว่าจะlogout ได้ก็ต่อเมื่อ login เท่านั้น
def logout(request):
    auth.logout(request)
    messages.success(request,"You are logout.")
    return redirect('login')



def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode() #เพื่อdecodeจากตัว primarykey uid ของ message ไปเก็บไว้ในตัวแปร uid
        user = Account._default_manager.get(pk=uid) #จะได้ค่า user ที่เป็น object ออกมา
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user,token): #ถ้า user ไม่มี error และเช็คtokenของ user กับ token เพื่อจะได้รู้ว่ามันปลอดถัยไหม
        user.is_active = True
        user.save()
        messages.success(request,'Your Account is actiavted!')
        return redirect('login')

    else:
        messages.error(request,'Invalid activation link.')
        return redirect('register')

@login_required(login_url='login')
def dashboard(request):
    return render(request,'accounts/dashboard.html')


def forgotpassword(request):
    if request.method == 'POST':
        email = request.POST['email'] #มาจากการกดsubmit ของคน
        if Account.objects.filter(email=email).exists(): #ถ้าอีเมล์มีตัวจนอยู่
            user = Account.objects.get(email__exact = email) # emaii__exact เป็นการเชคว่าเมล์นี้มีอยู่ในdata base ไหม

            #Access passwpord email
            current_site = get_current_site(request) #เอาค่า domain มาเก็บไว้ในตัวแปล
            email_subject = 'Reset your password' # ข้อความหัวเรื่องที่จะส่งไปในเมล์
            message = render_to_string('accounts/reset_password_email.html',{ #ส่ง templates ที่ทำไว้ไปในหน้าemail
                'user'  :   user, #user object เพราะต้องใช้ชื่อของuser.first_name เลยต้องส่งเข้า user เข้ามา
                'domain':   current_site,
                'uid'   :   urlsafe_base64_encode(force_bytes(user.pk)), #encode userid จะได้ไม่มีใครเห็นค่า primary key 
                'token' :   default_token_generator.make_token(user) #เรียก library สร้าง token ของ user
            }) 
            to_email   = email #เอาคำที่จะส่งเก็บไว้ในตัวแร
            send_email = EmailMessage(email_subject, message, to=[to_email]) #เอาของที่จะส่งมาเก็บไว้ในตัวแปรทั้งหมด
            send_email.send() #ส่งอีเมล์
            messages.success(request,'Password reset email has been send to your email address.')
            return redirect('login')

        else:
            messages.error(request,'Account does not exsits!')
            return redirect('forgotpassword')
    return render(request,'accounts/forgotpassword.html')


def resetpassword_valid(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode() #เพื่อdecodeจากตัว primarykey uid ของ message ไปเก็บไว้ในตัวแปร uid
        user = Account._default_manager.get(pk=uid) #จะได้ค่า user ที่เป็น object ออกมา

    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user,token): #ถ้า user ไม่มี error และเช็คtokenของ user กับ token เพื่อจะได้รู้ว่ามันปลอดถัยไหม
        request.session['uid'] = uid #จะไดเข้าถึง session ได้หลังจาก reset password
        messages.success(request,'Please reset your password')
        return redirect('resetpassword')
    else:
        messages.error(request,'This link has been expired!')
        return redirect('login')



def resetpassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid') #วิธีการจะเอาค่าจาก session มาเก็บในตัวแปร
            user = Account.objects.get(pk=uid)
            user.set_password(password) #ต้องใช้method set_password เพื่อเปลี่ยนรหัส เป็นฟังก์์ชันของdjango พอsetแล้วมันจะ hash ให้
            user.save()
            messages.success(request,'Password reset successful!')
            return redirect('login')

        else:
            messages.error(request,'Password do not match!')
            return redirect('resetpassword')
    else:
        return render(request,'accounts/resetpassword.html')