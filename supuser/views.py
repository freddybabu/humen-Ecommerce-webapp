from django.shortcuts import render,redirect,get_object_or_404
from accounts.models import Account
from category.models import Category
from store.models import Product,ProductImage,Variation
from supuser.forms import CategoryForm,ProductForm,VariationForm

# Create your views here.

def supuser(request):
    if 'email' in request.session:
        return render(request,'supuser/suphome.html')
    return redirect('signin')




def usermanage(request):
    if 'email' in request.session:
        users = Account.objects.filter(is_superadmin=False).order_by('id').reverse()
        context = {
            'users': users,
        }
        return render(request,'supuser/customer.html',context)
    return redirect('signin')
    
    
def block_user(request,id):
    if request.method == 'POST':
        pi = Account.objects.get(id=id)
        pi.is_active=False
        pi.save()
        return redirect('manage')
    
def unblock_user(request,id):
    if request.method == 'POST':
        pi = Account.objects.get(id=id)
        pi.is_active=True
        pi.save()
        return redirect('manage')
    

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

def del_category(request,id):
    if request.method == "POST":
        crt = Category.objects.get(id=id)
        crt.delete()
    return redirect('categorymanage')


def productmanage(request):
    if 'email' in request.session:
        Products = Product.objects.all()
        context = {
            "Products" : Products 
        }
        return render(request, 'supuser/products.html', context)
    return redirect('signin')




# def add_product(request):
#     if request.method == "POST":
#         product_form = ProductForm(request.POST, request.FILES)
#         if product_form.is_valid():
#             myproduct = product_form.save(commit=False)
#             myproduct.save()
#             return redirect('productmanage')    
#     else:
#         product_form = ProductForm()
    
#     context = {'product_form': product_form,}
#     return render(request, 'supuser/add_product.html', context)

def add_product(request):
    if request.method == "POST":
        product_form = ProductForm(request.POST, request.FILES)
        if product_form.is_valid():
            myproduct = product_form.save(commit=False)
            myproduct.save()
            image = request.FILES.get('image')
            if image:
                ProductImage.objects.create(product=myproduct, image=image)
            return redirect('productmanage')
    else:
        product_form = ProductForm()
    
    context = {'product_form': product_form}
    return render(request, 'supuser/add_product.html', context)


def del_product(request,id):
    if request.method == "POST":
        prod = Product.objects.get(id=id)
        prod.delete()
    return redirect('productmanage')


def edit_product(request, id):
    product = get_object_or_404(Product, id=id)
    if request.method == "POST":
        product_form = ProductForm(request.POST, request.FILES, instance=Product)
        if product_form.is_valid():
            product_form.save()
            return redirect('productmanage')
    else:
        product_form = ProductForm(instance=Product)

    context = {
        "product_form": product_form
    }
    return render(request, 'supuser/edit_product.html', context)


def Variationmanage(request):
    if 'email' in request.session:
        variations = Variation.objects.all()
        context = {
            "variations" : variations
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
        "variationform":variationform
    }
    return render(request,'supuser/add_variation.html',context)


def edit_variation(request,id):
    variate = get_object_or_404(Variation,id=id)
    if request.method == "POST":
        variationform = VariationForm(request.POST,instance=variate)
        if variationform.is_valid():
            variationform.save()
            return redirect('Variationmanage')
    else:
        variationform = VariationForm(instance=variate)
    context = {
        "variationform":variationform
    }
    return render(request, 'supuser/edit_variation.html',context)

def delete_variation(request,id):
    if request.method == "POST":
        variate = Variation.objects.get(id=id)
        variate.delete()
    return redirect('Variationmanage')
        