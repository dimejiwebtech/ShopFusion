from django.shortcuts import get_object_or_404, redirect, render
from carts.models import Cart, CartItem
from shop.models import Product, Variation
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, product_id):
    """
    Adds product with variations to cart.
    Handles both authenticated and anonymous users.
    Increases quantity if same product+variation exists.
    """
    current_user = request.user
    product = Product.objects.get(id=product_id)
    
    # Extract variations from POST data
    product_variation = _extract_product_variations(request, product)
    
    # Route to appropriate handler based on authentication
    if current_user.is_authenticated:
        _add_to_user_cart(product, product_variation, current_user)
    else:
        _add_to_session_cart(request, product, product_variation)
    
    return redirect('cart')


def _extract_product_variations(request, product):
    """
    Extracts product variations (size, color, etc.) from POST request.
    Returns list of Variation objects.
    """
    product_variation = []
    
    if request.method == 'POST':
        for item in request.POST:
            key = item
            value = request.POST[key]
            
            try:
                variation = Variation.objects.get(
                    product=product,
                    variation_category__iexact=key,
                    variation_value__iexact=value
                )
                product_variation.append(variation)
            except Variation.DoesNotExist:
                pass
    
    return product_variation


def _add_to_user_cart(product, product_variation, current_user):
    """
    Adds product to authenticated user's cart.
    If same product+variation exists, increases quantity.
    Otherwise creates new cart item.
    """
    # Get variation IDs for comparison
    product_variation_ids = sorted([v.id for v in product_variation])
    
    # Check if product already in user's cart
    cart_items = CartItem.objects.filter(product=product, user=current_user)
    
    if cart_items.exists():
        # Build lookup map of existing variations
        existing_variation_list = []
        id_list = []
        
        for item in cart_items:
            existing_variation = item.variations.all()
            existing_variation_list.append(sorted(list(existing_variation.values_list('id', flat=True))))
            id_list.append(item.id)
        
        # Check if exact variation combo exists
        if product_variation_ids in existing_variation_list:
            # Increase quantity of existing item
            index = existing_variation_list.index(product_variation_ids)
            item_id = id_list[index]
            item = CartItem.objects.get(product=product, id=item_id)
            item.quantity += 1
            item.save()
        else:
            # Create new cart item for different variation
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                user=current_user
            )
            if len(product_variation) > 0:
                cart_item.variations.add(*product_variation)
    else:
        # Create first cart item for this product
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1,
            user=current_user
        )
        if len(product_variation) > 0:
            cart_item.variations.add(*product_variation)


def _add_to_session_cart(request, product, product_variation):
    """
    Adds product to anonymous user's session cart.
    If same product+variation exists, increases quantity.
    Otherwise creates new cart item.
    """
    # Get variation IDs for comparison
    product_variation_ids = sorted([v.id for v in product_variation])
    
    # Get or create session cart
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
        cart.save()
    
    # Check if product already in session cart
    cart_items = CartItem.objects.filter(product=product, cart=cart)
    
    if cart_items.exists():
        # Build lookup map of existing variations
        existing_variation_list = []
        id_list = []
        
        for item in cart_items:
            existing_variation = item.variations.all()
            existing_variation_list.append(sorted(list(existing_variation.values_list('id', flat=True))))
            id_list.append(item.id)
        
        # Check if exact variation combo exists
        if product_variation_ids in existing_variation_list:
            # Increase quantity of existing item
            index = existing_variation_list.index(product_variation_ids)
            item_id = id_list[index]
            item = CartItem.objects.get(product=product, id=item_id)
            item.quantity += 1
            item.save()
        else:
            # Create new cart item for different variation
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                cart=cart
            )
            if len(product_variation) > 0:
                cart_item.variations.add(*product_variation)
    else:
        # Create first cart item for this product
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart
        )
        if len(product_variation) > 0:
            cart_item.variations.add(*product_variation)

def remove_cart(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(id=cart_item_id, product=product, user=request.user)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(id=cart_item_id, product=product, cart=cart)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()

    except:
        pass
    return redirect('cart')

def delete_cart_item(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(id=cart_item_id, product=product, user=request.user)
            cart_item.delete()
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(id=cart_item_id, product=product, cart=cart)
            cart_item.delete()

    except:
        pass
    return redirect('cart')

def cart(request, total=0, quantity=0, cart_items=None):
    try:
        # show cart if user is authenticated
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)

        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (1.5 * total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        cart = None
        cart_items = []
        tax = 0
        grand_total = 0

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'shop/cart.html', context)

@login_required(login_url=('login'))
def checkout(request, total=0, quantity=0, cart_items=None):
    try:
        # show cart if user is authenticated
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)

        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (1.5 * total)/100
        grand_total = total + tax

    except ObjectDoesNotExist:
        cart = None
        cart_items = []
        tax = 0
        grand_total = 0

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'shop/checkout.html', context)
