from typing import List

from django.core.cache import cache
from django.shortcuts import get_object_or_404
from ninja_extra import api_controller, route
from ninja_extra.exceptions import PermissionDenied
from ninja_jwt.authentication import JWTAuth

from skincare_routine.mixins import SkincareRoutinesMixin
from skincare_routine.models import (
    RoutineStep,
    SkincareRoutine,
    SkincareRoutinePeriod,
    SkincareRoutineProductType,
)
from skincare_routine.schemas import (
    CreateRoutineStepRequest,
    RoutineOptionsSchema,
    ToggleRoutineStepResponse,
    UpdateRoutineStepRequest,
    WeeklyRoutineSchema,
)


@api_controller("/skincare-routines", tags=["Skincare Routines"], auth=JWTAuth())
class SkincareRoutinesController(SkincareRoutinesMixin):
    @route.get("", response=List[WeeklyRoutineSchema])
    def list_routines(self):
        """
        List all routines for the current user with their weekly steps.
        Steps are organized by day of the week for efficient frontend rendering.
        If no routines exist, creates a default empty routine.
        """
        # Try to get from cache first
        cache_key = f"routines_{self.context.request.auth.id}"
        cached_routines = cache.get(cache_key)
        if cached_routines:
            return cached_routines

        routines = self.get_queryset()

        # Create default routine if none exist
        if not routines.exists():
            SkincareRoutine.objects.create(
                title="My Skincare Routine",
                description="My personalized skincare routine",
                created_by=self.context.request.auth,
            )
            routines = self.get_queryset()  # Refresh queryset to include new routine

        response = [self.format_routine_response(routine) for routine in routines]

        # Cache for 24 hours
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

        # Create steps for each day and track their IDs
        created_step_ids = []
        for day in data.days_of_week:
            step = self.create_routine_step(routine, data, day)
            created_step_ids.append(step.id)

        # Clear cache
        cache.delete(f"routine_weekly_data_{routine.id}")
        cache.delete(f"routines_{self.context.request.auth.id}")

        # Get a fresh instance of the routine with all steps
        updated_routine = self.get_object(routine.id)

        # Format response with just_created flag
        return self.format_routine_response(updated_routine, created_step_ids)

    @route.patch("/steps/{int:step_id}", response=WeeklyRoutineSchema)
    def update_routine_step(self, step_id: int, data: UpdateRoutineStepRequest):
        """Update a specific routine step"""
        step = get_object_or_404(RoutineStep, id=step_id)
        if step.routine.created_by != self.context.request.auth:
            raise PermissionDenied("You are not allowed to update this step")

        # Update fields using dict comprehension to filter out None values
        update_fields = {
            k: v for k, v in data.model_dump().items() if v is not None and k != "reminders"
        }

        # Handle foreign key references properly
        for field, value in update_fields.items():
            if field == "period" and isinstance(value, int):
                # Get the actual period object
                period_obj = get_object_or_404(SkincareRoutinePeriod, id=value)
                setattr(step, field, period_obj)
            elif field == "product_type" and isinstance(value, int):
                # Get the actual product type object
                product_type_obj = get_object_or_404(SkincareRoutineProductType, id=value)
                setattr(step, field, product_type_obj)
            else:
                setattr(step, field, value)

        # Handle reminder updates if provided
        if data.reminders is not None:
            step.update_reminders(data.reminders)

        step.save()

        # Clear cache
        cache.delete(f"routine_weekly_data_{step.routine.id}")
        cache.delete(f"routines_{self.context.request.auth.id}")

        return self.format_routine_response(step.routine)

    @route.patch("/steps/toggle/{int:step_id}", response=ToggleRoutineStepResponse)
    def toggle_routine_step(self, step_id: int):
        """Toggle a specific routine step's completion status and return just the new status"""
        step = get_object_or_404(RoutineStep, id=step_id)
        if step.routine.created_by != self.context.request.auth:
            raise PermissionDenied("You are not allowed to update this step")

        step.toggle_is_completed()

        # Clear cache
        cache.delete(f"routine_weekly_data_{step.routine.id}")
        cache.delete(f"routines_{self.context.request.auth.id}")

        return {"is_completed": step.is_completed}

    @route.delete("/steps/{int:step_id}", response=WeeklyRoutineSchema)
    def delete_routine_step(self, step_id: int):
        """Delete a specific routine step"""
        step = get_object_or_404(RoutineStep, id=step_id)
        if step.routine.created_by != self.context.request.auth:
            raise PermissionDenied("You are not allowed to delete this step")

        step.delete()
        cache.delete(f"routine_weekly_data_{step.routine.id}")
        cache.delete(f"routines_{self.context.request.auth.id}")
        return self.format_routine_response(step.routine)
