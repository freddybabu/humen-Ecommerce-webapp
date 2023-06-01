import datetime
from django.shortcuts import render,redirect
from carts.models import CartItem
from .forms import OrderForm
from .models import Order,OrderProduct


# Create your views here.


def payments(request):
    return render(request,'orders/payments.html')

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
    # transation_ID = request.GET.get()  
    
    try:
        order = Order.objects.get(order_number=order_number,is_ordered=True)
        ordered_product = OrderProduct.objects.filter(order_id=order.id)

        sub_total =0
        for item in ordered_product:
            sub_total = item.product_price*item.quantity
            
        context = {
            'order':order,
            'ordered_product':ordered_product,
            'sub_total':sub_total
        }
        return render(request, 'orders/order_complete.html', context)

    except Order.DoesNotExist:
       return redirect('home')



    
            
            