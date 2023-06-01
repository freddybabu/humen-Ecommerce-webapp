from django.shortcuts import get_object_or_404
import random
from django.contrib import messages, auth
from django.http import JsonResponse
from .import verify
from orders.models import Order
from django.contrib.auth import authenticate, login,logout
from django.shortcuts import render, redirect
from django.conf import settings
from .forms import RegistrationForm,UserForm,VerifyForm
from carts.models import Cart,CartItem
from .models import Account
from django.contrib.auth.decorators import login_required
from carts.views import _cart_id

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
import requests

from twilio.rest import Client



def register(request):
    form = RegistrationForm()
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]

            user = Account.objects.create_user(
                first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            user.phone_number = phone_number
            user.save()
            request.session['email']=email
            
            verify.send(phone_number)
            messages.success(request,"Registered Successfully! Verify OTP to continue")
            return redirect('ver')
    context = {
        'form':form
    }
    return render(request,'accounts/register.html',context)

            # return redirect('signin')
    # else:
    #     form = RegistrationForm()

    # context = {
    #     'form': form,
    # }
    # return render(request, 'accounts/register.html', context)

#########################################################################################################

def verify_code(request):
    if request.method == 'POST':
        form = VerifyForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            user = Account._default_manager.get(email=request.session.get('email'))
            if verify.check(user.phone_number, code):
                user.is_active = True
                user.is_verified = True
                user.save()
                return redirect('signin')
    else:
        form = VerifyForm()
    return render(request, 'accounts/verify.html', {'form':form})

##########################################################################################################

@login_required(login_url='signin')
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id,is_ordered=True)
    orders_count = orders.count()
    context = {
        'orders_count':orders_count
    }
    return render(request, 'accounts/dashboard.html',context)
 
#############################################################################################################   


def signin(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
         
        myuser = auth.authenticate(email=email, password=password)
        
        if myuser is not None:
            if myuser.is_superadmin:
                request.session['email'] = email
                return redirect('supuser')
            else:
                try:
                    cart = Cart.objects.get(cart_id=_cart_id(request))
                    is_cart_item_exists =  CartItem.objects.filter(cart=cart).exists()
                    if is_cart_item_exists:
                        cart_item = CartItem.objects.filter(cart=cart)
                        
                        # getting the product variation by cart id
                        product_variation = []
                        for item in cart_item:
                            variation = item.variations.all()
                            product_variation.append(list(variation))
                            
                        # Get the cart items from the user to access his product variation
                        cart_item = CartItem.objects.filter(user=myuser)
                        ex_var_list = []
                        id = []
                        for item in cart_item:
                            existing_variation = item.variations.all()
                            ex_var_list.append(list(existing_variation)) 
                            id.append(item.id)
                        
                        for pr in product_variation:
                            if pr in ex_var_list:
                                index = ex_var_list.index(pr)
                                item_id = id[index]
                                item = CartItem.objects.get(id=item_id)
                                item.quantity += 1
                                item.user = myuser
                                item.save()  
                            else:
                                cart_item = CartItem.objects.filter(cart=cart) 
                                for item in cart_item:
                                    item.user = myuser
                                    item.save()
                except:
                     pass
                 
                auth.login(request, myuser)
                messages.success(request, 'You are logged in')
                return redirect('home')
        else:
            messages.error(request, 'Invalid email or password')
            return redirect('signin')
    else:
        return render(request, 'accounts/signin.html')
    
################################################################################################################

@login_required(login_url='signin')
def signout(request):   
    if 'email' in request.session:
        request.session.flush
    auth.logout(request)
    messages.success(request, 'You are logged out.')
    return redirect('signin')

#############################################################################################################

def forgotpassword(request):
    
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user =  Account.objects.get(email__exact=email)
            
            #reset password email
            current_site = get_current_site(request)
            mail_subject = 'humen: Reset your password'
            message = render_to_string('accounts/reset_account_password .html',{
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user),
            })
            to_email = email
            print(email)
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()
            messages.success(request,'Password reset email has been send to your email address')
            return redirect('signin')
        
        else:
            messages.error(request,'Account does not exist!!')
            return redirect('forgotpassword')
    return render(request, 'accounts/forgotpassword.html')

##########################################################################################################

def resetpassword_validate(request,uidb64,token):
    try:
        uid=urlsafe_base64_decode(uidb64).decode()
        user=Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user=None
    
    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid']=uid
        messages.success(request,'Please reset your password.!')
        return redirect('resetpassword')
    else:
        messages.error(request,'Sorry the activation link is has expired')
        return redirect('signin')
################################################################################################################   
    
def resetpassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,'successfully reset password')
            return redirect('signin')
        else:
            messages.error(request,"Password are not match")
            return redirect('resetpassword')
        
    else:
        return render(request,'accounts/resetpassword.html')
    
##############################################################################################################   
    
    
def user_otp_sign_in(request):
    '''handle the user otp sign in'''
    print("user otp ethii")
    otp_sign_in_user_status = ''
    if request.method == 'POST':
        print('helloooo')
        phone_number = request.POST.get('phone_number')
        request.session['phone_number'] = phone_number
        print(phone_number)

        if Account.objects.filter(phone_number=phone_number).exists():
            print('heloooo')

            user = Account.objects.get(phone_number=phone_number).email
            client = Client('AC529b57fdcebcfa5db3696c73959779e4',
                                 'edf5a5b7ec653195e7bea98a65a4c094')
            verification = client.verify \
                .v2 \
                .services('VA17d6c4e0348d4667123fc544b0830c25') \
                .verifications \
                .create(to='+91{}'.format(phone_number), channel='sms')
            request.session['username'] = user
            user_authentication_status = 'success'
            otp_sign_in_user_status = 'success'
            return JsonResponse({'otp_sign_in_user_status': otp_sign_in_user_status})
        else:
            return render(request, 'accounts/user_otp_sign_in.html', {'message': "invalid phone number"})
    else:
        return render(request, 'accounts/user_otp_sign_in.html')
    
##############################################################################################################
def user_otp_sign_in_validation(request):
    '''handle the user otp validation'''
    if request.method == 'POST':
        otp_1 = request.POST.get('otp_1')
        otp_2 = request.POST.get('otp_2')
        otp_3 = request.POST.get('otp_3')
        otp_4 = request.POST.get('otp_4')
        # var err = document.getElementById('err')

        user_otp = str(otp_1 + otp_2 + otp_3 + otp_4)
        print(otp)
        print(user_otp)
        phone_number = request.session['phone_number']
        client = Client('AC529b57fdcebcfa5db3696c73959779e4',
                        'edf5a5b7ec653195e7bea98a65a4c094')
        verification_check = client.verify \
            .v2 \
            .services('VA17d6c4e0348d4667123fc544b0830c25') \
            .verification_checks \
            .create(to='+91{}'.format(phone_number), code=user_otp)

        print(verification_check.status)
        user_authentication_status = 'approved'
        # user_authentication_status = 'wrong_otp'
        # if str(user_otp) == str(otp):
        #     user_authentication_status = 'otp_verified'
        #     user = Users.objects.get(contact_number = str(request.session['contact_number']))
        #     request.session['user'] = user.email
        return JsonResponse({'user_authentication_status': user_authentication_status})
    return render(request, 'user_otp_sign_in_validation.html')    
 
###############################################################################################################
 
 

    
 
    
@login_required(login_url='signin')
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    
    context ={
        'orders':orders,
    }
    return render(request, 'accounts/my_orders.html',context)

#############################################################################################################