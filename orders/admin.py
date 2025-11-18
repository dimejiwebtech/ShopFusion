from django.contrib import admin
from .models import Payment, Order, OrderedProduct


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'payment_id', 'payment_method', 'amount_paid')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'payment', 'order_number')

@admin.register(OrderedProduct)
class OrderedProductAdmin(admin.ModelAdmin):
    list_display = ('order', 'payment', 'product')
