from django.contrib import admin
from .models import Payment, Order, OrderedProduct


class OrderedProductInline(admin.TabularInline):
    model = OrderedProduct
    readonly_fields = ('payment', 'user', 'product', 'quantity', 'product_price', 'ordered')
    extra = 0


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'payment_id', 'payment_method', 'amount_paid')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'full_name', 'payment', 'phone_number', 'email', 'order_total', 'tax', 'status', 'is_ordered')
    list_filter = ('status', 'is_ordered')
    search_fields = ('order_number', 'first_name', 'last_name', 'phone_number', 'email')
    list_per_page = 20
    inlines = [OrderedProductInline]

@admin.register(OrderedProduct)
class OrderedProductAdmin(admin.ModelAdmin):
    list_display = ('order', 'payment', 'product')
