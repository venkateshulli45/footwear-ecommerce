from django.urls import path
from . import views

urlpatterns = [
    path('women/', views.wft, name='wft'),
    path('men/', views.mft, name='mft'),
    path('kids/', views.kft, name='kft'),  
    path("confirm_purchase/", views.confirm_purchase, name="confirm_purchase"),
    path("purchase_confirmation/", views.purchase_confirmation, name="purchase_confirmation"),
    path("order_history/", views.order_history, name="order_history"),
    path("add_to_bag/", views.add_to_bag, name="add_to_bag"),
    path("view_bag/", views.view_bag, name="view_bag"),
    path("remove_from_bag/<int:item_id>/", views.remove_from_bag, name="remove_from_bag"),
]