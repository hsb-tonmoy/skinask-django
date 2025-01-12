from typing import List

from django.core.cache import cache
from django.shortcuts import get_object_or_404
from ninja.errors import HttpError
from ninja_extra import api_controller, route

from .mixins import SkincareRoutinesMixin
from .schemas import CreateRoutineStepRequest, RoutineOptionsSchema, WeeklyRoutineSchema


@api_controller("/skincare-routines", tags=["Skincare Routines"])
class SkincareRoutinesController(SkincareRoutinesMixin):
    @route.get("", response=List[WeeklyRoutineSchema])
    def list_routines(self):
        """
        List all routines for the current user with their weekly steps.
        Steps are organized by day of the week for efficient frontend rendering.
        """
        routines = self.get_queryset()
        return [self.format_routine_response(routine) for routine in routines]

    @route.get("/{int:routine_id}", response=WeeklyRoutineSchema)
    def get_routine(self, routine_id: int):
        """Get a specific routine with all its weekly steps"""
        # Try to get from cache first
        cache_key = f"routine_weekly_data_{routine_id}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data

        routine = self.get_object(routine_id)
        response = self.format_routine_response(routine)

        # Cache for 1 hour
        cache.set(cache_key, response, 3600)
        return response

    @route.get("/options", response=RoutineOptionsSchema)
    def get_routine_options(self):
        """Get all options needed for routine creation/editing"""
        cache_key = "routine_options"
        cached_options = cache.get(cache_key)
        if cached_options:
            return cached_options

        options = self.get_routine_steps_options()
        # Cache for 24 hours since these rarely change
        cache.set(cache_key, options, 86400)
        return options

    @route.post("/steps", response=WeeklyRoutineSchema)
    def create_routine_steps(self, data: CreateRoutineStepRequest):
        """Create multiple routine steps for different days of the week"""
        # Get the routine and verify ownership
        routine = get_object_or_404(self.get_queryset(), id=data.skincare_routine)

        # Verify the routine belongs to the current user
        # if routine.user != self.request.user:
        #     raise HttpError(403, "Not authorized to modify this routine")

        # Create a step for each day in frequency
        for day in data.days_of_week:
            # Get the maximum order for this day
            max_order = (
                routine.steps.filter(day_of_week=day)
                .order_by("-order")
                .values_list("order", flat=True)
                .first()
                or 0
            )

            routine.steps.create(
                color=data.color,
                product_name=data.product_name,
                notes=data.notes,
                period_id=data.period,
                product_type_id=data.product_type,
                day_of_week=day,
                order=max_order + 1,
            )

        # The routine's cache will be automatically cleared due to the save() method override
        return self.format_routine_response(routine)
