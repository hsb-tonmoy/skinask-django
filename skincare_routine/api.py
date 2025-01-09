from typing import List

from ninja_extra import api_controller, route, status

from skincare_routine.mixins import SkincareRoutinesMixin
from skincare_routine.schemas import SkincareRoutineRouteOptionsSchema, SkincareRoutineSchema


@api_controller("/skincare-routines")
class SkincareRoutinesController(SkincareRoutinesMixin):
    @route.get("", url_name="list", response=List[SkincareRoutineSchema])
    def list_routines(self):
        return self.get_queryset()

    @route.get(
        "/routine-steps-options",
        url_name="routine-steps-options",
        response=SkincareRoutineRouteOptionsSchema,
    )
    def get_routine_steps_options_view(self):
        return self.get_routine_steps_options()

    @route.get("/{pk}", url_name="detail", response=SkincareRoutineSchema)
    def get_routine(self, pk: int):
        return self.get_object(pk)
