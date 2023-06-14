from django.shortcuts import get_object_or_404
import random
from django.contrib import messages, auth
from django.http import JsonResponse
from .import verify
from orders.models import Order,OrderProduct
from django.contrib.auth import authenticate, login,logout
from django.shortcuts import render, redirect
from django.conf import settings
from .forms import RegistrationForm,UserForm,VerifyForm,AddressBookForm,UserProfileForm
from carts.models import Cart,CartItem
from store.models import Wishlist,Product
from .models import Account,AddressBook
from django.contrib.auth.decorators import login_required
from carts.views import _cart_id
from django.views.decorators.cache import never_cache
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.core.exceptions import ObjectDoesNotExist
import requests

from twilio.rest import Client
from accounts.verify import send,check


@never_cache
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
        'orders_count':orders_count,
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

@login_required(login_url='signin')
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
            print(to_email)
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()
            messages.success(request,'Password reset email has been send to your email address')
            return redirect('signin')
        else:
            messages.error(request,'Account does not exist!!')
            return redirect('forgotpassword')
    return render(request, 'accounts/forgotpassword.html')

##########################################################################################################
@login_required(login_url='signin')
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
@login_required(login_url='signin')    
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
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        phone_number = request.POST['phone_number']
        if Account.objects.all().filter(phone_number=phone_number):
            # phone_number_with_country_code='+91'+phone_number
            send(phone_number)
            return redirect(user_otp_sign_in_validation,phone_number)
        else:
            messages.error(request, 'Phone number is not registered with us')
    return render(request,'accounts/login_otp.html')

###############################################################################################################

def user_otp_sign_in_validation(request, phone_number):
    '''handle the user otp validation'''
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        otp_code = request.POST['otp']
        # phone_number_with_country_code = '+91' + phone_number
        try:
            user = Account.objects.get(phone_number=phone_number)
        except ObjectDoesNotExist:
            messages.error(request, 'User does not exist')
            return redirect('home')
        except Account.MultipleObjectsReturned:
            messages.error(request, 'Multiple accounts with the same phone number')
            return redirect('home')

        if check(phone_number, otp_code):
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Incorrect OTP')    
    return render(request, 'accounts/login_otp_verify.html')    
###############################################################################################################
    
@login_required(login_url='signin')
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    
    context ={
        'orders':orders,
    }
    return render(request, 'accounts/my_orders.html',context)

#############################################################################################################

def whishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    context = {
        'wishlist_items':wishlist_items
    }
    return render(request,'store/wishlist.html',context)
##############################################################################################################

@login_required(login_url='signin')
def order_details(request,order_id):
    try:
        order_product = OrderProduct.objects.filter(order__order_number=order_id)
        order = Order.objects.get(order_number=order_id)
        sub_total = 0
        shipping_charge=40
        grand_total = 0
        for i in order_product:
            sub_total += i.product_price * i.quantity
        
        grand_total = sub_total+shipping_charge
        context = {
            'order_product':order_product,
            'order':order,
            'sub_total':sub_total,
            'shipping_charge':shipping_charge,
            'grand_total':grand_total,
            
        }
        
    except Order.DoesNotExist:
        
        context ={
            'error_message':'Order does not exist'
        }
        
    return render(request,'accounts/order_details.html',context)

################################################################################################################

def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if order.status == 'Cancelled':
        messages.warning(request, 'This order has already been cancelled.')
    else:
        # Iterate over the order items
        for order_product in order.orderproduct_set.all():
            # Increase the stock quantity of each product
            product = order_product.product
            product.stock += order_product.quantity
            product.save()
        
        order.status = 'Cancelled'
        order.save()
        messages.success(request, 'Order successfully cancelled.')
        
    return redirect('my_orders')
    
#################################################################################################################
@login_required(login_url='signin')
def add_to_wishlist(request,product_id):
    myproduct = get_object_or_404(Product, id=product_id)
    created = Wishlist.objects.get_or_create(user=request.user,product=myproduct)
    if created:
        messages.success(request,'Product added to wishlist')
    else:
        messages.info(request,'Product already in wishlist.')
    return redirect('wishlist')

###############################################################################################################
@login_required(login_url='signin')
def remove_from_wishlist(request,product_id):
    myproduct = get_object_or_404(Product,id=product_id)
    Wishlist.objects.filter(user=request.user,product=myproduct).delete()
    messages.success(request,'Product removed from wishlist.')
    return redirect('wishlist')
    
################################################################################################################
def my_addresses(request):
    addresses =  AddressBook.objects.filter(user=request.user).order_by('-id')
    context = {
        'addresses':addresses
    }  
    return render(request,'accounts/my_addresses.html',context)

###############################################################################################################
@login_required(login_url='signin')
def add_addresses(request):
    form = AddressBookForm()
    if request.method == "POST":
        form = AddressBookForm(request.POST)
        if form.is_valid(): 
            saveform=form.save(commit=False)
            saveform.user = request.user
            saveform.save()
            messages.success(request,"New address added successfully")
            return redirect('my_addresses')
    context ={
        'form':form
    }
    return render(request,'accounts/add_address.html',context)
##################################################################################################################

def activate_address(request):
    a_id = request.GET['id']
    AddressBook.objects.update(status=False)
    AddressBook.objects.filter(id=a_id).update(status=True)
    
    return JsonResponse({'bool':True})   
    
##############################################################################################################
@login_required(login_url='signin')
def edit_profile(request):
    user_form = UserForm(instance=request.user)
    
    if request.method == 'POST':
        user_form = UserForm(request.POST,instance=request.user)
        if user_form.is_valid():
            user_form.save()
            messages.success(request,"Profile updated successfully")
            return redirect('edit_profile')
        
    context = {
        'user_form':user_form,
    }
    return render(request, 'accounts/edit_profile.html',context)
      