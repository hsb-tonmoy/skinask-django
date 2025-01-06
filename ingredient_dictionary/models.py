from django.db import models
from wagtail.fields import RichTextField


class IngredientCategory(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class IngredientBenefit(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=255)
    rating = models.CharField(max_length=255)
    short_description = models.TextField()
    description = RichTextField()
    key_points = models.TextField()
    categories = models.ManyToManyField(IngredientCategory, related_name="ingredients")
    benefits = models.ManyToManyField(IngredientBenefit, related_name="ingredients")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
