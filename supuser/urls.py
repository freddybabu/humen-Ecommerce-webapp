from django.urls import path
from .import views

urlpatterns = [
    path('',views.supuser,name='supuser'),
    path('manage/',views.usermanage,name='manage'),
    path('manage/block/<int:id>/',views.block_user, name='block_user'),
    path('manage/unblock/<int:id>/',views.unblock_user, name='unblock_user'),
    
    path('caregotys/', views.categorymanage, name='categorymanage'),
    path('Category/add/', views.add_category, name='add_category'),
    path('Category/del/<int:id>', views.del_category, name='del_category'),
    
    path('productmanage/',views.productmanage,name="productmanage"),
    path('productmanage/add/',views.add_product,name="add_product"),
    path('productmanage/edit/<int:id>',views.edit_product,name="edit_product"),
    path('productmanage/del/<int:id>', views.del_product, name='del_product'),
    
    path('Variationmanage/',views.Variationmanage,name="Variationmanage"),
    path('Variationmanage/add',views.add_variation,name="add_variation"),
    path('Variationmanage/edit<int:id>',views.edit_variation,name="edit_variation"),
    path('Variationmange/delete<int:id>',views.delete_variation,name="delete_variation"),
    
    path('orderslist',views.orderslist,name="orderslist"),
    path('orderslist/<int:order_id>',views.order_details_admin,name="order_details_admin"),
    path('change_status/<int:order_id>',views.change_status,name="change_status"),
    
    path('coupen_manage',views.coupen_manage,name='coupen_manage'),
    path('add_coupens',views.add_coupens,name="add_coupens"),
    path('del_coupens/<int:id>',views.del_coupens,name="del_coupens"),
    path('edit_coupens/<int:id>',views.edit_coupens,name="edit_coupens"),
    
    path('add_order_filter',views.add_order_filter,name="add_order_filter"),
]