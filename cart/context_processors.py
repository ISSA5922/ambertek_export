from django.db.models import Count
from .models import CartItem

def cart_items_count(request):
    """
    Context processor to make cart items count available in all templates
    """
    if not request.session.session_key:
        return {'cart_items_count': 0}
    
    try:
        count = CartItem.objects.filter(session_key=request.session.session_key).count()
        return {'cart_items_count': count}
    except:
        # If there's any error (like table doesn't exist yet), return 0
        return {'cart_items_count': 0}

# cart/context_processors.py
def cart_items_count(request):
    """Add cart items count to all templates"""
    cart = request.session.get('cart', {})
    count = 0
    for item in cart.values():
        count += item.get('quantity', 0)
    return {'cart_items_count': count}