from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

WAGTAILADMIN_BASE_URL = "https://dev.skinask.com"

# Security
ALLOWED_HOSTS = ["*"]
CSRF_TRUSTED_ORIGINS = ["https://dev.skinask.com"]

# Email
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
