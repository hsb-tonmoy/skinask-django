from typing import List, Optional

from ninja import Schema


class SkincareProductCategorySchema(Schema):
    id: int
    name: str
    description: str = None


class SkincareProductSchema(Schema):
    id: int
    product_name: str
    product_image: Optional[str] = None
    product_category: List[SkincareProductCategorySchema]
    product_price: float


class SkincareProductForSelectSchema(Schema):
    label: str
    value: int
