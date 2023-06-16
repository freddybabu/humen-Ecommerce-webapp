import datetime
from django.shortcuts import render,redirect
from django.http import JsonResponse
from carts.models import CartItem
from .forms import OrderForm
import datetime
from .models import Order,OrderProduct,Payment
import json
from store.models import Product
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
# Create your views here.


def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])
    print(body)
    
    #store transaction details in inside payment model
    payment = Payment(
        user=request.user,
        payment_id=body['transID'],
        payment_method=body['payment_method'],
        amount_paid=order.order_total,
        status=body['status'],
    )
    payment.save()
    
    order.payment = payment
    order.is_ordered = True
    order.save()
    
    #move the cart items to Orderproduct table
    cart_items = CartItem.objects.filter(user=request.user)
    
    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment  = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()
        
        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()
    
        #reduce the quantity of the sold products
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()
    
    #clear the cart
    CartItem.objects.filter(user=request.user).delete()
    
    #send email confirmation to the customer
    # mail_subject = 'Thank you for your order!'
    # message = render_to_string('orders/order_recieved_email.html',{
    #     'user':request.user,
    #     'order':order,
    # })
    # to_email = request.user.email
    # send_email = EmailMessage(mail_subject,message,to=[to_email])
    # send_email.send()
    
    
    
    #send order number  and transaction id back to  sendData method via jsonResponse
    data={
        'order_number':order.order_number,
        'transID':payment.payment_id
    }
    return JsonResponse(data)

def place_order(request, total=0,quantity=0):
    current_user = request.user
    shipping_charge = 40
    grand_total = 0
    # if the cart count is less than or equal to 0,then redirect back to shop
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')
    
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    grand_total = total + shipping_charge
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # store all the billing information inside order table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name'] 
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = total
            data.ip = request.META.get('REMOTE_ADDR')  
            data.save()
            # generate order number 
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d  = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d") 
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()
            
            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order':order,
                'cart_items':cart_items,
                'total':total,
                'shipping_charge':shipping_charge,
                'grand_total':grand_total,
            }
            
            return render(request, 'orders/payments.html', context)
        
    else:
        return redirect('checkout')
    
    return redirect('checkout')
    
 
def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')  
    
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_product = OrderProduct.objects.filter(order_id=order.id)
        
        payment = Payment.objects.get(payment_id=transID)
        
        shipping_charge = 40
        sub_total =0
        for item in ordered_product:
            sub_total = item.product_price*item.quantity
         
        grand_total = sub_total+shipping_charge   
        context = {
            'order':order,
            'ordered_product':ordered_product,
            'order_number':order.order_number,
            'transID':payment.payment_id,
            'payment':payment,
            'shipping_charge':shipping_charge,
            'sub_total':sub_total,
            'grand_total':grand_total,
        }
        return render(request, 'orders/order_complete.html', context)

    except (Payment.DoesNotExist,Order.DoesNotExist):
        return redirect('home')
        
       



    
            
            