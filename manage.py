#!/usr/bin/env python
import os
import sys

from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    if os.getenv("APP_ENV") == "production":
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "skinask_backend.settings.prod")
    else:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "skinask_backend.settings.dev")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
