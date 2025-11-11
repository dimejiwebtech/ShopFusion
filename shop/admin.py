from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'slug')
    prepopulated_fields = {'slug': ('category_name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'slug', 'price', 'stock', 'is_available', 'display_categories')
    list_filter = ('is_available', 'created_date', 'modified_date',)
    search_fields = ('product_name',)
    prepopulated_fields = {'slug': ('product_name',)}
    filter_horizontal = ('category',)

    def display_categories(self, obj):
        return ", ".join([cat.category_name for cat in obj.category.all()])
    display_categories.short_description = 'Categories'

    fieldsets = [
        ('Basic Information', {
            'fields': ('product_name', 'slug', 'price', 'stock', 'product_content', 'product_image', 'short_description')
        }),
        ('Products Settings', {
            'fields': ('category', 'is_available'),
        }),
        ('SEO', {
            'fields': ('seo_description', 'seo_keywords'),
            'classes': ('collapse',)
        }),
    ]