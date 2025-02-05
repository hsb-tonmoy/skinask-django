from datetime import datetime
from typing import Dict, List, Optional

from ninja import Schema

from skincare_routine.models import RoutineStep


class SkincareRoutineOptionsProductTypeSchema(Schema):
    value: int
    label: str


class SkincareRoutineOptionsPeriodSchema(Schema):
    value: int
    label: str


class SkincareRoutineProductTypeSchema(Schema):
    id: int
    name: str


class SkincareRoutinePeriodSchema(Schema):
    id: int
    name: str


class SkincareRoutineStepSchema(Schema):
    id: Optional[int] = None
    product: Optional[dict] = None
    product_name: Optional[str] = None
    product_type: SkincareRoutineProductTypeSchema
    period: SkincareRoutinePeriodSchema
    day_of_week: str
    color: Optional[str] = None
    notes: Optional[str] = None
    sort_order: int

    @classmethod
    def model_validate(cls, obj):
        return cls(
            id=obj.id,
            product_name=obj.product_name,
            product_type=SkincareRoutineProductTypeSchema(
                id=obj.product_type.id, name=obj.product_type.name
            ),
            period=SkincareRoutinePeriodSchema(id=obj.period.id, name=obj.period.name),
            day_of_week=obj.day_of_week,
            color=obj.color,
            notes=obj.notes,
            sort_order=obj.sort_order,
        )


class WeeklyRoutineSchema(Schema):
    id: int
    title: str
    description: Optional[str]
    days: Dict[str, List[SkincareRoutineStepSchema]]
    updated_at: datetime

    @classmethod
    def from_orm(cls, routine):
        return cls(
            id=routine.id,
            title=routine.title,
            description=routine.description,
            days={
                day[0]: [
                    SkincareRoutineStepSchema.model_validate(step)
                    for step in routine.steps.all()
                    if step.day_of_week == day[0]
                ]
                for day in RoutineStep.DAY_CHOICES
            },
            updated_at=routine.updated_at,
        )


class RoutineOptionsSchema(Schema):
    product_types: List[SkincareRoutineOptionsProductTypeSchema]
    periods: List[SkincareRoutineOptionsPeriodSchema]
    days_of_week: List[Dict[str, str]]


class CreateRoutineStepRequest(Schema):
    color: Optional[str]
    days_of_week: List[str]
    product_name: str
    notes: Optional[str] = None
    period: int
    skincare_routine: int
    product_type: int


class UpdateRoutineStepRequest(Schema):
    color: Optional[str] = None
    day_of_week: Optional[str] = None
    product_name: Optional[str] = None
    notes: Optional[str] = None
    period: Optional[int] = None
    product_type: Optional[int] = None
