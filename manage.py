#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


# This function is used to run the Django project from the command line.
def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rdm4lab.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


# This is the entry point for the Django project. It is used to run the Django project from the command line.
if __name__ == "__main__":
    main()
