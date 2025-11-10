from django.shortcuts import render, get_object_or_404

from shop.models import Category, Product

def home(request):
    products = Product.objects.all().filter(is_available=True)

    context = {
        'products': products,
    }
    return render(request, 'shop/home.html', context)

def store(request):
    products = Product.objects.all().filter(is_available=True)
    product_count = products.count()

    context = {
        'products': products,
        'product_count': product_count,
    }
    return render(request, 'shop/store.html', context)

def products_by_category(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    products = Product.objects.filter(category=category, is_available=True)
    context = {
        'category': category,
        'products': products,
        'product_count': products.count(),
    }
    return render(request, 'shop/store.html', context)

def product_detail(request, category_slug, product_slug):
    category = get_object_or_404(Category, slug=category_slug)
    product = get_object_or_404(Product, slug=product_slug, category=category, is_available=True)
    context = {
        'product': product,
        'category': category,
    }
    return render(request, 'shop/product_detail.html', context)