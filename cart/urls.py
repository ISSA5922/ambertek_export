

# cart/urls.py
from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    path('', login_required(views.cart_detail), name='cart_detail'),
    path('add/<int:product_id>/', login_required(views.add_to_cart), name='add_to_cart'),
    path('remove/<int:product_id>/', login_required(views.remove_from_cart), name='remove_from_cart'),
    path('update/<int:product_id>/', login_required(views.update_cart), name='update_cart'),
    path('clear/', login_required(views.clear_cart), name='clear_cart'),
    path('checkout/', login_required(views.checkout_view), name='checkout_view'),
    path('place-order/', login_required(views.place_order_view), name='place_order'),
    path('checkout/', views.checkout_view, name='checkout_view'),
]