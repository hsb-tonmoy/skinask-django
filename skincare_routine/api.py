from typing import List

from django.core.cache import cache
from django.db.models import Prefetch
from ninja.pagination import paginate
from ninja_extra import api_controller, route

from .mixins import SkincareRoutinesMixin
from .models import DayOfWeek, SkincareRoutineStep
from .schemas import RoutineOptionsSchema, WeeklyRoutineSchema


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
