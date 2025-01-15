# from wagtail_modeladmin.options import ModelAdmin, ModelAdminGroup, modeladmin_register

# from .models import (
#     SkincareRoutine,
#     SkincareRoutinePeriod,
#     SkincareRoutineProductType,
#     SkincareRoutineStep,
# )


# class SkincareRoutineAdmin(ModelAdmin):
#     model = SkincareRoutine
#     menu_label = "Routines"
#     menu_icon = "list-ul"
#     list_display = ("name", "user")
#     search_fields = ("name", "user")


# class SkincareRoutineStepAdmin(ModelAdmin):
#     model = SkincareRoutineStep
#     menu_label = "Routine Steps"
#     menu_icon = "list-ul"
#     list_display = ("product_name", "product_type", "period")
#     search_fields = ("product_name", "product_type", "period")


# class SkincareRoutineProductTypeAdmin(ModelAdmin):
#     model = SkincareRoutineProductType
#     menu_label = "Product Types"
#     menu_icon = "list-ul"
#     list_display = ("name", "updated_at")
#     search_fields = ("name", "updated_at")


# class SkincareRoutinePeriodAdmin(ModelAdmin):
#     model = SkincareRoutinePeriod
#     menu_label = "Periods"
#     menu_icon = "list-ul"
#     list_display = ("name", "updated_at")
#     search_fields = ("name", "updated_at")


# class SkincareRoutineGroupAdmin(ModelAdminGroup):
#     menu_label = "Skincare Routine"
#     menu_icon = "list-ul"
#     menu_order = 200
#     items = (
#         SkincareRoutineAdmin,
#         SkincareRoutineStepAdmin,
#         SkincareRoutineProductTypeAdmin,
#         SkincareRoutinePeriodAdmin,
#     )


# modeladmin_register(SkincareRoutineGroupAdmin)
