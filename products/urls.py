from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='products'),  # This handles /products/
    path('category/<int:category_id>/', views.product_list, name='products_by_category'),
    path('<int:product_id>/', views.product_detail, name='product_detail'),
    path('contact/', views.contact, name='contact'),  # This handles /contact/
]