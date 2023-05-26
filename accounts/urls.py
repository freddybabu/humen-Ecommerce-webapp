from django.urls import path
from . import views

urlpatterns = [
    path('register/',views.register, name='register'),
    path('signin/',views.signin, name='signin'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('signout/',views.signout, name='signout'),
    path('ver',views.verify_code, name='ver'),
    
    path('forgotpassword/',views.forgotpassword,name='forgotpassword'),
    path('resetpassword_validate/<uidb64>/<token>/',views.resetpassword_validate,name='resetpassword-validate'),
    path('resetpassword',views.resetpassword,name='resetpassword'),
    
    path('my_orders/',views.my_orders,name='my_orders'),
]