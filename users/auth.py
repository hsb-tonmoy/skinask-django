from allauth.headless.tokens.sessions import SessionTokenStrategy
from django.http import HttpRequest
from ninja_jwt.tokens import SlidingToken


class TokenStrategy(SessionTokenStrategy):
    def create_access_token(self, request: HttpRequest) -> str | None:
        user = request.user
        if user.is_authenticated:
            return str(SlidingToken.for_user(user))
        return None
