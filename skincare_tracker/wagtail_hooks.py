from django.utils.translation import gettext_lazy as _
from wagtail import hooks
from wagtail_modeladmin.options import ModelAdmin, ModelAdminGroup, modeladmin_register

from .models import Concern, ConcernCategory, TrackerSession


class ConcernCategoryAdmin(ModelAdmin):
    model = ConcernCategory
    menu_label = "Concern Categories"
    menu_icon = "tag"
    menu_order = 100
    list_display = ("name", "created_at", "updated_at")
    search_fields = ("name", "description")


class ConcernAdmin(ModelAdmin):
    model = Concern
    menu_label = "Concerns"
    menu_icon = "warning"
    menu_order = 200
    list_display = ("concern_name", "concern_category", "concern_level", "status", "created_by")
    list_filter = ("concern_category", "status", "tracking_frequency", "created_by")
    search_fields = ("concern_name", "created_by__username")


class TrackerSessionAdmin(ModelAdmin):
    model = TrackerSession
    menu_label = "Tracker Sessions"
    menu_icon = "date"
    menu_order = 300
    list_display = ("concern", "date_logged", "user_feeling", "created_at")
    list_filter = ("user_feeling", "concern__concern_category")
    search_fields = ("concern__concern_name", "concern__created_by__username")


class SkincareTrackerSettingsGroup(ModelAdminGroup):
    menu_label = "Skincare Tracker"
    menu_icon = "list-ul"
    menu_order = 200
    items = (
        ConcernCategoryAdmin,
        ConcernAdmin,
        TrackerSessionAdmin,
    )


# Register the admin group
modeladmin_register(SkincareTrackerSettingsGroup)
