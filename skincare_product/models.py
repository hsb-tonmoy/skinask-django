from django import forms
from django.contrib.auth import get_user_model
from django.db import models
from django_currentuser.db.models import CurrentUserField
from wagtail.admin.panels import FieldPanel

User = get_user_model()


class SkincareProductCategory(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
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
    product_description = models.TextField(null=True, blank=True)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_category = models.ManyToManyField(SkincareProductCategory)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = CurrentUserField(on_delete=models.CASCADE)

    panels = [
        FieldPanel("product_name"),
        FieldPanel("product_image"),
        FieldPanel("product_description"),
        FieldPanel("product_price"),
        FieldPanel("product_category", widget=forms.CheckboxSelectMultiple),
    ]

    class Meta:
        verbose_name_plural = "Skincare Products"

    def __str__(self):
        return self.product_name
