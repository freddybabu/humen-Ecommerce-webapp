from django.contrib import admin
from .models import Product,Variation,ProductImage
# Register your models here.

class PictureInline(admin.StackedInline):
    model = ProductImage

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name','price','stock','category','modified_date','is_available','slug')
    prepopulated_fields = {'slug':('product_name',)}
    inlines = [PictureInline]
    
    

class VariationAdmin(admin.ModelAdmin):
    list_display = ('product','variation_category', 'variation_value', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('product','variation_category', 'variation_value')

admin.site.register(Product,ProductAdmin)
admin.site.register(Variation,VariationAdmin)

    



