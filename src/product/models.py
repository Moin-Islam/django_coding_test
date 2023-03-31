from django.db import models
from config.g_model import TimeStampMixin
import json


class Variant(TimeStampMixin):
    title = models.CharField(max_length=40, unique=True)
    description = models.TextField()
    active = models.BooleanField(default=True)


class Product(TimeStampMixin):
    title = models.CharField(max_length=255)
    sku = models.SlugField(max_length=255, unique=True)
    description = models.TextField()
    active = models.BooleanField(default=True)

    
    
    # Reverse relationship to get variants associated with the product
    variants = models.ManyToManyField('ProductVariant', related_name='products')

    # Variant info field
    variant_info = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        variant_info = []
        for variant in self.variants.all():
            variant_info.append({
                'id': variant.id,
                'title': variant.variant_title,
                'variant': variant.variant.title
            })
        print(variant_info) # Add this line to check if variant_info is properly collected
        self.variant_info = json.dumps(variant_info)
        super().save(*args, **kwargs)



class ProductImage(TimeStampMixin):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    file_path = models.URLField()


class ProductVariant(TimeStampMixin):
    variant_title = models.CharField(max_length=255)
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_variants')


class ProductVariantPrice(TimeStampMixin):
    product_variant_one = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, related_name='product_variant_one')
    product_variant_two = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, related_name='product_variant_two')
    product_variant_three = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, related_name='product_variant_three')
    price = models.FloatField()
    stock = models.FloatField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
