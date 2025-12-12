from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'quantity', 'get_price_display', 'get_item_total_display']
    
    def get_price_display(self, obj):
        """Display formatted price"""
        return f"TZS {obj.price:,.0f}"
    get_price_display.short_description = 'Price'
    
    def get_item_total_display(self, obj):
        """Display formatted item total"""
        return f"TZS {obj.item_total:,.0f}"
    get_item_total_display.short_description = 'Total'
    
    # Optional: If you want to prevent adding new items
    def has_add_permission(self, request, obj=None):
        return False


class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer_name', 'customer_phone', 'get_total_amount_formatted', 
                   'get_payment_method_display', 'get_status_display', 'created_at', 'get_admin_actions']
    list_filter = ['status', 'payment_method', 'created_at', 'payment_status']
    search_fields = ['order_number', 'customer_name', 'customer_phone', 'customer_email']
    readonly_fields = ['order_number', 'created_at', 'updated_at', 'get_items_count']
    inlines = [OrderItemInline]
    date_hierarchy = 'created_at'
    list_per_page = 20
    
    # Admin actions for bulk operations
    actions = ['mark_as_processing', 'mark_as_shipped', 'mark_as_delivered', 'mark_as_cancelled']
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'status', 'created_at', 'updated_at', 'get_items_count')
        }),
        ('Customer Information', {
            'fields': ('customer_name', 'customer_phone', 'customer_email', 
                      'customer_address', 'customer_city', 'customer_region')
        }),
        ('Order Details', {
            'fields': ('total_amount', 'payment_method', 'payment_status', 'notes')
        }),
        ('Notifications', {
            'fields': ('confirmation_email_sent', 'confirmation_email_sent_at',
                      'admin_email_sent', 'admin_email_sent_at',
                      'sms_sent', 'whatsapp_sent', 'customer_notified', 'admin_notified'),
            'classes': ('collapse',)
        }),
    )
    
    def get_total_amount_formatted(self, obj):
        return f"TZS {obj.total_amount:,.0f}"
    get_total_amount_formatted.short_description = 'Total Amount'
    get_total_amount_formatted.admin_order_field = 'total_amount'
    
    def get_payment_method_display(self, obj):
        return dict(Order.PAYMENT_METHODS).get(obj.payment_method, obj.payment_method)
    get_payment_method_display.short_description = 'Payment Method'
    
    def get_status_display(self, obj):
        status_colors = {
            'pending': 'warning',
            'processing': 'info',
            'confirmed': 'primary',
            'shipped': 'success',
            'delivered': 'success',
            'cancelled': 'danger',
        }
        color = status_colors.get(obj.status, 'secondary')
        status_text = dict(Order.ORDER_STATUS).get(obj.status, obj.status)
        return format_html('<span class="badge bg-{}">{}</span>', color, status_text)
    get_status_display.short_description = 'Status'
    
    def get_admin_actions(self, obj):
        """Action buttons for each order"""
        view_url = reverse('admin:orders_order_change', args=[obj.id])
        delete_url = reverse('admin:orders_order_delete', args=[obj.id])
        return format_html(
            '<a href="{}" class="btn btn-sm btn-info me-1">View</a>'
            '<a href="{}" class="btn btn-sm btn-danger">Delete</a>',
            view_url, delete_url
        )
    get_admin_actions.short_description = 'Actions'
    
    def get_items_count(self, obj):
        return obj.items.count()
    get_items_count.short_description = 'Items Count'
    
    # Admin bulk actions
    def mark_as_processing(self, request, queryset):
        updated = queryset.update(status='processing')
        self.message_user(request, f'{updated} order(s) marked as processing.')
    mark_as_processing.short_description = "Mark selected as Processing"
    
    def mark_as_shipped(self, request, queryset):
        updated = queryset.update(status='shipped')
        self.message_user(request, f'{updated} order(s) marked as shipped.')
    mark_as_shipped.short_description = "Mark selected as Shipped"
    
    def mark_as_delivered(self, request, queryset):
        updated = queryset.update(status='delivered')
        self.message_user(request, f'{updated} order(s) marked as delivered.')
    mark_as_delivered.short_description = "Mark selected as Delivered"
    
    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} order(s) marked as cancelled.')
    mark_as_cancelled.short_description = "Mark selected as Cancelled"


# Register Order model
admin.site.register(Order, OrderAdmin)


# OrderItem Admin - only if you want to view/edit order items separately
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['get_order_number', 'product_name', 'quantity', 'get_price_display', 'get_item_total_display']
    list_filter = ['order__status']
    search_fields = ['product_name', 'order__order_number']
    readonly_fields = ['order', 'product_id', 'product_name', 'quantity', 'get_price_display', 'get_item_total_display']
    
    def get_order_number(self, obj):
        return obj.order.order_number
    get_order_number.short_description = 'Order Number'
    get_order_number.admin_order_field = 'order__order_number'
    
    def get_price_display(self, obj):
        return f"TZS {obj.price:,.0f}"
    get_price_display.short_description = 'Price'
    
    def get_item_total_display(self, obj):
        return f"TZS {obj.item_total:,.0f}"
    get_item_total_display.short_description = 'Item Total'
    
    # Prevent adding/deleting order items directly
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False