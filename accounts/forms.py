from django import forms
from .models import Account


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
          'placeholder':'Enter password',
          'class':'form-label',
    } ))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
          'placeholder':'Confirm password'
    } ))
    class Meta:
        model = Account
        fields = ['first_name','last_name','phone_number','email','password']
        
    def __init__(self, *args, **kwargs):
        super(RegistrationForm,self).__init__(*args,**kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter first Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter Last Name'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter phonenumber'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter Email address'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-label'
            
    def clean(self):
        clean_data = super(RegistrationForm,self).clean()
        password = clean_data.get('password')
        confirm_password = clean_data.get('confirm_password')
        
        if password != confirm_password:
            raise forms.ValidationError(
                "password does not match!"
            )
    
        
class VerifyForm(forms.Form):
    code = forms.CharField(
        max_length=8,
        required=True,
        help_text='Enter code',
        widget=forms.TextInput(attrs={'class': 'custom-class', 'placeholder': 'Enter code here'})
    )
    
class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ("first_name","last_name","phone_number")
        widgets = {
            "first_name":forms.TextInput(attrs={"class":"form-control"}),
            "last_name":forms.TextInput(attrs={"class":"form-control"}),
            "phone_number":forms.TextInput(attrs={"class":"form-control", 'placeholder':'9744733924'}),
        }