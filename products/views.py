# products/views.py
from django.shortcuts import render, get_object_or_404
from .models import Product, Category
from home.models import CategoryBanner, HomepageBanner, FeaturedProduct

def home(request):
    # Get current language from session or cookie
    current_language = request.session.get('ambertek_language') or request.COOKIES.get('ambertek_language', 'en')
    
    # Get active banners and content
    homepage_banners = HomepageBanner.objects.filter(is_active=True)
    category_banners = CategoryBanner.objects.filter(is_active=True)
    featured_products = FeaturedProduct.objects.filter(is_active=True)
    
    context = {
        'cart_items_count': 0,
        'current_language': current_language,
        'homepage_banners': homepage_banners,
        'category_banners': category_banners,
        'featured_products': featured_products,
    }
    return render(request, 'index.html', context)

def product_list(request, category_id=None):
    current_language = request.session.get('ambertek_language') or request.COOKIES.get('ambertek_language', 'en')
    
    # Get all active products
    products = Product.objects.filter(available=True)
    categories = Category.objects.all()
    
    active_category = None
    active_category_name = "All Products"
    
    # Filter by category if specified
    if category_id:
        products = products.filter(category_id=category_id)
        active_category = category_id
        category_obj = get_object_or_404(Category, id=category_id)
        active_category_name = category_obj.name
        # Update name for Swahili
        if current_language == 'sw':
            active_category_name = category_obj.name
    elif current_language == 'sw':
        active_category_name = "Bidhaa Zote"
    
    context = {
        'products': products,
        'categories': categories,
        'active_category': active_category,
        'active_category_name': active_category_name,
        'current_language': current_language,
        'cart_items_count': 0,
    }
    return render(request, 'products/product_list.html', context)

def product_detail(request, product_id):
    current_language = request.session.get('ambertek_language') or request.COOKIES.get('ambertek_language', 'en')
    
    product = get_object_or_404(Product, id=product_id)
    
    context = {
        'product': product,
        'current_language': current_language,
        'cart_items_count': 0,
    }
    return render(request, 'products/product_detail.html', context)

def contact(request):
    current_language = request.session.get('ambertek_language') or request.COOKIES.get('ambertek_language', 'en')
    
    context = {
        'current_language': current_language,
        'cart_items_count': 0,
    }
    return render(request, 'contact.html', context)