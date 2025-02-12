from django.utils.translation import gettext_lazy as _
from wagtail import hooks
from wagtail_modeladmin.options import ModelAdmin, ModelAdminGroup, modeladmin_register

from .models import SkincareProduct, SkincareProductCategory


class SkincareProductAdmin(ModelAdmin):
    model = SkincareProduct
    menu_label = "Products"
    menu_icon = "pick"  # Using a product-like icon
    menu_order = 100
    list_display = ("product_name", "product_price", "product_category__name")
    list_filter = ("product_category", "created_by")
    search_fields = ("product_name", "product_description", "created_by__username")


class ProductCategoryAdmin(ModelAdmin):
    model = SkincareProductCategory
    menu_label = "Product Categories"
    menu_icon = "tag"
    menu_order = 200
    list_display = ("name", "created_at", "updated_at")
    search_fields = ("name", "description")


class SkincareProductSettingsGroup(ModelAdminGroup):
    menu_label = "Products"
    menu_icon = "pick"
    menu_order = 300  # Positioned after Skincare Routine group
    items = (
        SkincareProductAdmin,
        ProductCategoryAdmin,
    )


# Register the admin group
modeladmin_register(SkincareProductSettingsGroup)
