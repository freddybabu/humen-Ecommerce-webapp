import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.core import serializers
from django.forms import inlineformset_factory
from accounts.models import Account
from category.models import Category
from orders.models import Order, OrderProduct
from store.models import Product, ProductImage, Variation
from supuser.forms import CategoryForm, ProductForm, VariationForm, images,CouponForm
from datetime import datetime,timedelta,timezone
from supuser.models import Coupon
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
# Create your views here.


def supuser(request):
    if 'email' in request.session:
        orders = Order.objects.all().order_by('-created_at')[:5]
    
        users = Account.objects.all()
        users_count = users.count()

        myproducts = Product.objects.all().order_by('-id')
    
        categories = Category.objects.all()
        category_count = categories.count()
    
        total_order = Order.objects.all()
        total_orders = total_order.count()
    
        today = datetime.today()
        start_of_week = today - timedelta(days=today.weekday())
        dates = [start_of_week + timedelta(days=i) for i in range(7)]
        sales = []
        for date in dates:
            Orders = OrderProduct.objects.filter(
                ordered=True,
                created_at__year=date.year,
                created_at__month=date.month,
                created_at__day=date.day,
            )
            total_sales = sum(order.product_price * order.quantity for order in Orders)
            sales.append(total_sales)
        sums = sum(sales)
        product_count = myproducts.exclude(orderproduct__ordered=True).count()
        context = {
            'orders': orders,
            'product_count': product_count,
            'category_count': category_count,
            'products': myproducts,
            'total_orders': total_orders,
            "users_count": users_count,
            'dates': dates,
            'sales': sales,
            'sums': sums
        }
        return render(request, 'supuser/suphome.html', context)
    else:
        return redirect('signin')

#================================== USER MANAGE =========================================================== #

def usermanage(request):
    if 'email' in request.session:
        user_list = Account.objects.filter(is_superadmin=False).order_by('id').reverse()
        paginator = Paginator(user_list, 6)  # Display 10 users per page

        page_number = request.GET.get('page')
        users = paginator.get_page(page_number)

        context = {
            'users': users,
        }
        return render(request, 'supuser/customer.html', context)
    return redirect('signin')


def block_user(request, id):
    if request.method == 'POST':
        pi = Account.objects.get(id=id)
        pi.is_active = False
        pi.save()
        return redirect('manage')


def unblock_user(request, id):
    if request.method == 'POST':
        pi = Account.objects.get(id=id)
        pi.is_active = True
        pi.save()
        return redirect('manage')

#============================================ CATEGORY MANAGE ================================================

def categorymanage(request):
    if 'email' in request.session:
        categories = Category.objects.all()
        context = {
            "category": categories
        }
        return render(request, 'supuser/category.html', context)
    return redirect('signin')


