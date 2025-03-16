import os

from .base import *

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_TEST_DB"),
        "USER": os.getenv("POSTGRES_TEST_USER"),
        "PASSWORD": os.getenv("POSTGRES_TEST_PASSWORD"),
        "HOST": os.getenv("POSTGRES_TEST_HOST"),
        "PORT": os.getenv("POSTGRES_TEST_PORT"),
    }
}
