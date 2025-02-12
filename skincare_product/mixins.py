from typing import Any, Dict

from django.db.models import Prefetch, QuerySet
from django.shortcuts import get_object_or_404

from skincare_product.models import SkincareProduct, SkincareProductCategory
from skincare_product.schemas import SkincareProductSchema


class SkincareProductsMixin:
    request: Any

    def get_queryset(self) -> QuerySet:
        return SkincareProduct.objects.all()

    def get_product_for_select(self) -> Dict:
        # Return name and id as label and value
        return [
            {"label": product.product_name, "value": product.id} for product in self.get_queryset()
        ]
