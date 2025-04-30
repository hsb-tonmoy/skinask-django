from typing import Optional

import pytz
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from ninja import Schema
from pydantic import field_validator


class UserProfileSchema(Schema):
    """Schema for user profile data."""

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language: Optional[str] = None
    timezone: Optional[str] = None

    @field_validator("language")
    def validate_language(cls, value):
        if value is None:
            return value

        valid_languages = [lang_code for lang_code, _ in settings.LANGUAGES]
        if value not in valid_languages:
            raise ValueError(_("Invalid language choice"))
        return value

    @field_validator("timezone")
    def validate_timezone(cls, value):
        if value is None:
            return value

        try:
            pytz.timezone(value)
        except pytz.exceptions.UnknownTimeZoneError:
            raise ValueError(_("Invalid timezone"))
        return value

    @field_validator("first_name", "last_name")
    def validate_name(cls, value):
        if value is None:
            return value

        if len(value) > 150:  # Django's default max_length for these fields
            raise ValueError(_("Name is too long"))
        return value


# OAuth schemas
class GoogleAuthorizeSchema(Schema):
    client_id: str
    redirect_uri: str
    state: Optional[str] = None
    scope: Optional[str] = None


class GoogleCallbackSchema(Schema):
    code: Optional[str] = None
    state: Optional[str] = None
    error: Optional[str] = None


class GoogleTokenRequest(Schema):
    code: str
    platform: str = "native"


class TokenRequest(Schema):
    code: str
    platform: Optional[str] = None


class TokenResponse(Schema):
    access_token: str
    expires_in: int
    scope: str
    token_type: str
    id_token: str
    refresh_token: Optional[str] = None
    client_id: Optional[str] = None
