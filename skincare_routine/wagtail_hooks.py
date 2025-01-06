from wagtail.snippets.models import register_snippet

from .models import (
    SkincareRoutine,
    SkincareRoutinePeriod,
    SkincareRoutineProductType,
    SkincareRoutineStep,
)

register_snippet(SkincareRoutine)
register_snippet(SkincareRoutineStep)
register_snippet(SkincareRoutineProductType)
register_snippet(SkincareRoutinePeriod)
