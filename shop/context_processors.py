from shop.models import Category

def get_categories(request):
    categories = list(Category.objects.all().order_by('order'))
    return {
        'categories': categories
    }

# def get_categories(request):
#     categories = list(
#         Category.objects.annotate(
#             posts_count=Count('posts', filter=Q(posts__status='published'))
#         ).order_by('order') 
#     )

#     return {
#         'categories': categories
#     }
