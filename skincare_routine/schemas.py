from typing import Optional

from ninja import Schema

from skincare_product.schemas import SkincareProductSchema


# Generic schemas
class SkincareRoutineProductTypeSchema(Schema):
    id: int
    name: str


class SkincareRoutinePeriodSchema(Schema):
    id: int
    name: str


class SkincareRoutineStepSchema(Schema):
    id: int
    product: Optional[SkincareProductSchema] = None
    product_name: Optional[str] = None
    product_type: SkincareRoutineProductTypeSchema
    period: SkincareRoutinePeriodSchema


class SkincareRoutineSchema(Schema):
    id: int
    name: str
    steps: list[SkincareRoutineStepSchema]


# API schemas
class SkincareRoutineRouteOptionsSchema(Schema):
    product_types: list[SkincareRoutineProductTypeSchema]
    periods: list[SkincareRoutinePeriodSchema]
