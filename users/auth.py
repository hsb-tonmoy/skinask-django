from typing import Any, Dict

from allauth.headless.adapter import DefaultHeadlessAdapter
from allauth.headless.tokens.sessions import SessionTokenStrategy
from django.http import HttpRequest
from ninja_jwt.tokens import RefreshToken


class TokenStrategy(SessionTokenStrategy):
    def create_access_token(self, request: HttpRequest) -> str | None:
        user = request.user
        if user.is_authenticated:
            refresh_token = RefreshToken.for_user(user)
            return str(refresh_token.access_token)
        return None

    def create_access_token_payload(self, request: HttpRequest) -> Dict[str, Any] | None:
        access_token = self.create_access_token(request)
        if not access_token:
            return None

        user = request.user
        refresh_token = RefreshToken.for_user(user)
        return {
            "access_token": access_token,
            "refresh_token": str(refresh_token),
        }


class HeadlessAdapter(DefaultHeadlessAdapter):
    def serialize_user(self, user) -> Dict[str, Any]:
        return {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "timezone": user.timezone,
            "language": user.language,
        }
