from django import forms

from category.models import Category
from store.models import Product,Variation


class CategoryForm(forms.ModelForm):
    
    class Meta:
       model =  Category
       fields = ["category_name","description"]
       


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["product_name","description","price","stock","is_available","category"]
        widgets = {
            'images':forms.ClearableFileInput(attrs={})
        }
    
    images = forms.ImageField(label='Product_image', required=False, error_messages={'required':'please upload an image'})

    
    
    
class VariationForm(forms.ModelForm):
    
    class Meta:
        model = Variation
        fields = ["product","variation_category","variation_value","is_active"]
