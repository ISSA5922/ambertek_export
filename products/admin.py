from django.contrib import admin
from .models import Category, Product, ProductImage

# Inline for Product Images
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Number of empty forms to show
    max_num = 5  # Maximum images per product

# Category Admin
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'id']
    search_fields = ['name']
    list_per_page = 20

# Product Admin
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # What to display in the list view
    list_display = ['name', 'category', 'price', 'available', 'created_at']
    
    # Filters on the right side
    list_filter = ['category', 'available', 'created_at']
    
    # Search functionality
    search_fields = ['name', 'description']
    
    # Inline images
    inlines = [ProductImageInline]
    
    # Fields to display in edit form
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'category', 'price', 'available')
        }),
        ('Description', {
            'fields': ('description',)
        }),
        ('Media Files', {
            'fields': ('image', 'video')
        }),
    )
    
    # Ordering - newest first
    ordering = ['-created_at']
    
    # Pagination
    list_per_page = 25
    
    # Date hierarchy for filtering by date
    date_hierarchy = 'created_at'

# ProductImage Admin
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'id', 'caption']
    list_filter = ['product']
    search_fields = ['product__name', 'caption']
    list_per_page = 20