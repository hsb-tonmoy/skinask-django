from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class SkincareProductCategory(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Skincare Product Categories"

    def __str__(self):
        return self.name


class SkincareProduct(models.Model):
    product_name = models.CharField(max_length=255)
    product_image = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    product_description = models.TextField()
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_category = models.ManyToManyField(SkincareProductCategory)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Skincare Products"

    def __str__(self):
        return self.product_name
