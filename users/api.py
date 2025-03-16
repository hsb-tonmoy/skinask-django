from django.utils.translation import gettext_lazy as _
from ninja_extra import api_controller, http_get, http_patch
from ninja_jwt.authentication import JWTAuth

from .schemas import UserProfileSchema


@api_controller("/users", tags=["Users"], auth=JWTAuth())
class UserController:
    """Controller for user-related operations."""

    @http_get("/me", response=dict)
    def get_current_user(self):
        """Get the current user's profile."""
        user = self.context.request.user

        return {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "language": user.language,
            "timezone": user.timezone,
        }

    @http_patch("/me", response=dict)
    def update_profile(self, data: UserProfileSchema):
        """Update the current user's profile information.

        This endpoint allows updating first_name, last_name, language, and timezone.
        Email and password cannot be updated through this endpoint.
        """
        user = self.context.request.user

        # Track which fields are updated
        updated_fields = []

        # Update fields if provided in the request
        if data.first_name is not None:
            user.first_name = data.first_name
            updated_fields.append("first_name")

        if data.last_name is not None:
            user.last_name = data.last_name
            updated_fields.append("last_name")

        if data.language is not None:
            user.language = data.language
            updated_fields.append("language")

        if data.timezone is not None:
            user.timezone = data.timezone
            updated_fields.append("timezone")

        # Only save if there are fields to update
        if updated_fields:
            user.save(update_fields=updated_fields)

        return {
            "success": True,
            "message": _("Profile updated successfully"),
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "language": user.language,
                "timezone": user.timezone,
            },
        }
