from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.models import Orderable, Page


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
        verbose_name_plural = "Product Types"

    def get_usage_count(self):
        """Returns the number of steps using this product type"""
        return self.routine_steps.count()

    def get_routines_using_this(self):
        """Returns all routines that have steps using this product type"""
        return SkincareRoutinePage.objects.filter(steps__product_type=self).distinct()


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
        verbose_name_plural = "Periods"

    def get_usage_count(self):
        """Returns the number of steps using this period"""
        return self.routine_steps.count()


class SkincareRoutinePage(Page):
    """
    A page type for creating skincare routines
    """

    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="skincare_routines",
        help_text="The user who created this routine",
    )

    introduction = models.TextField(help_text="Brief description of this routine", blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("introduction"),
        InlinePanel("steps", label="Steps"),
    ]

    def clear_cache(self):
        """Clear the cache for this routine's weekly data"""
        cache.delete(f"routine_weekly_data_{self.id}")

    def save(self, *args, **kwargs):
        self.clear_cache()
        super().save(*args, **kwargs)

    def get_steps_by_product_type(self, product_type):
        """Get all steps in this routine using a specific product type"""
        return self.steps.filter(product_type=product_type)

    def get_steps_by_period(self, period):
        """Get all steps in this routine for a specific period"""
        return self.steps.filter(period=period)

    def get_steps_by_day(self, day):
        """Get all steps in this routine for a specific day"""
        return self.steps.filter(day_of_week=day)


class RoutineStep(Orderable):
    """
    Represents a step in a skincare routine.
    Using Orderable allows for drag-and-drop reordering in the Wagtail admin.
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

    routine = ParentalKey(SkincareRoutinePage, on_delete=models.CASCADE, related_name="steps")
    product_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Name of the product if not selecting from catalog",
    )
    product_type = models.ForeignKey(
        SkincareRoutineProductType,
        on_delete=models.PROTECT,  # Prevent deletion of product type if it's being used
        related_name="routine_steps",
    )
    period = models.ForeignKey(
        SkincareRoutinePeriod,
        on_delete=models.PROTECT,  # Prevent deletion of period if it's being used
        related_name="routine_steps",
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
        ordering = ["sort_order", "day_of_week"]  # Default ordering

    def __str__(self):
        return f"{self.get_day_of_week_display()} - {self.product_name or 'Unnamed Step'}"
