"""
File location; .../G3/apps.py
Description: This file contains the configuration for the G3 app.
Author: Rachit Khare
(c) 2024 RDM4Lab - all rights reserved
"""

# Django imports
from django.apps import AppConfig

# ------------------------------------------
# Define the configuration here
# ------------------------------------------


class G3Config(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "G3"
    url_namespace = "G3"

    def ready(self):
        # Import the signals here
        import G3.signals
