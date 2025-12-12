# cart/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from products.models import Product
from django.http import JsonResponse
import json
import logging

logger = logging.getLogger(__name__)


@login_required
def add_to_cart(request, product_id):
    """Add a product to the cart - REQUIRES LOGIN"""
    # Check if user is authenticated
    if not request.user.is_authenticated:
        current_language = request.session.get('ambertek_language', 'en')
        if current_language == 'sw':
            messages.warning(request, "Lazima uingie ili kuongeza bidhaa kwenye gari!")
        else:
            messages.warning(request, "You must login to add items to cart!")
        request.session['next_url'] = request.path
        return redirect('login')
    
    product = get_object_or_404(Product, id=product_id)
    
    # Get current language
    current_language = request.session.get('ambertek_language', 'en')
    
    # Initialize cart in session
    if 'cart' not in request.session:
        request.session['cart'] = {}
    
    cart = request.session['cart']
    
    # Get quantity from request
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
    else:
        # Also check GET for direct links
        quantity = int(request.GET.get('quantity', 1))
    
    # Add or update product in cart
    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] += quantity
        action = "updated"
    else:
        cart[str(product_id)] = {
            'name': product.name,
            'price': float(product.price),  # Convert to float
            'quantity': quantity,
            'image': product.image.url if product.image and hasattr(product.image, 'url') else '',
            'slug': product.slug if hasattr(product, 'slug') else product.name.lower().replace(' ', '-'),
        }
        action = "added"
    
    request.session['cart'] = cart
    request.session.modified = True
    
    # Success message based on language
    if current_language == 'sw':
        if action == "added":
            success_msg = f"{product.name} imeongezwa kwenye gari la ununuzi!"
        else:
            success_msg = f"{product.name} imesasishwa kwenye gari la ununuzi!"
    else:
        if action == "added":
            success_msg = f"{product.name} has been added to your cart!"
        else:
            success_msg = f"{product.name} has been updated in your cart!"
    
    messages.success(request, success_msg)
    
    # Check if it's an AJAX request
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': success_msg,
            'cart_count': len(cart),
            'cart_total': sum(item['quantity'] for item in cart.values())
        })
    
    # Decide where to redirect based on a parameter
    redirect_to = request.POST.get('redirect_to', request.GET.get('redirect_to', 'cart'))
    
    if redirect_to == 'product':
        return redirect('product_detail', product_id=product_id)
    elif redirect_to == 'product_list':
        return redirect('product_list')
    elif redirect_to == 'checkout':
        return redirect('checkout_view')
    else:
        # Default: redirect to cart
        return redirect('cart_detail')


@login_required
def cart_detail(request):
    """Display cart contents - REQUIRES LOGIN"""
    if not request.user.is_authenticated:
        current_language = request.session.get('ambertek_language', 'en')
        if current_language == 'sw':
            messages.warning(request, "Lazima uingie ili kuona gari lako la ununuzi!")
        else:
            messages.warning(request, "You must login to view your shopping cart!")
        request.session['next_url'] = '/cart/'
        return redirect('login')
    
    current_language = request.session.get('ambertek_language', 'en')
    
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0
    items_count = 0
    
    for product_id, item in cart.items():
        try:
            product = Product.objects.get(id=int(product_id))
            item_total = product.price * item['quantity']
            total += item_total
            items_count += item['quantity']
            cart_items.append({
                'product': product,
                'name': item['name'],
                'price': item['price'],
                'quantity': item['quantity'],
                'item_total': item_total,
                'image': item.get('image', ''),
                'slug': item.get('slug', '')
            })
        except (Product.DoesNotExist, ValueError):
            # Remove invalid items from cart
            if str(product_id) in cart:
                del cart[str(product_id)]
                request.session['cart'] = cart
                request.session.modified = True
    
    context = {
        'cart_items': cart_items,
        'cart_total': total,
        'items_count': items_count,
        'current_language': current_language,
        'cart_items_count': len(cart),
    }
    return render(request, 'cart/cart_detail.html', context)


