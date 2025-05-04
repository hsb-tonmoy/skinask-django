from django.utils.translation import gettext_lazy as _
from wagtail import hooks
from wagtail_modeladmin.options import ModelAdmin, ModelAdminGroup, modeladmin_register

from .models import (
    Concern,
    ConcernCategory,
    TrackerSession,
    TrackerSessionNote,
    TrackerSessionPhoto,
    TrackerSessionProduct,
    TrackerSessionVideo,
)


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

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(created_by=request.user)
        return qs


class TrackerSessionAdmin(ModelAdmin):
    model = TrackerSession
    menu_label = "Tracker Sessions"
    menu_icon = "date"
    menu_order = 300
    list_display = ("concern", "date_logged", "user_feeling", "created_at")
    list_filter = ("user_feeling", "concern__concern_category", "concern__created_by")
    search_fields = ("concern__concern_name", "concern__created_by__username")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(concern__created_by=request.user)
        return qs


class TrackerSessionPhotoAdmin(ModelAdmin):
    model = TrackerSessionPhoto
    menu_label = "Session Photos"
    menu_icon = "image"
    menu_order = 400
    list_display = ("session", "created_at")
    list_filter = ("session__concern__concern_category",)
    search_fields = ("session__concern__concern_name",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(session__concern__created_by=request.user)
        return qs


class TrackerSessionVideoAdmin(ModelAdmin):
    model = TrackerSessionVideo
    menu_label = "Session Videos"
    menu_icon = "media"
    menu_order = 500
    list_display = ("session", "created_at")
    list_filter = ("session__concern__concern_category",)
    search_fields = ("session__concern__concern_name",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(session__concern__created_by=request.user)
        return qs


class TrackerSessionNoteAdmin(ModelAdmin):
    model = TrackerSessionNote
    menu_label = "Session Notes"
    menu_icon = "edit"
    menu_order = 600
    list_display = ("session", "created_at")
    list_filter = ("session__concern__concern_category",)
    search_fields = ("session__concern__concern_name", "note")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(session__concern__created_by=request.user)
        return qs


class TrackerSessionProductAdmin(ModelAdmin):
    model = TrackerSessionProduct
    menu_label = "Session Products"
    menu_icon = "pick"
    menu_order = 700
    list_display = ("session", "product", "created_at")
    list_filter = ("session__concern__concern_category", "product")
    search_fields = ("session__concern__concern_name", "product__product_name")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(session__concern__created_by=request.user)
        return qs


class SkincareTrackerSettingsGroup(ModelAdminGroup):
    menu_label = "Skincare Tracker"
    menu_icon = "list-ul"
    menu_order = 200
    items = (
        ConcernCategoryAdmin,
        ConcernAdmin,
        TrackerSessionAdmin,
        TrackerSessionPhotoAdmin,
        TrackerSessionVideoAdmin,
        TrackerSessionNoteAdmin,
        TrackerSessionProductAdmin,
    )


# Register the admin group
modeladmin_register(SkincareTrackerSettingsGroup)


@hooks.register("construct_main_menu")
def hide_snippets_menu_item(request, menu_items):
    menu_items[:] = [item for item in menu_items if item.name != "snippets"]
