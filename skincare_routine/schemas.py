from datetime import datetime
from typing import Dict, List, Optional

from ninja import Schema

from skincare_routine.models import DayOfWeek


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
    id: int
    product: Optional[dict] = None  # Simplified from SkincareProductSchema
    product_name: Optional[str] = None
    product_type: SkincareRoutineProductTypeSchema
    period: SkincareRoutinePeriodSchema
    day_of_week: str
    color: Optional[str] = None
    notes: Optional[str] = None
    order: int


class WeeklyRoutineSchema(Schema):
    id: int
    name: str
    days: Dict[str, List[SkincareRoutineStepSchema]]
    updated_at: datetime

    @classmethod
    def from_orm(cls, routine):
        return cls(
            id=routine.id,
            name=routine.name,
            days={
                day.value: [
                    SkincareRoutineStepSchema.model_validate(step)
                    for step in routine.steps.all()
                    if step.day_of_week == day.value
                ]
                for day in DayOfWeek
            },
            updated_at=routine.updated_at,
        )


class RoutineOptionsSchema(Schema):
    product_types: List[SkincareRoutineOptionsProductTypeSchema]
    periods: List[SkincareRoutineOptionsPeriodSchema]
    days_of_week: List[Dict[str, str]]


class CreateRoutineStepRequest(Schema):
    color: Optional[str]
    days_of_week: List[str]  # List of day_of_week values
    product_name: str
    notes: Optional[str]
    period: int  # period_id
    skincare_routine: int  # routine_id
    product_type: int  # product_type_id
