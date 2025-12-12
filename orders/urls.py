from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('create/', views.create_order, name='create_order'),
    path('success/<int:order_id>/', views.order_success, name='order_success'),
    path('track/', views.track_order, name='track_order'),
    path('checkout/', login_required(views.checkout_view), name='checkout'),
    path('place-order/', login_required(views.place_order_view), name='place_order'),
    path('order-confirmation/<int:order_id>/', login_required(views.order_confirmation_view), name='order_confirmation'),
    path('my-orders/', login_required(views.my_orders_view), name='my_orders'),
    path('order-detail/<int:order_id>/', login_required(views.order_detail_view), name='order_detail'),
]