@login_required
def remove_from_cart(request, product_id):
    """Remove a product from cart - REQUIRES LOGIN"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    product = get_object_or_404(Product, id=product_id)
    
    # Get current language
    current_language = request.session.get('ambertek_language', 'en')
    
    cart = request.session.get('cart', {})
    
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart'] = cart
        request.session.modified = True
        
        if current_language == 'sw':
            success_msg = f"{product.name} imeondolewa kwenye gari la ununuzi!"
        else:
            success_msg = f"{product.name} has been removed from your cart!"
        
        messages.success(request, success_msg)
    
    return redirect('cart_detail')


@login_required
def update_cart(request, product_id):
    """Update quantity of a product in cart - REQUIRES LOGIN"""
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': 'Login required',
            'redirect': '/accounts/login/'
        })
    
    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 1))
            product = get_object_or_404(Product, id=product_id)
            
            cart = request.session.get('cart', {})
            
            if quantity > 0:
                cart[str(product_id)]['quantity'] = quantity
            else:
                # If quantity is 0 or less, remove the item
                if str(product_id) in cart:
                    del cart[str(product_id)]
            
            request.session['cart'] = cart
            request.session.modified = True
            
            # Recalculate totals
            total = 0
            item_total = 0
            cart_count = 0
            
            for pid, item in cart.items():
                try:
                    p = Product.objects.get(id=int(pid))
                    if str(pid) == str(product_id):
                        item_total = p.price * quantity if quantity > 0 else 0
                    total += p.price * item['quantity']
                    cart_count += item['quantity']
                except (Product.DoesNotExist, ValueError):
                    pass
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'item_total': item_total,
                    'cart_total': total,
                    'cart_count': len(cart),
                    'items_count': cart_count
                })
            else:
                messages.success(request, f"Quantity updated for {product.name}")
            
        except (ValueError, KeyError) as e:
            logger.error(f"Error updating cart: {e}")
            messages.error(request, "Error updating quantity. Please try again.")
    
    return redirect('cart_detail')


@login_required
def clear_cart(request):
    """Clear all items from cart - REQUIRES LOGIN"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Get current language
    current_language = request.session.get('ambertek_language', 'en')
    
    if 'cart' in request.session:
        del request.session['cart']
        request.session.modified = True
        
        if current_language == 'sw':
            messages.success(request, "Gari la ununuzi limefutwa!")
        else:
            messages.success(request, "Your shopping cart has been cleared!")
    
    return redirect('cart_detail')


@login_required
def checkout_view(request):
    """Checkout view - requires login"""
    current_language = request.session.get('ambertek_language', 'en')
    
    # Check if cart is empty
    cart = request.session.get('cart', {})
    if not cart:
        if current_language == 'sw':
            messages.warning(request, "Gari lako la ununuzi ni tupu.")
        else:
            messages.warning(request, "Your shopping cart is empty.")
        return redirect('cart_detail')
    
    # Calculate cart total
    cart_items = []
    cart_total = 0
    items_count = 0
    
    for product_id, item in cart.items():
        try:
            product = Product.objects.get(id=int(product_id))
            item_total = product.price * item['quantity']
            cart_total += item_total
            items_count += item['quantity']
            
            cart_items.append({
                'product': product,
                'quantity': item['quantity'],
                'price': product.price,
                'item_total': item_total,
                'image': item.get('image', '')
            })
        except (Product.DoesNotExist, ValueError):
            continue
    
    # Get user profile for pre-filled data
    user = request.user
    profile = getattr(user, 'profile', None)
    
    # Pre-fill checkout form with user data
    initial_data = {}
    if user.is_authenticated:
        initial_data = {
            'customer_name': f"{user.first_name} {user.last_name}".strip() or user.username,
            'customer_email': user.email,
        }
        if profile:
            initial_data.update({
                'customer_phone': profile.phone_number or '',
                'shipping_address': profile.address or '',
                'customer_city': profile.city or '',
                'customer_region': profile.region or '',
            })
    
    # Get saved checkout data from session if any
    if 'checkout_data' in request.session:
        initial_data.update(request.session['checkout_data'])
    
    context = {
        'current_language': current_language,
        'cart_items': cart_items,
        'cart_total': cart_total,
        'items_count': items_count,
        'user': user,
        'profile': profile,
        'initial_data': initial_data,
    }
    
    return render(request, 'cart/checkout.html', context)


