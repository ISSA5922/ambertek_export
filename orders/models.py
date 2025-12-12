# orders/models.py
from django.db import models
from django.utils import timezone
import uuid
from datetime import datetime
from django.contrib.auth.models import User

class Order(models.Model):
    ORDER_STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_METHODS = [
        ('cod', 'Cash on Delivery'),
        ('mobile', 'Mobile Money'),
        ('bank', 'Bank Transfer'),
    ]
    
    # Order number
    order_number = models.CharField(max_length=20, unique=True, blank=True)
    
    # User can be null for guest orders, but we'll require login for cart
   
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    customer_address = models.TextField()
    customer_city = models.CharField(max_length=50, blank=True)
    customer_region = models.CharField(max_length=50, blank=True)
    
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHODS, default='cod')
    payment_status = models.BooleanField(default=False)
    
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    estimated_delivery = models.DateField(null=True, blank=True)
    
    # Email notification fields
    confirmation_email_sent = models.BooleanField(default=False)
    confirmation_email_sent_at = models.DateTimeField(null=True, blank=True)
    admin_email_sent = models.BooleanField(default=False)
    admin_email_sent_at = models.DateTimeField(null=True, blank=True)
    
    # SMS/WhatsApp notification fields
    sms_sent = models.BooleanField(default=False)
    whatsapp_sent = models.BooleanField(default=False)
    customer_notified = models.BooleanField(default=False)
    admin_notified = models.BooleanField(default=False)
    
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Order #{self.order_number} - {self.customer_name}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate order number: ORD-YYYYMMDD-XXXX
            date_str = datetime.now().strftime('%Y%m%d')
            random_str = str(uuid.uuid4())[:4].upper()
            self.order_number = f"ORD-{date_str}-{random_str}"
        super().save(*args, **kwargs)
    
    def get_payment_method_display(self):
        """Get human-readable payment method"""
        for code, name in self.PAYMENT_METHODS:
            if code == self.payment_method:
                return name
        return self.payment_method
    
    class Meta:
        ordering = ['-created_at']


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product_id = models.IntegerField()
    product_name = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.product_name} x {self.quantity}"
    
    @property
    def item_total(self):
        return self.price * self.quantity
    
    @property
    def total(self):
        """Alias for item_total for email templates"""
        return self.item_total