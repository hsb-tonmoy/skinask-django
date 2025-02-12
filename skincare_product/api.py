from typing import List

from ninja_extra import api_controller, route
from ninja_extra.searching import Searching, searching
from ninja_jwt.authentication import JWTAuth

from skincare_product.mixins import SkincareProductsMixin
from skincare_product.schemas import SkincareProductForSelectSchema, SkincareProductSchema


@api_controller("/skincare-products", tags=["Skincare Products"], auth=JWTAuth())
class SkincareProductsController(SkincareProductsMixin):
    @route.get("", response=List[SkincareProductForSelectSchema])
    @searching(Searching, search_fields=["label"])
    def list_skincare_products(self, request):
        return self.get_product_for_select()
