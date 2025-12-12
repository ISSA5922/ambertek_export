from django.contrib import admin
from .models import HomepageBanner, CategoryBanner, FeaturedProduct

@admin.register(HomepageBanner)
class HomepageBannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'display_order', 'created_at']
    list_editable = ['is_active', 'display_order']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'subtitle']

@admin.register(CategoryBanner)
class CategoryBannerAdmin(admin.ModelAdmin):
    list_display = ['category_name', 'is_active', 'display_order', 'created_at']
    list_editable = ['is_active', 'display_order']
    list_filter = ['is_active']
    search_fields = ['category_name', 'description']

@admin.register(FeaturedProduct)
class FeaturedProductAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'price', 'is_active', 'display_order', 'created_at']
    list_editable = ['price', 'is_active', 'display_order']
    list_filter = ['is_active', 'created_at']
    search_fields = ['product_name', 'description']