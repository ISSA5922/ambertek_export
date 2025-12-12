# utils/email_service.py - Fix the logging issue
import logging
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.conf import settings

logger = logging.getLogger(__name__)

class EmailService:
    
    def __init__(self):
        print("[EmailService] Initialized")
    
    def send_order_confirmation(self, order):
        """Send order confirmation email to customer"""
        print(f"[EmailService] Sending order confirmation to: {order.customer_email}")
        
        try:
            if not order.customer_email:
                print("[EmailService] No email address provided")
                return False
            
            # Check if email settings exist
            if not hasattr(settings, 'EMAIL_BACKEND'):
                print("[EmailService] EMAIL_BACKEND not set in settings")
                return False
            
            # Get order items
            from orders.models import OrderItem
            order_items = OrderItem.objects.filter(order=order)
            
            # Prepare simple email
            subject = f"Order Confirmation #{order.order_number} - Ambertek Exports"
            
            message = f"""
Order Confirmation #{order.order_number}

Dear {order.customer_name},

Thank you for your order with Ambertek Exports!

ORDER DETAILS:
-------------
Order Number: {order.order_number}
Order Date: {order.created_at.strftime('%B %d, %Y')}
Total Amount: TZS {order.total_amount:,.0f}
Payment Method: {order.get_payment_method_display()}
Status: {order.status.title()}

SHIPPING ADDRESS:
-----------------
{order.customer_name}
{order.customer_address}
{order.customer_city}, {order.customer_region}
Phone: {order.customer_phone}

ORDER ITEMS:
------------
"""
            
            for item in order_items:
                message += f"- {item.product_name} x {item.quantity}: TZS {item.price * item.quantity:,.0f}\n"
            
            message += f"""
Total: TZS {order.total_amount:,.0f}

DELIVERY INFORMATION:
---------------------
Estimated Delivery: {order.estimated_delivery.strftime('%B %d, %Y') if order.estimated_delivery else '3-5 business days'}

CONTACT US:
-----------
Phone: +254 7XX XXX XXX
Email: support@ambertek.com
Hours: Monday-Friday, 9AM-5PM EAT

Thank you for choosing Ambertek Exports!

Best regards,
Ambertek Exports Team
"""
            
            # Send email
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'Ambertek Exports <noreply@ambertek.com>')
            
            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=[order.customer_email],
                fail_silently=False,
            )
            
            print(f"[EmailService] Order confirmation sent to {order.customer_email}")
            return True
            
        except Exception as e:
            print(f"[EmailService] Error: {e}")
            return False
    
    def send_admin_notification(self, order):
        """Send order notification to admin"""
        try:
            admin_email = getattr(settings, 'ORDER_NOTIFICATION_EMAIL', None)
            if not admin_email:
                print("[EmailService] No admin email configured")
                return False
            
            subject = f"New Order: #{order.order_number}"
            
            message = f"""
NEW ORDER NOTIFICATION
======================

Order #{order.order_number}
Customer: {order.customer_name}
Phone: {order.customer_phone}
Email: {order.customer_email or 'Not provided'}
Total: TZS {order.total_amount:,.0f}
Payment Method: {order.get_payment_method_display()}

SHIPPING ADDRESS:
{order.customer_address}
{order.customer_city}, {order.customer_region}

ORDER ITEMS:
"""
            
            from orders.models import OrderItem
            order_items = OrderItem.objects.filter(order=order)
            
            for item in order_items:
                message += f"- {item.product_name} x {item.quantity}: TZS {item.price * item.quantity:,.0f}\n"
            
            message += f"""
TOTAL: TZS {order.total_amount:,.0f}

CUSTOMER NOTES:
{order.notes or 'No notes provided'}

---
View order in admin: {getattr(settings, 'SITE_URL', 'http://localhost:8000')}/admin/orders/order/{order.id}/
"""
            
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'Ambertek Exports <noreply@ambertek.com>')
            
            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=[admin_email],
                fail_silently=False,
            )
            
            print(f"[EmailService] Admin notification sent for order #{order.order_number}")
            return True
            
        except Exception as e:
            print(f"[EmailService] Admin notification error: {e}")
            return False

# Create global instance
email_service = EmailService()