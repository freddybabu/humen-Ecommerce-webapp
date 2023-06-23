from django.urls import path
from . import views

urlpatterns = [
    path('register/',views.register, name='register'),
    path('signin/',views.signin, name='signin'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('signout/',views.signout, name='signout'),
    path('ver',views.verify_code, name='ver'),
    
    path('forgotpassword',views.forgotpassword,name='forgotpassword'),
    path('resetpassword_validate/<uidb64>/<token>/',views.resetpassword_validate,name='resetpassword-validate'),
    path('resetpassword',views.resetpassword,name='resetpassword'),
    
    path('user_otp_sign_in',views.user_otp_sign_in,name='user_otp_sign_in'),
    path('user_otp_sign_in_validation/<str:phone_number>/',views.user_otp_sign_in_validation,name='user_otp_sign_in_validation'),
    
    path('my_orders/',views.my_orders,name='my_orders'),
    path('order_details/<int:order_id>/',views.order_details,name='order_details'),
    path('order_details/cancel_order/<int:order_id>/', views.cancel_order,name='cancel_order'),
    
    path('wishlist/',views.whishlist,name='wishlist'),
    path('add_to_wishlist/<int:product_id>/',views.add_to_wishlist,name='add_to_wishlist'),
    path('remove_from_wishlist/<int:product_id>/',views.remove_from_wishlist,name='remove_from_wishlist'),
    
    path('my_addresses/',views.my_addresses,name='my_addresses'),
    path('my_addresses/add_addresses',views.add_addresses,name='add_addresses'),
    path('activate-address/',views.activate_address,name='activate-address'),
    path('edit_profile/',views.edit_profile,name='edit_profile'),
    path('change_password/',views.change_password,name='change_password'),
    
    path('contact/',views.contact,name='contact'),
    
    # path('return/<int:order_id>/<int:product_id>',views.initiate_return,name='return'),
]