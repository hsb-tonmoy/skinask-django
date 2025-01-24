from typing import List

from django.core.cache import cache
from django.shortcuts import get_object_or_404
from ninja_extra import api_controller, route
from ninja_jwt.authentication import JWTAuth

from .mixins import SkincareRoutinesMixin
from .schemas import CreateRoutineStepRequest, RoutineOptionsSchema, WeeklyRoutineSchema


@api_controller("/skincare-routines", tags=["Skincare Routines"], auth=JWTAuth())
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
        routine = get_object_or_404(self.get_queryset(), id=data.skincare_routine)

        # Create steps for each day
        for day in data.days_of_week:
            self.create_routine_step(routine, data, day)

        # Clear cache
        cache.delete(f"routine_weekly_data_{routine.id}")

        # Get a fresh instance of the routine with all steps
        updated_routine = self.get_object(routine.id)

        return self.format_routine_response(updated_routine)
