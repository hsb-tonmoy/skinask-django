from typing import Any

from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from skincare_routine.models import (
    SkincareRoutine,
    SkincareRoutinePeriod,
    SkincareRoutineProductType,
)
from skincare_routine.schemas import SkincareRoutineRouteOptionsSchema


class SkincareRoutinesMixin:
    request: Any

    def get_queryset(self) -> QuerySet:
        return SkincareRoutine.objects.prefetch_related(
            "steps__product", "steps__product_type", "steps__period"
        ).all()

    def get_object(self, pk: int) -> SkincareRoutine:
        queryset = SkincareRoutine.objects.prefetch_related(
            "steps__product", "steps__product_type", "steps__period"
        )
        return get_object_or_404(queryset, pk=pk)

    def get_routine_steps_options(self) -> SkincareRoutineRouteOptionsSchema:
        return SkincareRoutineRouteOptionsSchema(
            product_types=SkincareRoutineProductType.objects.all(),
            periods=SkincareRoutinePeriod.objects.all(),
        )
