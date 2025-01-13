from django.utils.translation import gettext_lazy as _
from wagtail import hooks
from wagtail_modeladmin.options import ModelAdmin, ModelAdminGroup, modeladmin_register

from .models import SkincareRoutinePage, SkincareRoutinePeriod, SkincareRoutineProductType


class SkincareRoutineAdmin(ModelAdmin):
    model = SkincareRoutinePage
    menu_label = "Routines"
    menu_icon = "list-ul"
    menu_order = 100
    list_display = ("title", "created_by", "latest_revision_created_at", "live")
    list_filter = ("created_by", "live")
    search_fields = ("title", "created_by__username")

    def save_model(self, request, instance, form, change):
        instance.save(user=request.user)
        return instance

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(created_by=request.user)
        return qs


class ProductTypeAdmin(ModelAdmin):
    model = SkincareRoutineProductType
    menu_label = "Product Types"
    menu_icon = "tag"
    menu_order = 200
    list_display = ("name", "get_usage_count", "created_at", "updated_at")
    search_fields = ("name",)

    def get_usage_count(self, obj):
        return obj.get_usage_count()

    get_usage_count.short_description = "Steps Using"


class PeriodAdmin(ModelAdmin):
    model = SkincareRoutinePeriod
    menu_label = "Time Periods"
    menu_icon = "time"
    menu_order = 300
    list_display = ("name", "get_usage_count", "created_at", "updated_at")
    search_fields = ("name",)

    def get_usage_count(self, obj):
        return obj.get_usage_count()

    get_usage_count.short_description = "Steps Using"


class SkincareSettingsGroup(ModelAdminGroup):
    menu_label = "Skincare"
    menu_icon = "list-ul"
    menu_order = 200
    items = (
        SkincareRoutineAdmin,
        ProductTypeAdmin,
        PeriodAdmin,
    )


# Register the admin group
modeladmin_register(SkincareSettingsGroup)


@hooks.register("construct_main_menu")
def hide_snippets_menu_item(request, menu_items):
    menu_items[:] = [item for item in menu_items if item.name != "snippets"]


# @hooks.register('construct_page_chooser_queryset')
# def show_only_skincare_routine_index(pages, request):
#     """Hide SkincareRoutineIndexPage from page chooser"""
#     pages = pages.not_type(SkincareRoutineIndexPage)
#     return pages
