# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect
from django.utils.translation import gettext as _
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)


def is_safe_url(url, allowed_hosts=None):
    """
    Check if a URL is safe for redirect.
    Return the safe URL or None.
    """
    if url is None:
        return None
    
    # Parse the URL
    parsed_url = urlparse(url)
    
    # Check if URL is relative (safe)
    if not parsed_url.netloc:
        return url
    
    # Check against allowed hosts (optional)
    if allowed_hosts:
        if parsed_url.netloc in allowed_hosts:
            return url
    
    # Default: only allow relative URLs
    return None


@csrf_protect
def login_view(request):
    """
    Handle user login with CSRF protection and proper redirects
    """
    # Get current language
    current_language = request.session.get('ambertek_language', 'en')
    
    # If user is already logged in, redirect to home
    if request.user.is_authenticated:
        if current_language == 'sw':
            messages.info(request, "Tayari umeingia.")
        else:
            messages.info(request, "You are already logged in.")
        
        # Get redirect URL from various sources
        redirect_url = request.GET.get('next') or request.POST.get('next') or \
                      request.session.get('next_url', 'home')
        
        # Validate redirect URL
        safe_redirect = is_safe_url(redirect_url)
        if safe_redirect:
            return redirect(safe_redirect)
        return redirect('home')
    
    # Handle POST request
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        remember_me = request.POST.get('remember_me') == 'on'
        
        # Check if input is email or username
        if '@' in username:
            try:
                user_obj = User.objects.get(email=username)
                username = user_obj.username
            except User.DoesNotExist:
                username = None
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Login successful
            login(request, user)
            
            # Set session expiration based on remember me
            if remember_me:
                # 2 weeks expiration
                request.session.set_expiry(1209600)
            else:
                # Session expires when browser closes
                request.session.set_expiry(0)
            
            # Create profile if it doesn't exist
            if not hasattr(user, 'profile'):
                from .models import UserProfile
                UserProfile.objects.get_or_create(user=user)
            
            # Success message
            if current_language == 'sw':
                messages.success(request, f"Karibu tena, {user.username}!")
            else:
                messages.success(request, f"Welcome back, {user.username}!")
            
            # Handle redirect after login
            # Priority: 1. POST next, 2. GET next, 3. Session next_url, 4. Default home
            redirect_url = request.POST.get('next') or request.GET.get('next') or \
                          request.session.get('next_url', 'home')
            
            # Clear stored redirect URL from session
            if 'next_url' in request.session:
                del request.session['next_url']
            
            # Validate and redirect
            safe_redirect = is_safe_url(redirect_url)
            if safe_redirect:
                return redirect(safe_redirect)
            return redirect('home')
            
        else:
            # Authentication failed
            if current_language == 'sw':
                messages.error(request, "Jina la mtumiaji au nywila sio sahihi.")
            else:
                messages.error(request, "Invalid username or password.")
    
    # GET request - show login form
    # Store the redirect URL in session for POST requests
    next_url = request.GET.get('next', '')
    if next_url:
        request.session['next_url'] = next_url
    
    context = {
        'current_language': current_language,
        'next_url': next_url,
    }
    return render(request, 'accounts/login.html', context)


