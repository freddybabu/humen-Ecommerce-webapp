import json
from datetime import date
from django.http import HttpResponse,JsonResponse
from django.shortcuts import render,redirect,get_object_or_404
from store.models import Product,Variation
from .models import Cart,CartItem
from accounts.models import AddressBook
from supuser.models import Coupon
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from datetime import datetime
from django.contrib import messages

# Create your views here.

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request,product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id) #get the product
    # if user is authenticated
    if current_user.is_authenticated:
            product_variation = []
            if request.method == 'POST':
                for item in request.POST:
                    key = item
                    value = request.POST[key]
                    
                    try:
                        variation = Variation.objects.get(product=product,variation_category__iexact=key, variation_value__iexact=value)
                        product_variation.append(variation)
                    except:
                        pass
            
            is_cart_exists = CartItem.objects.filter(product=product,user=current_user).exists()
            if is_cart_exists:
                cart_item = CartItem.objects.filter(product=product,user=current_user)
                ex_var_list = []
                id = []
                for item in cart_item:
                    existing_variation = item.variations.all()
                    ex_var_list.append(list(existing_variation)) 
                    id.append(item.id)   
                
                if product_variation in ex_var_list:
                    # increase cart item quantity
                    index = ex_var_list.index(product_variation)
                    item_id = id[index]
                    item = CartItem.objects.get(product=product, id=item_id)
                    item.quantity += 1
                    item.save()
                else:
                    item = CartItem.objects.create(product=product, quantity=1, user=current_user)
                    if len(product_variation) > 0:
                        item.variations.clear()
                        item.variations.add(*product_variation)
                    item.save() 
            else:
                cart_item = CartItem.objects.create(
                    product = product,
                    quantity = 1,
                    user = current_user,
                )
                if len(product_variation) > 0:
                    cart_item.variations.clear()
                    cart_item.variations.add(*product_variation)
                cart_item.save()
            return redirect('cart')
        
    else:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
                
                try:
                    variation = Variation.objects.get(product=product,variation_category_iexact=key, variation_value_iexact=value)
                    product_variation.append(variation)
                except:
                    pass
        
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request)) #get the cart using the cart_id present in the session
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
        cart.save()
        
        is_cart_exists = CartItem.objects.filter(product=product,cart=cart).exists()
        if is_cart_exists:
            cart_item = CartItem.objects.filter(product=product,cart=cart)
            # existing_variations-->database
            # current variation --> product_variation
            # item_id --> database
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation)) 
                id.append(item.id)   
                
            print(ex_var_list)
            
            if product_variation in ex_var_list:
                # increase cart item quantity
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()
            else:
                item = CartItem.objects.create(product=product, quantity=1, cart=cart)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save() 
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                cart = cart,
            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        return redirect('cart')

def remove_cart(request,product_id,cart_item_id):
    
    product = get_object_or_404(Product,id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product,user=request.user, id=cart_item_id)
        else:
             cart = Cart.objects.get(cart_id=_cart_id(request))
             cart_item = CartItem.objects.get(product=product,cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete() 
    except:
        pass     
    return redirect('cart')

def remove_cart_item(request,product_id,cart_item_id):
    
    product = get_object_or_404(Product,id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
    else:
         cart = Cart.objects.get(cart_id=_cart_id(request))
         cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')

def cart(request,total=0, quantity=0, cart_items =None):
    grand_total = 0
    shipping_charge = 40
    coupons =None
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user,is_active=True)
        
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart,is_active=True)
            coupons = Coupon.objects.all()
        for cart_item in cart_items:
            total += (cart_item.product.price*cart_item.quantity)
            quantity += cart_item.quantity
        grand_total = total + shipping_charge
    except ObjectDoesNotExist:
           pass
    
    context = {
        'total':total,
        'quantity':quantity,
        'cart_items':cart_items,
        'shipping_charge':shipping_charge,
        'grand_total':grand_total,
        'coupons':coupons
    }
         
    return render(request,'store/cart.html', context)


@login_required(login_url='signin')
def checkout(request):
    total = 0
    quantity = 0
    grand_total = 0
    shipping_charge = 40
    cart_items = None
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user,is_active=True)
        else:
             cart = Cart.objects.get(cart_id=_cart_id(request))
             cart_items = CartItem.objects.filter(cart=cart,is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price*cart_item.quantity)
            quantity += cart_item.quantity
        grand_total = total + shipping_charge
        
        # if(request.session.get('total')):
        #     grand_total=request.session.get('total')
        
        addresses = AddressBook.objects.filter(user=request.user).order_by('-id')
        cadd  = AddressBook.objects.filter(user=request.user,status=True).first()
        
    except ObjectDoesNotExist:
           pass
    
    context = {
        'total':total,
        'quantity':quantity,
        'shipping_charge':shipping_charge,
        'cart_items':cart_items,
        'grand_total':grand_total,
        'addresses':addresses,
        'cadd':cadd,
    }
    return render(request,'store/checkout.html', context)


@require_POST
def apply_coupon(request):
    body = json.loads(request.body)
    print(body)
    grand_total = int(body['grand_total'])
    coupon_code = body['coupon']
    try:
        coupon = Coupon.objects.get(code__iexact=coupon_code)
    except Coupon.DoesNotExist:
        data = {
            "total": grand_total,
            "message": "Not a Valid Coupon"
        }
    else:
        today = date.today()
        valid_from = coupon.active_date
        valid_to = coupon.expiry_date
        min_amount = int(coupon.min_amount)
        if min_amount < grand_total and valid_from <= today <= valid_to:
            discount_amount = int(coupon.discount)
            grand_total -= discount_amount
            request.session['total'] = grand_total  # Update the session variable
            data = {
                "total": grand_total,
                "message": f"{coupon.code} Applied",
                "discount_amount": discount_amount,
            }
        else:
            data = {
                "total": grand_total,
                "message": "Not a Valid Coupon"
            }
    return JsonResponse(data)
        
   

         
        
        
    