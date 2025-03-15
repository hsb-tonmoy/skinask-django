import datetime

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.models import Orderable

from skincare_product.models import SkincareProduct

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
        help_text=_("The user who created this routine"),
    )
    description = models.TextField(help_text=_("Brief description of this routine"), blank=True)
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
        ("MON", _("Monday")),
        ("TUE", _("Tuesday")),
        ("WED", _("Wednesday")),
        ("THU", _("Thursday")),
        ("FRI", _("Friday")),
        ("SAT", _("Saturday")),
        ("SUN", _("Sunday")),
    ]

    routine = ParentalKey(SkincareRoutine, on_delete=models.CASCADE, related_name="steps")
    product_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text=_("Name of the product if not selecting from catalog"),
    )
    product = models.ForeignKey(
        SkincareProduct,
        on_delete=models.PROTECT,
        related_name="routine_steps",
        null=True,
        blank=True,
    )
    product_type = models.ForeignKey(
        SkincareRoutineProductType, on_delete=models.PROTECT, related_name="routine_steps"
    )
    period = models.ForeignKey(
        SkincareRoutinePeriod, on_delete=models.PROTECT, related_name="routine_steps"
    )
    day_of_week = models.CharField(max_length=3, choices=DAY_CHOICES, default="MON")
    color = models.CharField(
        max_length=255, null=True, blank=True, help_text=_("Color code for the step (e.g. #FF0000)")
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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Clear any cached data that might depend on this step
        self.routine.clear_cache()

    def update_reminders(self, reminder_data):
        """
        Update reminders for this step based on frontend data.

        The expected reminder_data format:
        {
            "MON": {"is_active": True, "time": timestamp_in_ms},
            "TUE": {"is_active": True, "time": timestamp_in_ms},
            ...
        }
        """
        # Clear existing reminders for the current day
        for day, data in reminder_data.items():
            self.reminders.filter(day_of_week=day).delete()

            if (
                data.is_active and hasattr(data, "time") and data.time
            ):  # Check if both is_active is True and time is provided
                # Convert from milliseconds to seconds, then to a datetime object in UTC.
                dt = datetime.datetime.fromtimestamp(data.time / 1000.0, tz=datetime.UTC)
                StepReminder.objects.create(
                    step=self, day_of_week=day, is_active=True, reminder_time=dt
                )


class StepReminder(models.Model):
    """
    Stores reminder settings for a routine step.
    The reminder_time is stored as a DateTimeField in UTC.
    """

    step = models.ForeignKey(RoutineStep, on_delete=models.CASCADE, related_name="reminders")
    day_of_week = models.CharField(max_length=3, choices=RoutineStep.DAY_CHOICES)
    is_active = models.BooleanField(default=True)
    reminder_time = models.DateTimeField(help_text=_("Scheduled reminder time stored in UTC"))

    class Meta:
        unique_together = ["step", "day_of_week", "reminder_time"]
        ordering = ["day_of_week", "reminder_time"]

    def __str__(self):
        return f"Reminder for {self.step} on {self.get_day_of_week_display()}"