@login_required
def place_order_view(request):
    """Place order view - requires login"""
    if request.method != 'POST':
        return redirect('checkout_view')
    
    current_language = request.session.get('ambertek_language', 'en')
    
    # Get cart items
    cart = request.session.get('cart', {})
    if not cart:
        if current_language == 'sw':
            messages.error(request, "Gari la ununuzi ni tupu.")
        else:
            messages.error(request, "Shopping cart is empty.")
        return redirect('cart_detail')
    
    # Get form data
    customer_name = request.POST.get('customer_name', '').strip()
    customer_email = request.POST.get('customer_email', '').strip()
    customer_phone = request.POST.get('customer_phone', '').strip()
    shipping_address = request.POST.get('shipping_address', '').strip()
    customer_city = request.POST.get('customer_city', '').strip()
    customer_region = request.POST.get('customer_region', '').strip()
    payment_method = request.POST.get('payment_method', 'cod').strip()
    notes = request.POST.get('notes', '').strip()
    
    # Validate required fields
    required_fields = {
        'customer_name': customer_name,
        'customer_email': customer_email,
        'customer_phone': customer_phone,
        'shipping_address': shipping_address,
    }
    
    missing_fields = [field for field, value in required_fields.items() if not value]
    
    if missing_fields:
        if current_language == 'sw':
            messages.error(request, "Tafadhali jaza sehemu zote zinazohitajika.")
        else:
            messages.error(request, "Please fill in all required fields.")
        
        # Store form data in session
        request.session['checkout_data'] = {
            'customer_name': customer_name,
            'customer_email': customer_email,
            'customer_phone': customer_phone,
            'shipping_address': shipping_address,
            'customer_city': customer_city,
            'customer_region': customer_region,
            'payment_method': payment_method,
            'notes': notes,
        }
        return redirect('checkout_view')
    
    try:
        from orders.models import Order, OrderItem
        
        # Calculate total amount
        total_amount = 0
        for product_id, item in cart.items():
            try:
                product = Product.objects.get(id=int(product_id))
                total_amount += product.price * item['quantity']
            except (Product.DoesNotExist, ValueError):
                continue
        
        # Create order
        order = Order.objects.create(
            user=request.user,
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            customer_address=shipping_address,
            customer_city=customer_city,
            customer_region=customer_region,
            total_amount=total_amount,
            payment_method=payment_method,
            payment_status=False,  # Default to unpaid
            status='pending',
            notes=notes
        )
        
        # Create order items
        for product_id, item in cart.items():
            try:
                product = Product.objects.get(id=int(product_id))
                
                OrderItem.objects.create(
                    order=order,
                    product_id=product.id,
                    product_name=product.name,
                    quantity=item['quantity'],
                    price=product.price
                )
            except (Product.DoesNotExist, ValueError):
                continue
        
        # Clear cart
        request.session['cart'] = {}
        request.session.modified = True
        
        # Clear checkout data from session
        if 'checkout_data' in request.session:
            del request.session['checkout_data']
        
        # Success message
        if current_language == 'sw':
            messages.success(request, f"Asante! Agizo lako #{order.order_number} limepokelewa.")
        else:
            messages.success(request, f"Thank you! Your order #{order.order_number} has been received.")
        
        return redirect('order_confirmation', order_id=order.id)
        
    except Exception as e:
        logger.error(f"Order placement error: {e}")
        if current_language == 'sw':
            messages.error(request, "Hitilafu imetokea wakati wa kuweka agizo. Tafadhali jaribu tena.")
        else:
            messages.error(request, "An error occurred while placing order. Please try again.")
        return redirect('checkout_view')