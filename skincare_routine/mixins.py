from typing import Any, Dict

from django.db.models import Prefetch, QuerySet
from django.shortcuts import get_object_or_404

from skincare_routine.models import (
    DayOfWeek,
    SkincareRoutine,
    SkincareRoutinePeriod,
    SkincareRoutineProductType,
    SkincareRoutineStep,
)
from skincare_routine.schemas import RoutineOptionsSchema, WeeklyRoutineSchema


class SkincareRoutinesMixin:
    request: Any

    def get_queryset(self) -> QuerySet:
        """Get queryset with optimized prefetch_related"""
        return (
            SkincareRoutine.objects
            # .filter(user=self.request.user)
            .prefetch_related(
                Prefetch(
                    "steps",
                    queryset=SkincareRoutineStep.objects.select_related(
                        "product", "product_type", "period"
                    ).order_by("day_of_week", "order"),
                )
            ).order_by("-created_at")
        )

    def get_object(self, pk: int) -> SkincareRoutine:
        """Get single routine with optimized prefetch_related"""
        return get_object_or_404(self.get_queryset(), pk=pk)

    def format_routine_response(self, routine: SkincareRoutine) -> Dict:
        """Format routine data for frontend consumption"""
        return WeeklyRoutineSchema.from_orm(routine).model_dump()

    def get_routine_steps_options(self) -> RoutineOptionsSchema:
        """Get all options needed for routine creation/editing"""
        return RoutineOptionsSchema(
            product_types=SkincareRoutineProductType.objects.all(),
            periods=SkincareRoutinePeriod.objects.all(),
            days_of_week=[{"value": day.value, "label": day.label} for day in DayOfWeek],
        )
