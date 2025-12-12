from django.db import models

class HomepageBanner(models.Model):
    title = models.CharField(max_length=200, help_text="Title for the banner")
    subtitle = models.CharField(max_length=300, blank=True, help_text="Subtitle or description")
    image = models.ImageField(upload_to='homepage/banners/', help_text="Recommended size: 1200x600 pixels")
    is_active = models.BooleanField(default=True, help_text="Show this banner on homepage")
    display_order = models.PositiveIntegerField(default=0, help_text="Order in which banners are displayed")
    button_text = models.CharField(max_length=50, default="Shop Now", blank=True)
    button_link = models.CharField(max_length=200, default="/products/", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['display_order', '-created_at']
        verbose_name = "Homepage Banner"
        verbose_name_plural = "Homepage Banners"
    
    def __str__(self):
        return self.title

class CategoryBanner(models.Model):
    category_name = models.CharField(max_length=100, help_text="Name of the category")
    description = models.TextField(help_text="Category description")
    image = models.ImageField(upload_to='homepage/categories/', help_text="Recommended size: 400x300 pixels")
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['display_order']
        verbose_name = "Category Banner"
        verbose_name_plural = "Category Banners"
    
    def __str__(self):
        return self.category_name

class FeaturedProduct(models.Model):
    product_name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='homepage/featured/')
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['display_order']
        verbose_name = "Featured Product"
        verbose_name_plural = "Featured Products"
    
    def __str__(self):
        return self.product_name