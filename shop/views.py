from django.shortcuts import redirect, render, get_object_or_404
from carts.models import CartItem
from carts.views import _cart_id
from shop.forms import ReviewForm
from shop.models import Category, Product, ProductGallery, ReviewRating
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.db.models import Avg, Count
from django.contrib import messages

def home(request):
    products = Product.objects.all().filter(is_available=True)
    
    # Add rating data to each product
    for product in products:
        reviews = ReviewRating.objects.filter(product=product, status=True)
        product.review_count = reviews.count()
        product.avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    context = {
        'products': products,
    }
    return render(request, 'shop/home.html', context)


def store(request):
    products = Product.objects.all().filter(is_available=True)
    
    # Add rating data to each product
    for product in products:
        reviews = ReviewRating.objects.filter(product=product, status=True)
        product.review_count = reviews.count()
        product.avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
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
    """
    Display product details with ratings and reviews.
    Handles review submission for authenticated users.
    """
    product = get_object_or_404(Product, slug=product_slug, category__slug=category_slug)

    # Get the product gallery
    product_gallery = ProductGallery.objects.filter(product=product)
    
    # Handle review submission
    if request.method == 'POST' and request.user.is_authenticated:
        form = ReviewForm(request.POST)
        if form.is_valid():
            # Check if user already reviewed this product
            existing_review = ReviewRating.objects.filter(
                product=product,
                user=request.user
            ).first()
            
            if existing_review:
                # Update existing review
                existing_review.subject = form.cleaned_data['subject']
                existing_review.review = form.cleaned_data['review']
                existing_review.rating = form.cleaned_data['rating']
                existing_review.ip = request.META.get('REMOTE_ADDR')
                existing_review.save()
                messages.success(request, 'Your review has been updated successfully!')
            else:
                # Create new review
                review = form.save(commit=False)
                review.product = product
                review.user = request.user
                review.ip = request.META.get('REMOTE_ADDR')
                review.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
            
            return redirect('product_detail', category_slug=category_slug, product_slug=product_slug)
    else:
        form = ReviewForm()
    
    # Get reviews and calculate statistics
    reviews = ReviewRating.objects.filter(product=product, status=True).order_by('-created_at')
    review_count = reviews.count()
    
    # Calculate average rating and rating distribution
    if review_count > 0:
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
        rating_distribution = {
            5: reviews.filter(rating=5).count(),
            4: reviews.filter(rating=4).count(),
            3: reviews.filter(rating=3).count(),
            2: reviews.filter(rating=2).count(),
            1: reviews.filter(rating=1).count(),
        }
    else:
        avg_rating = 0
        rating_distribution = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    
    # Check if user has purchased this product
    user_has_purchased = False
    user_review = None
    if request.user.is_authenticated:
        from orders.models import OrderedProduct
        user_has_purchased = OrderedProduct.objects.filter(
            user=request.user,
            product=product,
            ordered=True
        ).exists()
        user_review = ReviewRating.objects.filter(product=product, user=request.user).first()
    
    context = {
        'product': product,
        'product_gallery': product_gallery,
        'form': form,
        'reviews': reviews,
        'review_count': review_count,
        'avg_rating': round(avg_rating, 1) if avg_rating else 0,
        'rating_distribution': rating_distribution,
        'user_has_purchased': user_has_purchased,
        'user_review': user_review,
    }
    
    return render(request, 'shop/product_detail.html', context)

def product_search(request):
    if 'search-query' in request.GET:
        search_query = request.GET['search-query']
        if search_query:
            products = Product.objects.filter(
                Q(product_name__icontains=search_query) | 
                Q(short_description__icontains=search_query) |
                Q(product_content__icontains=search_query),
                is_available=True
            ).order_by('-created_date')
    
    paginator = Paginator(products, 6)
    page = request.GET.get('page')
    paged_product = paginator.get_page(page)
    
    context = {
        'products': products,
        'paged_product': paged_product,
        'product_count': products.count(),
        'search_query': search_query,
    }
    return render(request, 'shop/store.html', context)