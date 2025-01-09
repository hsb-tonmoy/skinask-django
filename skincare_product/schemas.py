from ninja import Schema


class SkincareProductCategorySchema(Schema):
    id: int
    name: str


class SkincareProductSchema(Schema):
    id: int
    product_name: str
    product_image: str
    product_category: SkincareProductCategorySchema
    product_price: float
