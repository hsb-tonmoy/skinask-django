from django.contrib.auth.models import User
from django.db import models

from skincare_product.models import SkincareProduct


class SkincareRoutineProductType(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Product Types"

    def __str__(self):
        return self.name


class SkincareRoutinePeriod(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Periods"

    def __str__(self):
        return self.name


class SkincareRoutine(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Routines"

    def __str__(self):
        return self.name


class SkincareRoutineStep(models.Model):
    skincare_routine = models.ForeignKey(
        SkincareRoutine, on_delete=models.CASCADE, related_name="steps"
    )
    product = models.ForeignKey(SkincareProduct, on_delete=models.CASCADE, null=True, blank=True)
    product_name = models.CharField(max_length=255, null=True, blank=True)
    product_type = models.ForeignKey(SkincareRoutineProductType, on_delete=models.CASCADE)
    period = models.ForeignKey(SkincareRoutinePeriod, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Routine Steps"

    def __str__(self):
        return self.product.product_name if self.product else self.product_name
