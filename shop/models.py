from django.db import models
from django.urls import reverse
from tinymce.models import HTMLField

class Category(models.Model):
    category_name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    order = models.IntegerField(default=0)
    description = HTMLField(blank=True)
    category_image = models.ImageField(upload_to='categories', blank=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['category_name']

    def get_url(self):
        return reverse('products_by_category', args=[self.slug])

    def __str__(self):
        return self.category_name
    

class Product(models.Model):
    product_name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    category = models.ManyToManyField(Category, related_name='products')
    price = models.IntegerField()
    product_content = HTMLField(blank=True)
    short_description = models.TextField(blank=True)
    product_image = models.ImageField(upload_to='products', blank=True)
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    seo_description = models.TextField(max_length=200, blank=True)
    seo_keywords = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['product_name']

    def get_url(self):
        first_category = self.category.first()
        if first_category:
            return reverse('product_detail', args=[first_category.slug, self.slug])
        return '#' 

    def __str__(self):
        return self.product_name
