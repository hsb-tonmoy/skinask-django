from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import models
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.models import Orderable

User = get_user_model()


class SkincareRoutineProductType(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    panels = [
        FieldPanel("name"),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Product Type"
        verbose_name_plural = "Product Types"

    def get_usage_count(self):
        return self.routine_steps.count()


class SkincareRoutinePeriod(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    panels = [
        FieldPanel("name"),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Period"
        verbose_name_plural = "Periods"

    def get_usage_count(self):
        return self.routine_steps.count()


class SkincareRoutine(ClusterableModel):
    """
    Main routine model using ClusterableModel to support inline relations
    """

    title = models.CharField(max_length=255)
    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="skincare_routines",
        help_text="The user who created this routine",
    )
    description = models.TextField(help_text="Brief description of this routine", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    panels = [
        FieldPanel("title"),
        FieldPanel("description"),
        InlinePanel("steps", label="Steps"),
    ]

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-created_at"]

    def clear_cache(self):
        cache.delete(f"routine_weekly_data_{self.id}")

    def save(self, clean=True, user=None, *args, **kwargs):
        if user and not self.created_by:
            self.created_by = user
        self.clear_cache()
        super().save(*args, **kwargs)

    def get_steps_by_product_type(self, product_type):
        return self.steps.filter(product_type=product_type)

    def get_steps_by_period(self, period):
        return self.steps.filter(period=period)

    def get_steps_by_day(self, day):
        return self.steps.filter(day_of_week=day)


class RoutineStep(Orderable):
    """
    Individual step in a skincare routine
    """

    DAY_CHOICES = [
        ("MON", "Monday"),
        ("TUE", "Tuesday"),
        ("WED", "Wednesday"),
        ("THU", "Thursday"),
        ("FRI", "Friday"),
        ("SAT", "Saturday"),
        ("SUN", "Sunday"),
    ]

    routine = ParentalKey(SkincareRoutine, on_delete=models.CASCADE, related_name="steps")
    product_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Name of the product if not selecting from catalog",
    )
    product_type = models.ForeignKey(
        SkincareRoutineProductType, on_delete=models.PROTECT, related_name="routine_steps"
    )
    period = models.ForeignKey(
        SkincareRoutinePeriod, on_delete=models.PROTECT, related_name="routine_steps"
    )
    day_of_week = models.CharField(max_length=3, choices=DAY_CHOICES, default="MON")
    color = models.CharField(
        max_length=255, null=True, blank=True, help_text="Color code for the step (e.g. #FF0000)"
    )
    notes = models.TextField(null=True, blank=True)

    panels = [
        FieldPanel("product_name"),
        FieldPanel("product_type"),
        FieldPanel("period"),
        FieldPanel("day_of_week"),
        FieldPanel("color"),
        FieldPanel("notes"),
    ]

    class Meta:
        ordering = ["sort_order", "day_of_week"]

    def __str__(self):
        return f"{self.get_day_of_week_display()} - {self.product_name or 'Unnamed Step'}"
