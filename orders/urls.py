from django.urls import path

from . import views

app_name = 'orders'

urlpatterns = [
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/', views.cart_view, name='cart_view'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('cart/update_by_product/<int:product_id>/', views.update_cart_item_by_product,
         name='update_cart_item_by_product'),
    path('cart/remove_by_product/<int:product_id>/', views.remove_from_cart_by_product,
         name='remove_from_cart_by_product'),
]