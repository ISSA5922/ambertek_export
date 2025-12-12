from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse

class CartAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check if user is trying to access checkout without login
        if request.path.startswith('/cart/checkout') or request.path.startswith('/orders/'):
            if not request.user.is_authenticated:
                # Store the intended URL
                request.session['next_url'] = request.path
                
                # Get current language
                current_language = request.session.get('ambertek_language', 'en')
                
                # Add message
                if current_language == 'sw':
                    messages.warning(request, "Lazima uingie ili kuweka agizo.")
                else:
                    messages.warning(request, "You must login to place an order.")
                
                # Redirect to login
                return redirect(reverse('login'))
        
        response = self.get_response(request)
        return response