from typing import Any, Dict

from django.db.models import Prefetch, QuerySet
from django.shortcuts import get_object_or_404

from skincare_routine.models import (
    RoutineStep,
    SkincareRoutine,
    SkincareRoutinePeriod,
    SkincareRoutineProductType,
)
from skincare_routine.schemas import RoutineOptionsSchema, WeeklyRoutineSchema


class SkincareRoutinesMixin:
    request: Any

    def get_queryset(self) -> QuerySet:
        """Get queryset with optimized prefetch_related"""
        return (
            SkincareRoutine.objects.filter(created_by=self.context.request.auth)
            .prefetch_related(
                Prefetch(
                    "steps",
                    queryset=RoutineStep.objects.select_related("product_type", "period")
                    .prefetch_related("reminders")
                    .order_by("sort_order", "day_of_week"),
                )
            )
            .order_by("-created_at")
        )

    def get_object(self, pk: int) -> SkincareRoutine:
        """Get single routine with optimized prefetch_related"""
        return get_object_or_404(self.get_queryset(), pk=pk)

    def format_routine_response(self, routine: SkincareRoutine) -> Dict:
        """Format routine data for frontend consumption"""
        return WeeklyRoutineSchema.from_orm(routine).model_dump()

    def get_routine_steps_options(self) -> RoutineOptionsSchema:
        """Get all options needed for routine creation/editing"""
        product_types = SkincareRoutineProductType.objects.all()
        periods = SkincareRoutinePeriod.objects.all()
        return RoutineOptionsSchema(
            product_types=[
                {"value": product_type.id, "label": product_type.name}
                for product_type in product_types
            ],
            periods=[{"value": period.id, "label": period.name} for period in periods],
            days_of_week=[
                {"value": day[0], "label": str(day[1])} for day in RoutineStep.DAY_CHOICES
            ],
        )

    def create_routine_step(self, routine: SkincareRoutine, data: dict, day: str) -> RoutineStep:
        """Helper method to create a single routine step"""
        # Get the maximum sort_order for the given day
        max_order = (
            routine.steps.filter(day_of_week=day)
            .order_by("-sort_order")
            .values_list("sort_order", flat=True)
            .first()
            or 0
        )

        # Create the step
        step = RoutineStep(
            routine=routine,  # ParentalKey needs the parent instance
            color=data.color,
            product_name=data.product.label if data.product.value == 0 else None,
            product_id=None if data.product.value == 0 else data.product.value,
            notes=data.notes,
            period_id=data.period,
            product_type_id=data.product_type,
            day_of_week=day,
            sort_order=max_order + 1,
        )

        # Save the step
        step.save()

        # Handle reminders if provided
        if data.reminders and day in data.reminders:
            reminder_data = {day: data.reminders[day]}
            step.update_reminders(reminder_data)

        # Save the parent routine to ensure the relationship is properly set
        routine.save()

        return step
