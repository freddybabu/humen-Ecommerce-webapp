from django.db import models
from category.models import Category
from django.urls import reverse
from django.core.validators import MinValueValidator
from accounts.models import Account


# Create your models here.

class Product(models.Model):
    product_name = models.CharField(max_length=200,unique=True)
    slug         = models.SlugField(max_length=200,unique=True)
    description  = models.TextField(max_length=500,blank=True)
    price        = models.IntegerField()
    offer_price  = models.IntegerField(null=True, blank=True)
    images       = models.ImageField(upload_to='photos/products')
    stock        = models.IntegerField(validators=[MinValueValidator(0)])
    is_available = models.BooleanField(default=True)
    category     = models.ForeignKey(Category,on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    
    objects = models.Manager()
    
    def get_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])

    
    def __str__(self):
        return str(self.product_name)
    
    def get_image_upload_path(instance, filename):
        
        return 'photos/products/{0}/{1}'.format(instance.slug, filename)
    
    
    images = models.ImageField(upload_to=get_image_upload_path)
    
  
class ProductImage(models.Model):
    Product = models.ForeignKey(Product, on_delete=models.CASCADE)
    images  = models.ImageField(upload_to='photos/products')
    
    def __str__(self) -> str:
        return self.images.url
    

class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager, self).filter(variation_category='color', is_active=True)   
    
    def sizes(self):
        return super(VariationManager, self).filter(variation_category='size', is_active=True)

variation_category_choice = (
    ('color','color'),
    ('size','size'),
)

class Variation(models.Model):
    product  = models.ForeignKey(Product,on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=100, choices=variation_category_choice)
    variation_value = models.CharField(max_length=100)
    stock = models.IntegerField(default=0,validators=[MinValueValidator(0)])
    is_active  = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)
    
    objects = VariationManager()
    
    def __str__(self) -> str:
        return self.variation_value
      
class Wishlist(models.Model):
    user = models.ForeignKey(Account,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True) 
    
all_items = Wishlist.objects.all()
    

class ReviewRating(models.Model):
    products = models.ForeignKey(Product,on_delete=models.CASCADE)
    user = models.ForeignKey(Account,on_delete=models.CASCADE)
    subject = models.CharField(max_length=100,blank=True)
    review  = models.TextField(max_length=500,blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20,blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.subject
    
