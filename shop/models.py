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
    
class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager, self).filter(variation_category='color', is_active=True)
    
    def sizes(self):
        return super(VariationManager, self).filter(variation_category='size', is_active=True)
    
variation_category_choice = (
    ('color', 'color'),
    ('size', 'size'),
)
    
class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=100, choices=variation_category_choice)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)

    objects = VariationManager()

    def save(self, *args, **kwargs):
    # Check if comma exists in variation_value
        if ',' in self.variation_value:
            values = [v.strip() for v in self.variation_value.split(',')]
            # Create separate variations for each value
            for value in values:
                Variation.objects.get_or_create(
                    product=self.product,
                    variation_category=self.variation_category,
                    variation_value=value,
                    defaults={'is_active': self.is_active}
                )
            # Don't save the original comma-separated one
            return
        else:
            # Save normally if no comma
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.product_name} - {self.variation_value}"
