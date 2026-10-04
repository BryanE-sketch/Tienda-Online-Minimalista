from django.urls import path

from . import views

app_name = 'orders'

urlpatterns = [
    path('carrito/', views.cart_detail, name='cart_detail'),
    path('carrito/anadir/<int:product_id>/', views.cart_add, name='cart_add'),
    path('carrito/actualizar/<int:product_id>/', views.cart_update, name='cart_update'),
    path('carrito/quitar/<int:product_id>/', views.cart_remove, name='cart_remove'),
]