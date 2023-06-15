import re
from django import forms
from .models import Account,AddressBook,UserProfile 


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
        
        #password strength validation
        if password:
            # Ensure the password meets the required criteria
            if len(password) < 8:
                raise forms.ValidationError("Password must be at least 8 characters long.")
            if not re.search(r'\d', password):
                raise forms.ValidationError("Password must contain at least one digit.")
            if not re.search(r'[A-Z]', password):
                raise forms.ValidationError("Password must contain at least one uppercase letter.")
            if not re.search(r'[a-z]', password):
                raise forms.ValidationError("Password must contain at least one lowercase letter.")
            if not re.search(r'[!@#$%^&*()-=_+]', password):
                raise forms.ValidationError("Password must contain at least one special character (!@#$%^&*()-=_+).")

        return clean_data
        
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
        
    
    def __init__(self, *args, **kwargs):
        super(UserForm,self).__init__( *args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
        
    
        
class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False,error_messages= {'invalid':"image files only"}, widget=forms.FileInput)
    class Meta:
        model = UserProfile
        fields = ("address_line_1","address_line_2","city","state","country","profile_picture")
        
    def __init__(self, *args, **kwargs):
        super(UserProfileForm,self).__init__( *args, **kwargs)
        for field in self.fields:
             self.fields[field].widget.attrs['class'] = 'form-control'
        
    
        
class AddressBookForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control my-2', 'placeholder':'First Name'}))
    last_name  = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control my-2','placeholder':'Last Name'}))
    phone      = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control my-2','placeholder':'Phone Number'}))
    email      = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control my-2','placeholder':'E-mail'}))
    address_line_1 = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control my-2','placeholder':'House name & Locality'}))
    address_line_2 = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control my-2','placeholder':'Address line 2(optional)'}))
    city         = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control my-2','placeholder':'City'}))
    state        = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control my-2','placeholder':'State'}))
    country      = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control my-2','placeholder':'Country'}))
    pincode      = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control my-2','placeholder':'Pincode'}))
    status       = forms.BooleanField(required=False,widget=forms.CheckboxInput())
    
    class Meta:
        model = AddressBook
        fields = ['first_name','last_name','phone','email','address_line_1','address_line_2','city','state','country','pincode','status']
        exclude = ("user",)