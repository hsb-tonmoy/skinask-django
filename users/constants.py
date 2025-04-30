import os
from datetime import timedelta

from django.conf import settings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Google OAuth settings
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"

# Application settings
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
APP_SCHEME = os.getenv("APP_SCHEME", "skinask://")

# JWT settings
JWT_SECRET = settings.SECRET_KEY
# Use values from ninja_jwt settings if available
JWT_EXPIRATION_TIME = getattr(settings, "NINJA_JWT", {}).get(
    "ACCESS_TOKEN_LIFETIME", timedelta(days=1)
)
REFRESH_TOKEN_EXPIRY = getattr(settings, "NINJA_JWT", {}).get(
    "REFRESH_TOKEN_LIFETIME", timedelta(days=7)
)
