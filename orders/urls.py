from django.urls import path
from .import views

urlpatterns = [
    path('place_order/', views.place_order, name='place_order'),
    path('payments/',views.payments,name='payments'),
    path('order_complete/',views.order_complete,name='order_complete'),
    path('cash_on_delivery',views.cash_on_delivery,name='cash_on_delivery'),
    # path('confirm_order',views.confirm_order,name="confirm_order"),
    
    path('return/<int:order_id>/<int:product_id>',views.initiate_return,name='return'),
    
]
