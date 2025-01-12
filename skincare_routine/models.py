from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import models


class DayOfWeek(models.TextChoices):
    MONDAY = "MON", "Monday"
    TUESDAY = "TUE", "Tuesday"
    WEDNESDAY = "WED", "Wednesday"
    THURSDAY = "THU", "Thursday"
    FRIDAY = "FRI", "Friday"
    SATURDAY = "SAT", "Saturday"
    SUNDAY = "SUN", "Sunday"


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
        indexes = [
            models.Index(fields=["user", "created_at"]),
        ]

    def __str__(self):
        return self.name

    def clear_cache(self):
        """Clear the cache for this routine's weekly data"""
        cache.delete(f"routine_weekly_data_{self.id}")

    def save(self, *args, **kwargs):
        """Override save to clear cache when routine is updated"""
        self.clear_cache()
        super().save(*args, **kwargs)


class SkincareRoutineStep(models.Model):
    skincare_routine = models.ForeignKey(
        SkincareRoutine, on_delete=models.CASCADE, related_name="steps"
    )
    product = models.ForeignKey(
        "skincare_product.SkincareProduct", on_delete=models.CASCADE, null=True, blank=True
    )
    product_name = models.CharField(max_length=255, null=True, blank=True)
    product_type = models.ForeignKey(SkincareRoutineProductType, on_delete=models.CASCADE)
    period = models.ForeignKey(SkincareRoutinePeriod, on_delete=models.CASCADE)
    day_of_week = models.CharField(
        max_length=3, choices=DayOfWeek.choices, db_index=True, default=DayOfWeek.MONDAY
    )
    color = models.CharField(max_length=255, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Routine Steps"
        ordering = ["day_of_week", "order"]
        indexes = [
            models.Index(fields=["skincare_routine", "day_of_week", "order"]),
        ]

    def get_day_of_week_display(self):
        return DayOfWeek(self.day_of_week).label

    def __str__(self):
        return f"{self.get_day_of_week_display()} - {self.product.product_name if self.product else self.product_name}"

    def save(self, *args, **kwargs):
        """Override save to clear routine cache when step is updated"""
        super().save(*args, **kwargs)
        self.skincare_routine.clear_cache()
