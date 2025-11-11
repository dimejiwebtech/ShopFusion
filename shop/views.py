from django.shortcuts import render, get_object_or_404

from carts.models import CartItem
from carts.views import _cart_id
from shop.models import Category, Product
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

def home(request):
    products = Product.objects.all().filter(is_available=True)

    context = {
        'products': products,
    }
    return render(request, 'shop/home.html', context)

def store(request):
    products = Product.objects.all().filter(is_available=True)
    paginator = Paginator(products, 6)
    page = request.GET.get('page')
    paged_product = paginator.get_page(page)
    product_count = products.count()

    context = {
        'products': products,
        'paged_product': paged_product,
        'product_count': product_count,
    }
    return render(request, 'shop/store.html', context)

def products_by_category(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    products = Product.objects.filter(category=category, is_available=True)
    paginator = Paginator(products, 2)
    page = request.GET.get('page')
    paged_product = paginator.get_page(page)
    context = {
        'category': category,
        'products': products,
        'paged_product': paged_product,
        'product_count': products.count(),
    }
    return render(request, 'shop/store.html', context)

def product_detail(request, category_slug, product_slug):
    category = get_object_or_404(Category, slug=category_slug)
    product = get_object_or_404(Product, slug=product_slug, category=category, is_available=True)
    in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=product).exists()
    
    context = {
        'product': product,
        'category': category,
        'in_cart': in_cart,
    }
    return render(request, 'shop/product_detail.html', context)