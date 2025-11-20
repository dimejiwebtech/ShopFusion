import datetime
from django.shortcuts import redirect, render
from carts.models import CartItem
from orders.forms import OrderForm
from orders.models import Order, OrderedProduct, Payment
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from collections import defaultdict

# Email Imports
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site

def payments(request):
    """
    Handles payment processing and order creation.
    Processes PayPal payment data and creates OrderedProduct entries.
    """
    if request.method == 'POST':
        try:
            # Parse payment data from PayPal
            data = json.loads(request.body)
            
            # Create payment record
            payment = Payment.objects.create(
                user=request.user,
                payment_id=data['payment_id'],
                payment_method=data['payment_method'],
                amount_paid=data['amount_paid'],
                status=data['status']
            )
            
            # Get the order and update with payment
            order = Order.objects.get(
                order_number=data['order_number'], 
                user=request.user,
                is_ordered=False
            )
            order.is_ordered = True
            order.payment = payment
            order.save()
            
            # Move cart items to ordered products - Direct 1:1 mapping
            cart_items = CartItem.objects.filter(user=request.user)
            
            for item in cart_items:
                # Get variations for this cart item
                item_variations = item.variations.all()
                color = item_variations.filter(variation_category__iexact='color').first()
                size = item_variations.filter(variation_category__iexact='size').first()
                
                # Create OrderedProduct entry
                ordered_product = OrderedProduct.objects.create(
                    order=order,
                    payment=payment,
                    user=request.user,
                    product=item.product,
                    quantity=item.quantity,
                    product_price=item.product.price,
                    ordered=True
                )
                
                # Store variations in M2M field for reference
                ordered_product.variations.set(item_variations)

                # Reduce product stock
                item.product.stock -= item.quantity
                item.product.save()
            
            # Clear user's cart
            cart_items.delete()
            current_site = get_current_site(request)
            mail_subject = "Order Confirmation - StoreFrenzy"
            message = render_to_string('orders/emails/order_received_email.html', {
                'user': request.user,
                'order': order,
                'domain': current_site.domain,
            })
            to_email = request.user.email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.content_subtype = 'html' 
            send_email.send()


            
            return JsonResponse({
                'success': True,
                'redirect_url': f'/orders/order-complete/?order_number={order.order_number}&payment_id={payment.payment_id}'
            })
            
        except Order.DoesNotExist:
            return JsonResponse({
                'success': False, 
                'error': 'Order not found'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'error': str(e)
            }, status=400)
    
    return JsonResponse({
        'success': False, 
        'error': 'Invalid request method'
    }, status=400)

def place_order(request, total=0, quantity=0):
    """
    Creates order from cart and displays payment page.
    Validates cart and calculates totals before checkout.
    """
    current_user = request.user

    # Redirect if cart is empty
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')
    
    # Calculate totals
    grand_total = 0
    tax = 0

    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    
    tax = (1.5 * total) / 100
    grand_total = total + tax
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Save billing information in Order
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone_number = form.cleaned_data['phone_number']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            
            # Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            # Get order for payment page
            order = Order.objects.get(
                user=current_user, 
                is_ordered=False, 
                order_number=order_number
            )
            
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
            }
            return render(request, 'orders/payments.html', context)
    
    # If GET request, redirect to checkout
    return redirect('checkout')

def order_complete(request):
    """
    Displays order completion page with invoice details.
    Shows order summary, items, and payment confirmation.
    """
    order_number = request.GET.get('order_number')
    payment_id = request.GET.get('payment_id')
    
    try:
        # Get order and related data
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderedProduct.objects.filter(order=order)
        
        # Calculate subtotal
        subtotal = sum(item.product_price * item.quantity for item in ordered_products)
        
        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order_number,
            'payment_id': payment_id,
            'subtotal': subtotal,
        }
        return render(request, 'orders/order_complete.html', context)
    
    except Order.DoesNotExist:
        return redirect('store')