def add_category(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('categorymanage')
    else:
        form = CategoryForm()
    context = {
        "form": form
    }
    return render(request, 'supuser/add_category.html', context)


def del_category(request, id):
    if request.method == "POST":
        crt = Category.objects.get(id=id)
        crt.delete()
    return redirect('categorymanage')

#======================================== PRODUCT MANAGE =====================================================

def productmanage(request):
    if 'email' in request.session:
        # Products = Product.objects.all()
        Products = Product.objects.order_by('-created_date')

        context = {
            "Products": Products
        }
        return render(request, 'supuser/products.html', context)
    return redirect('signin')


# ProductImageFormSet = inlineformset_factory(product, ProductImage, form=images, extra=3)
ProductImageFormSet = inlineformset_factory(
    Product, ProductImage, form=images, extra=3, fields=['images'])


def add_product(request):
    if request.method == "POST":
        product_form = ProductForm(request.POST, request.FILES)
        image_form = ProductImageFormSet(request.POST,request.FILES,instance=Product())
        if product_form.is_valid() and image_form.is_valid():
            myproduct = product_form.save(commit=False)
            myproduct.save()
            image_form.instance = myproduct
            image_form.save()
            return redirect('productmanage')
    else:
        product_form = ProductForm()
        image_form = ProductImageFormSet(instance=Product())

    context = {'product_form': product_form,'image_form':image_form}
    return render(request, 'supuser/add_product.html', context)


def del_product(request, id):
    if request.method == "POST":
        prod = Product.objects.get(id=id)
        prod.delete()
    return redirect('productmanage')


def edit_product(request, id):
    product = get_object_or_404(Product, id=id)
    if request.method == "POST":
        product_form = ProductForm(
            request.POST, request.FILES, instance=product)
        if product_form.is_valid():
            product_form.save()
            return redirect('productmanage')
    else:
        product_form = ProductForm(instance=product)

    context = {
        "product_form": product_form
    }
    return render(request, 'supuser/edit_product.html', context)

#================================================= VARIATION MANAGE ============================================

def Variationmanage(request):
    if 'email' in request.session:
        variation_list = Variation.objects.all()
        paginator = Paginator(variation_list, 5)  # Display 10 variations per page

        page_number = request.GET.get('page')
        variations = paginator.get_page(page_number)

        context = {
            "variations": variations
        }
        return render(request, 'supuser/Variation.html', context)
    return redirect('signin')


def add_variation(request):
    if request.method == "POST":
        variationform = VariationForm(request.POST)
        if variationform.is_valid():
            variationform.save()
            return redirect('Variationmanage')

    else:
        variationform = VariationForm()
    context = {
        "variationform": variationform
    }
    return render(request, 'supuser/add_variation.html', context)


def edit_variation(request, id):
    variate = get_object_or_404(Variation, id=id)
    if request.method == "POST":
        variationform = VariationForm(request.POST, instance=variate)
        if variationform.is_valid():
            variationform.save()
            return redirect('Variationmanage')
    else:
        variationform = VariationForm(instance=variate)
    context = {
        "variationform": variationform
    }
    return render(request, 'supuser/edit_variation.html', context)


def delete_variation(request, id):
    if request.method == "POST":
        variate = Variation.objects.get(id=id)
        variate.delete()
    return redirect('Variationmanage')

#============================================= ORDER MANAGE ===================================================

def orderslist(request):
    order_list = Order.objects.all().order_by('-created_at')
    paginator = Paginator(order_list, 10)  # Number of orders per page

    page = request.GET.get('page')
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)

    context = {
        'orders': orders,
    }
    return render(request, 'supuser/orders_list.html', context)



def order_details_admin(request, order_id):
    try:
        sub_total = 0
        shipping_charge = 40
        grand_total = 0
        order_product = OrderProduct.objects.filter(
            order__order_number=order_id)
        order = Order.objects.get(order_number=order_id)
        for i in order_product:
            sub_total += i.product_price * i.quantity
        grand_total = sub_total + shipping_charge

        context = {
            'order_product': order_product,
            'order': order,
            'sub_total': sub_total,
            'shipping_charge':shipping_charge,
            'grand_total':grand_total,
        }
    except Order.DoesNotExist:

        context = {
            'error_message': 'Order does not exist'
        }
    return render(request, 'supuser/order_details_admin.html', context)


def change_status(request, order_id):
    if request.method == 'POST':
        status = request.POST.get('status')
        try:
            order = Order.objects.get(id=order_id)
            order.status = status
            order.save()
        except Order.DoesNotExist:
            pass
    return redirect('orderslist')

#================================= COUPON MANAGE ====================================================================================

def coupen_manage(request):
    coupens = Coupon.objects.all()
    context = {
        "coupens":coupens
    }
    return render(request,'supuser/coupen_manage.html',context)


def add_coupens(request):
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('coupen_manage')
    else:
        form=CouponForm()
        
    context = {
        'form':form
    }
    return render(request,'supuser/add_coupons.html',context)


def del_coupens(request,id):
    if request.method == "POST":
        coup = Coupon.objects.get(id=id)
        coup.delete()
    return redirect('coupen_manage')

def edit_coupens(request,id):
    if request.method == "POST":
        coup = Coupon.objects.get(id=id)
        form = CouponForm(request.POST,instance=coup)
        if form.is_valid:
            form.save()
        return redirect('coupen_manage')
    else:
        coup = Coupon.objects.get(id=id)
        form = CouponForm(instance=coup)
        context = {
            "form":form
        }
    return render(request,'supuser/edit_coupen.html',context)
    

  
def add_order_filter(request):
    body = json.loads(request.body)
    try:
        start_date =datetime.strptime(body['from'],'%Y-%m-%d')
        end_date = datetime.strptime(body['to'],'%Y-%m-%d')
    except ValueError:
        end_date = timezone.now()
        start_date = end_date - timedelta(days=end_date.weekday())
    try:
        orders = Order.objects.filter(created_at__gte=start_date, created_at__lte=end_date)
        json_data = serializers.serialize('json', orders)
    except Order.DoesNotExist:
        orders = None     
    data ={
             "order":json_data,
            }
    return JsonResponse(data)      