@csrf_protect
def register_view(request):
    """
    Handle user registration with CSRF protection and proper redirects
    """
    # Get current language
    current_language = request.session.get('ambertek_language', 'en')
    
    # If user is already logged in, redirect to home
    if request.user.is_authenticated:
        if current_language == 'sw':
            messages.info(request, "Tayari umeingia.")
        else:
            messages.info(request, "You are already logged in.")
        return redirect('home')
    
    # Handle POST request
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password1 = request.POST.get('password1', '').strip()
        password2 = request.POST.get('password2', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        agree_terms = request.POST.get('agree_terms') == 'on'
        
        errors = []
        
        # Validation
        if not all([username, email, password1, password2]):
            if current_language == 'sw':
                errors.append("Tafadhali jaza sehemu zote zinazohitajika.")
            else:
                errors.append("Please fill in all required fields.")
        
        if password1 != password2:
            if current_language == 'sw':
                errors.append("Nywila hazifanani.")
            else:
                errors.append("Passwords do not match.")
        
        if len(password1) < 8:
            if current_language == 'sw':
                errors.append("Nywila lazima iwe na angalau herufi 8.")
            else:
                errors.append("Password must be at least 8 characters.")
        
        if not agree_terms:
            if current_language == 'sw':
                errors.append("Lazima ukubali masharti na mashariti.")
            else:
                errors.append("You must agree to the terms and conditions.")
        
        if User.objects.filter(username=username).exists():
            if current_language == 'sw':
                errors.append("Jina la mtumiaji tayari limechukuliwa.")
            else:
                errors.append("Username already taken.")
        
        if User.objects.filter(email=email).exists():
            if current_language == 'sw':
                errors.append("Barua pepe tayari imesajiliwa.")
            else:
                errors.append("Email already registered.")
        
        # If no errors, create user
        if not errors:
            try:
                # Create user
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password1,
                    first_name=first_name,
                    last_name=last_name
                )
                
                # Create user profile with phone number
                from .models import UserProfile
                profile, created = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={'phone_number': phone_number}
                )
                
                # Update phone number if profile already existed
                if not created:
                    profile.phone_number = phone_number
                    profile.save()
                
                # Log the user in
                login(request, user)
                
                # Success message
                if current_language == 'sw':
                    messages.success(request, f"Akaunti yako imeundwa kikamilifu! Karibu, {user.username}!")
                else:
                    messages.success(request, f"Your account has been created successfully! Welcome, {user.username}!")
                
                # Handle redirect after registration
                redirect_url = request.POST.get('next') or request.GET.get('next') or \
                              request.session.get('next_url', 'home')
                
                # Clear stored redirect URL from session
                if 'next_url' in request.session:
                    del request.session['next_url']
                
                # Validate and redirect
                safe_redirect = is_safe_url(redirect_url)
                if safe_redirect:
                    return redirect(safe_redirect)
                return redirect('home')
                
            except Exception as e:
                logger.error(f"Registration error: {e}")
                if current_language == 'sw':
                    errors.append("Hitilafu imetokea wakati wa kujisajili.")
                else:
                    errors.append("An error occurred during registration.")
                for error in errors:
                    messages.error(request, error)
        else:
            # Show errors
            for error in errors:
                messages.error(request, error)
    
    # GET request - show registration form
    # Store the redirect URL in session for POST requests
    next_url = request.GET.get('next', '')
    if next_url:
        request.session['next_url'] = next_url
    
    context = {
        'current_language': current_language,
        'next_url': next_url,
    }
    return render(request, 'accounts/register.html', context)


@login_required
def logout_view(request):
    """
    Handle user logout with optional redirect
    """
    current_language = request.session.get('ambertek_language', 'en')
    username = request.user.username
    
    # Get redirect URL if provided
    redirect_url = request.GET.get('next', 'home')
    safe_redirect = is_safe_url(redirect_url)
    
    logout(request)
    
    if current_language == 'sw':
        messages.success(request, f"Umetoka kwenye akaunti yako. Kwaheri, {username}!")
    else:
        messages.success(request, f"You have been logged out. Goodbye, {username}!")
    
    if safe_redirect:
        return redirect(safe_redirect)
    return redirect('home')


@login_required
def profile_view(request):
    """
    Display user profile
    """
    current_language = request.session.get('ambertek_language', 'en')
    user = request.user
    
    # Ensure profile exists
    if not hasattr(user, 'profile'):
        from .models import UserProfile
        UserProfile.objects.get_or_create(user=user)
        user.refresh_from_db()
    
    context = {
        'current_language': current_language,
        'user': user,
        'profile': user.profile,
    }
    return render(request, 'accounts/profile.html', context)


