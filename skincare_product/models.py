from django.contrib.auth.models import User
from django.db import models


class SkincareProductCategory(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class SkincareProduct(models.Model):
    product_name = models.CharField(max_length=255)
    product_image = models.ImageField(upload_to="skincare_product_images/")
    product_description = models.TextField()
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_category = models.ManyToManyField(SkincareProductCategory)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.product_name
