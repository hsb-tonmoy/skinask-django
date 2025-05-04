from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

# Create your models here.


class ConcernCategory(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    image = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


CONERN_FREQUENCY_CHOICES = [
    ("DAILY", "Daily"),
    ("WEEKLY", "Weekly"),
    ("MONTHLY", "Monthly"),
    ("YEARLY", "Yearly"),
]

CONCERN_STATUS_CHOICES = [
    ("ACTIVE", "Active"),
    ("IMPROVED", "Improved"),
    ("RESOLVED", "Resolved"),
    ("ARCHIVED", "Archived"),
]


class Concern(models.Model):
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="concerns",
    )
    concern_name = models.CharField(max_length=255, null=True, blank=True)
    concern_category = models.ForeignKey(
        "ConcernCategory",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="concerns",
    )
    concern_level = models.IntegerField(null=True, blank=True)
    tracking_frequency = models.CharField(
        max_length=255,
        choices=CONERN_FREQUENCY_CHOICES,
    )
    status = models.CharField(
        max_length=255,
        choices=CONCERN_STATUS_CHOICES,
        default="ACTIVE",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.concern_name or self.concern_category.name


USER_FEELING_CHOICES = [
    ("BETTER", "Better"),
    ("WORSE", "Worse"),
    ("SAME", "Same"),
]


class TrackerSession(models.Model):
    concern = models.ForeignKey(
        "Concern",
        on_delete=models.CASCADE,
        related_name="tracker_sessions",
    )
    date_logged = models.DateTimeField()
    user_feeling = models.CharField(
        max_length=255,
        choices=USER_FEELING_CHOICES,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class TrackerSessionPhoto(models.Model):
    session = models.ForeignKey(
        "TrackerSession",
        on_delete=models.CASCADE,
        related_name="tracker_session_photos",
    )
    photo = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class TrackerSessionVideo(models.Model):
    session = models.ForeignKey(
        "TrackerSession",
        on_delete=models.CASCADE,
        related_name="tracker_session_videos",
    )
    video = models.ForeignKey(
        "wagtailmedia.Media",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class TrackerSessionNote(models.Model):
    session = models.ForeignKey(
        "TrackerSession",
        on_delete=models.CASCADE,
        related_name="tracker_session_notes",
    )
    note = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class TrackerSessionProduct(models.Model):
    session = models.ForeignKey(
        "TrackerSession",
        on_delete=models.CASCADE,
        related_name="tracker_session_products",
    )
    product = models.ForeignKey(
        "skincare_product.SkincareProduct",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