@csrf_protect
@login_required
def edit_profile_view(request):
    """
    Edit user profile
    """
    current_language = request.session.get('ambertek_language', 'en')
    user = request.user
    
    # Ensure profile exists
    if not hasattr(user, 'profile'):
        from .models import UserProfile
        UserProfile.objects.get_or_create(user=user)
        user.refresh_from_db()
    
    if request.method == 'POST':
        # Update user info
        user.first_name = request.POST.get('first_name', user.first_name).strip()
        user.last_name = request.POST.get('last_name', user.last_name).strip()
        user_email = request.POST.get('email', user.email).strip().lower()
        
        # Update profile info
        user.profile.phone_number = request.POST.get('phone_number', user.profile.phone_number).strip()
        user.profile.address = request.POST.get('address', user.profile.address).strip()
        user.profile.city = request.POST.get('city', user.profile.city).strip()
        user.profile.region = request.POST.get('region', user.profile.region).strip()
        
        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            user.profile.profile_picture = request.FILES['profile_picture']
        
        # Validate email uniqueness (excluding current user)
        if user_email != user.email and User.objects.filter(email=user_email).exists():
            if current_language == 'sw':
                messages.error(request, "Barua pepe tayari inatumiwa na mtu mwingine.")
            else:
                messages.error(request, "Email is already used by another user.")
        else:
            try:
                user.email = user_email
                user.save()
                user.profile.save()
                
                if current_language == 'sw':
                    messages.success(request, "Wasifu wako umesasishwa kikamilifu!")
                else:
                    messages.success(request, "Your profile has been updated successfully!")
                
                return redirect('profile')
            except Exception as e:
                logger.error(f"Profile update error: {e}")
                if current_language == 'sw':
                    messages.error(request, "Hitilafu imetokea wakati wa kusasisha wasifu.")
                else:
                    messages.error(request, "An error occurred while updating profile.")
    
    context = {
        'current_language': current_language,
        'user': user,
        'profile': user.profile,
    }
    return render(request, 'accounts/edit_profile.html', context)


@csrf_protect
@login_required
def change_password_view(request):
    """
    Change user password
    """
    current_language = request.session.get('ambertek_language', 'en')
    
    if request.method == 'POST':
        old_password = request.POST.get('old_password', '').strip()
        new_password1 = request.POST.get('new_password1', '').strip()
        new_password2 = request.POST.get('new_password2', '').strip()
        
        # Check if old password is correct
        if not request.user.check_password(old_password):
            if current_language == 'sw':
                messages.error(request, "Nywila ya zamani sio sahihi.")
            else:
                messages.error(request, "Old password is incorrect.")
            return redirect('change_password')
        
        # Check if new passwords match
        if new_password1 != new_password2:
            if current_language == 'sw':
                messages.error(request, "Nywila mpya hazifanani.")
            else:
                messages.error(request, "New passwords do not match.")
            return redirect('change_password')
        
        # Check password strength
        if len(new_password1) < 8:
            if current_language == 'sw':
                messages.error(request, "Nywila mpya lazima iwe na angalau herufi 8.")
            else:
                messages.error(request, "New password must be at least 8 characters.")
            return redirect('change_password')
        
        # Change password
        try:
            request.user.set_password(new_password1)
            request.user.save()
            
            # Re-authenticate user with new password
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, request.user)
            
            if current_language == 'sw':
                messages.success(request, "Nywila yako imebadilishwa kikamilifu!")
            else:
                messages.success(request, "Your password has been changed successfully!")
            
            return redirect('profile')
        except Exception as e:
            logger.error(f"Password change error: {e}")
            if current_language == 'sw':
                messages.error(request, "Hitilafu imetokea wakati wa kubadilisha nywila.")
            else:
                messages.error(request, "An error occurred while changing password.")
    
    context = {
        'current_language': current_language,
    }
    return render(request, 'accounts/change_password.html', context)


def password_reset_request(request):
    """
    Handle password reset request
    """
    current_language = request.session.get('ambertek_language', 'en')
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        
        try:
            user = User.objects.get(email=email)
            # Here you would send a password reset email
            # For now, just show a message
            if current_language == 'sw':
                messages.info(request, f"Ujumbe wa kuweka upya nywila umetumwa kwa {email}.")
            else:
                messages.info(request, f"Password reset email sent to {email}.")
        except User.DoesNotExist:
            if current_language == 'sw':
                messages.error(request, "Barua pepe hii haijasajiliwa.")
            else:
                messages.error(request, "This email is not registered.")
    
    context = {
        'current_language': current_language,
    }
    return render(request, 'accounts/password_reset.html', context)