# ambertek/urls.py
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponseRedirect

# Import views from your apps
from products import views as product_views

# Import cart views
try:
    from cart import views as cart_views
except ImportError:
    # If cart app doesn't exist yet
    cart_views = None

# Import order views
try:
    from orders import views as order_views
except ImportError:
    # If orders app doesn't exist yet
    order_views = None

# Import account views
try:
    from accounts import views as account_views
except ImportError:
    # If accounts app doesn't exist yet
    account_views = None

def get_current_language(request):
    return request.session.get('ambertek_language') or request.COOKIES.get('ambertek_language', 'en')

def set_current_language(request, language_code):
    if language_code in ['en', 'sw']:
        request.session['ambertek_language'] = language_code
        response = HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        response.set_cookie('ambertek_language', language_code)
        return response
    return HttpResponseRedirect('/')

def home_view(request):
    current_language = get_current_language(request)
    
    from home.models import HomepageBanner, CategoryBanner, FeaturedProduct
    
    homepage_banners = HomepageBanner.objects.filter(is_active=True)
    category_banners = CategoryBanner.objects.filter(is_active=True)
    featured_products = FeaturedProduct.objects.filter(is_active=True)
    
    context = {
        'cart_items_count': request.session.get('cart_items_count', 0),
        'current_language': current_language,
        'homepage_banners': homepage_banners,
        'category_banners': category_banners,
        'featured_products': featured_products,
    }
    return render(request, 'index.html', context)

def set_language(request, language_code):
    return set_current_language(request, language_code)

def contact_view(request):
    current_language = get_current_language(request)
    context = {
        'current_language': current_language,
        'cart_items_count': request.session.get('cart_items_count', 0),
    }
    return render(request, 'contact.html', context)

def products_view(request, category_id=None):
    current_language = get_current_language(request)
    
    from products.models import Product, Category
    products = Product.objects.filter(available=True)
    categories = Category.objects.all()
    
    active_category = None
    active_category_name = "All Products"
    
    # Filter by category if category_id is provided
    if category_id:
        from django.shortcuts import get_object_or_404
        products = products.filter(category_id=category_id)
        active_category = category_id
        category_obj = get_object_or_404(Category, id=category_id)
        active_category_name = category_obj.name
    
    # Update name for Swahili
    if current_language == 'sw' and not category_id:
        active_category_name = "Bidhaa Zote"
    
    context = {
        'products': products,
        'categories': categories,
        'current_language': current_language,
        'cart_items_count': request.session.get('cart_items_count', 0),
        'active_category': active_category,
        'active_category_name': active_category_name,
    }
    return render(request, 'products/product_list.html', context)

# Placeholder functions if apps don't exist
def placeholder_function(request, *args, **kwargs):
    from django.http import HttpResponseRedirect
    from django.contrib import messages
    messages.info(request, "This functionality is coming soon!")
    return HttpResponseRedirect('/products/')

# Helper to get views safely
def get_view(app_views, view_name):
    """Helper to get view or placeholder"""
    if app_views and hasattr(app_views, view_name):
        return getattr(app_views, view_name)
    return placeholder_function

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Home & Language
    path('', home_view, name='home'),
    path('language/<str:language_code>/', set_language, name='set_language'),
    
    # Products URLs
    path('products/', products_view, name='products'),
    path('products/category/<int:category_id>/', products_view, name='products_by_category'),
    path('products/<int:product_id>/', 
         get_view(product_views, 'product_detail'), 
         name='product_detail'),
    
    # Contact
    path('contact/', contact_view, name='contact'),
    
    # Accounts URLs
    path('accounts/', include('accounts.urls')),
    
    # Cart URLs
    path('cart/add/<int:product_id>/', get_view(cart_views, 'add_to_cart'), name='add_to_cart'),
    path('cart/', get_view(cart_views, 'cart_detail'), name='cart_detail'),
    path('cart/remove/<int:product_id>/', get_view(cart_views, 'remove_from_cart'), name='remove_from_cart'),
    path('cart/update/<int:product_id>/', get_view(cart_views, 'update_cart'), name='update_cart'),
    path('cart/clear/', get_view(cart_views, 'clear_cart'), name='clear_cart'),
    
    # Order URLs
    path('checkout/', get_view(order_views, 'checkout'), name='checkout'),
    path('place-order/', get_view(order_views, 'place_order'), name='place_order'),
    path('order/confirmation/<int:order_id>/', get_view(order_views, 'order_confirmation'), name='order_confirmation'),
    path('order/success/<int:order_id>/', get_view(order_views, 'order_success'), name='order_success'),
    path('order/track/<str:order_number>/', get_view(order_views, 'order_track'), name='order_track'),
    
    # Email test URLs
    path('test-email/', get_view(order_views, 'test_email'), name='test_email'),
    path('test-email-simple/', get_view(order_views, 'test_email_simple'), name='test_email_simple'),
    path('test-complete-email/', get_view(order_views, 'test_complete_email'), name='test_complete_email'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)