from typing import Optional

import jwt
import requests
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from ninja_extra import api_controller, http_get, http_patch, http_post
from ninja_jwt.authentication import JWTAuth

from .constants import (
    APP_SCHEME,
    BASE_URL,
    GOOGLE_AUTH_URL,
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    GOOGLE_TOKEN_URL,
)
from .schemas import TokenResponse, UserProfileSchema


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


@api_controller("/auth", tags=["Auth"])
class AuthController:
    """Controller for Oauth-related operations."""

    @http_get("/authorize", response={302: None})
    def authorize(self, state: Optional[str] = None, scope: Optional[str] = None):
        """
        Initiates the OAuth flow by redirecting to Google's authorization endpoint.
        For mobile apps only - redirects back to the app via the app scheme.
        """
        if not GOOGLE_CLIENT_ID:
            return {"error": "Missing GOOGLE_CLIENT_ID environment variable"}, 500

        platform = "mobile"

        # Use state to drive redirect back to platform
        state_param = f"{platform}|{state}" if state else platform

        print("BASE_URL", BASE_URL)

        params = {
            "client_id": GOOGLE_CLIENT_ID,
            "redirect_uri": f"{BASE_URL}/api/auth/callback",
            "response_type": "code",
            "scope": scope or "openid email profile",
            "state": state_param,
            "prompt": "select_account",
        }

        url = f"{GOOGLE_AUTH_URL}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
        response = HttpResponseRedirect(url)
        response.status_code = 302
        return response

    @http_get("/callback", response={302: None})
    def callback(
        self, state: Optional[str] = None, code: Optional[str] = None, error: Optional[str] = None
    ):
        """
        Handles the callback from Google OAuth and redirects to the mobile app.
        """
        if not state:
            return {"error": "Invalid state"}, 400

        # Split the state to get platform and original state
        state_parts = state.split("|")
        original_state = state_parts[1] if len(state_parts) > 1 else ""

        # Build the redirect URL with parameters
        params = []
        if code:
            params.append(f"code={code}")
        if original_state:
            params.append(f"state={original_state}")
        if error:
            params.append(f"error={error}")

        redirect_url = f"{APP_SCHEME}?{'&'.join(params)}"

        response = HttpResponseRedirect(redirect_url)
        response.status_code = 302
        return response

    @http_post("/token", response=TokenResponse)
    def token(self, code: str, platform: str = "native"):
        """
        Exchanges an authorization code for access and refresh tokens.
        For mobile apps only.
        """
        if not code:
            return {"error": "Missing authorization code"}, 400

        # Exchange the code for tokens with Google
        token_request_data = {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": f"{BASE_URL}/api/auth/callback",
            "grant_type": "authorization_code",
            "code": code,
        }

        response = requests.post(GOOGLE_TOKEN_URL, data=token_request_data)
        google_data = response.json()

        if "error" in google_data:
            return {
                "error": google_data.get("error"),
                "error_description": google_data.get("error_description"),
                "message": "OAuth validation error - please ensure the app complies with Google's OAuth 2.0 policy",
            }, 400

        if not google_data.get("id_token"):
            return {"error": "Missing required parameters"}, 400

        # Return entire google_data
        return google_data

        # Decode the ID token to get user info
        # user_info = jwt.decode(
        #     google_data["id_token"],
        #     options={"verify_signature": False}
        # )

        # # Get or create a user based on the Google information
        # User = get_user_model()
        # email = user_info.get("email")

        # if not email or not user_info.get("email_verified"):
        #     return {"error": "Email not verified or not provided"}, 400

        # try:
        #     # Try to find an existing user with this email
        #     user = User.objects.get(email=email)
        # except User.DoesNotExist:
        #     # Create a new user
        #     user = User(
        #         email=email,
        #         first_name=user_info.get("given_name", ""),
        #         last_name=user_info.get("family_name", ""),
        #     )
        #     user.set_unusable_password()  # OAuth user doesn't need a password
        #     user.save()

        # # Generate tokens using ninja-jwt library which is already integrated
        # from ninja_jwt.tokens import RefreshToken
        # refresh = RefreshToken.for_user(user)

        # return {
        #     "access_token": str(refresh.access_token),
        #     "refresh_token": str(refresh),
        # }
