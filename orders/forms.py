from django import forms
from .models import Order,Return


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name','last_name','phone','email','address_line_1','address_line_2','country','state','city','order_note']
        
        
class ReturnForm(forms.Form):
    
    reason = forms.CharField(max_length=200,widget=forms.Textarea(attrs={"class":"form-control"}))
    
    class Meta:
        model = Return
        fields = ['reason']
        