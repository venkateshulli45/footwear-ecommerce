from django.urls import path

from . import views

urlpatterns = [
    path('women/', views.wft, name='wft'),
    path('men/', views.mft, name='mft'),
    path('kids/', views.kft, name='kft'),
    path('product/<str:category>/<int:product_id>/', views.product_detail, name='product_detail'),
    path('add_to_bag/', views.add_to_bag, name='add_to_bag'),
    path('view_bag/', views.view_bag, name='view_bag'),
    path('remove_from_bag/<int:item_id>/', views.remove_from_bag, name='remove_from_bag'),
    path('update_bag/<int:item_id>/', views.update_bag_quantity, name='update_bag_quantity'),
    path('checkout/', views.checkout, name='checkout'),
    path('order_confirmation/', views.order_confirmation, name='order_confirmation'),
    path('order_history/', views.order_history, name='order_history'),
    path('cancel_order/<int:order_id>/', views.cancel_order, name='cancel_order'),
]
