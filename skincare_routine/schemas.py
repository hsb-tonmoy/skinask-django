from datetime import datetime
from typing import Dict, List, Optional, Union

from ninja import Schema

from skincare_product.schemas import SkincareProductCategorySchema, SkincareProductSchema
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


class ReminderTimeSchema(Schema):
    is_active: bool
    time: int  # timestamp in milliseconds

    class Config:
        # Allow extra fields to be ignored
        extra = "ignore"


class SkincareRoutineStepSchema(Schema):
    id: Optional[int] = None
    product: Optional[SkincareProductSchema] = None
    product_name: Optional[str] = None
    product_type: SkincareRoutineProductTypeSchema
    period: SkincareRoutinePeriodSchema
    day_of_week: str
    reminders: Optional[ReminderTimeSchema] = None
    color: Optional[str] = None
    notes: Optional[str] = None
    sort_order: int
    just_created: bool = False

    @classmethod
    def model_validate(cls, obj):
        # Process reminders
        reminders_data = None
        if obj.reminders.exists():
            # Get all reminders for this step on the current day
            day_reminders = obj.reminders.filter(day_of_week=obj.day_of_week)
            if day_reminders.exists():
                # Extract timestamp in milliseconds (single value now)
                reminder = day_reminders.first()
                reminder_time = int(reminder.reminder_time.timestamp() * 1000)
                reminders_data = ReminderTimeSchema(
                    is_active=reminder.is_active, time=reminder_time
                )

        # Convert product to SkincareProductSchema if it exists
        product_data = None
        if obj.product:
            # Handle product image safely
            product_image = None
            if obj.product.product_image:
                try:
                    product_image = obj.product.product_image.get_rendition("original").url
                except Exception:
                    # If there's any issue with the rendition, try to get the direct URL
                    try:
                        product_image = obj.product.product_image.url
                    except Exception:
                        # If all else fails, leave as None
                        pass

            product_data = SkincareProductSchema(
                id=obj.product.id,
                product_name=obj.product.product_name,
                product_image=product_image,
                product_category=[
                    SkincareProductCategorySchema(
                        id=category.id, name=category.name, description=category.description
                    )
                    for category in obj.product.product_category.all()
                ],
                product_price=float(obj.product.product_price),
            )

        return cls(
            id=obj.id,
            product=product_data,
            product_name=obj.product_name,
            product_type=SkincareRoutineProductTypeSchema(
                id=obj.product_type.id, name=obj.product_type.name
            ),
            period=SkincareRoutinePeriodSchema(id=obj.period.id, name=obj.period.name),
            day_of_week=obj.day_of_week,
            color=obj.color,
            notes=obj.notes,
            reminders=reminders_data,
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
    days_of_week: List[Dict[str, Union[str, int, bool]]]


class ProductSelectionSchema(Schema):
    value: int
    label: str


class CreateRoutineStepRequest(Schema):
    color: Optional[str]
    days_of_week: List[str]
    product: ProductSelectionSchema
    notes: Optional[str] = None
    period: int
    skincare_routine: int
    product_type: int
    reminders: Dict[str, ReminderTimeSchema]

    class Config:
        # Allow extra fields to be ignored
        extra = "ignore"


class UpdateRoutineStepRequest(Schema):
    color: Optional[str] = None
    day_of_week: Optional[str] = None
    product_name: Optional[str] = None
    notes: Optional[str] = None
    period: Optional[int] = None
    product_type: Optional[int] = None
    reminders: Optional[Dict[str, ReminderTimeSchema]] = None

    class Config:
        # Allow extra fields to be ignored
        extra = "ignore"
