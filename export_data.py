import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")

import django
django.setup()

from django.core.management import call_command

with open("sqlite_data.json", "w", encoding="utf-8") as f:
    call_command(
        "dumpdata",
        natural_foreign=True,
        natural_primary=True,
        exclude=["contenttypes", "auth.permission", "sessions"],
        stdout=f,
    )

print("SQLite data exported successfully!")