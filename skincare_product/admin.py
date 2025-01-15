from wagtail_modeladmin.options import ModelAdmin, ModelAdminGroup, modeladmin_register

from .models import SkincareProduct, SkincareProductCategory


class SkincareProductAdmin(ModelAdmin):
    model = SkincareProduct
    menu_label = "Skincare Products"
    menu_icon = "list-ul"
    list_display = ("product_name", "product_category")
    search_fields = ("product_name", "product_category")


class SkincareProductCategoryAdmin(ModelAdmin):
    model = SkincareProductCategory
    menu_label = "Skincare Product Categories"
    menu_icon = "list-ul"
    list_display = ("name",)
    search_fields = ("name",)


class SkincareProductGroupAdmin(ModelAdminGroup):
    menu_label = "Skincare Product"
    menu_icon = "list-ul"
    menu_order = 200
    items = (SkincareProductAdmin, SkincareProductCategoryAdmin)


modeladmin_register(SkincareProductGroupAdmin)
