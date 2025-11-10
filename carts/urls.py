from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_cart, name='add_cart'),
    path('remove-from-cart/<int:product_id>/', views.remove_cart, name='remove_cart'),
    path('delete-from-cart/<int:product_id>/', views.delete_cart_item, name='delete_cart_item'),
]