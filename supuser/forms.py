from django import forms

from category.models import Category
from store.models import Product,Variation,ProductImage


class CategoryForm(forms.ModelForm):
    
    class Meta:
       model =  Category
       fields = ["category_name","description"]
       


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["product_name", "description","slug", "price", "images","stock","is_available", "category"]
        widgets = {
            'images': forms.ClearableFileInput(attrs={'multiple': True, 'class': 'form-control'}),
            'product_name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }

  
    images = forms.ImageField(label='Product Image', required=True, error_messages={'required': 'Please upload an image.'})

class images(forms.ModelForm):
    model = ProductImage
    fields = ["product","images"]
    
    
class VariationForm(forms.ModelForm):
    
    class Meta:
        model = Variation
        fields = ["product","variation_category","variation_value","is_active"]
        
