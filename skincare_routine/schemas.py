from datetime import datetime
from typing import Dict, List, Optional

from ninja import Schema

from skincare_routine.models import DayOfWeek


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
    product_types: List[SkincareRoutineProductTypeSchema]
    periods: List[SkincareRoutinePeriodSchema]
    days_of_week: List[Dict[str, str]]
