"""
File location; .../G1/apps.py
Description: This file contains the configuration for the G1 app.
Author: Rachit Khare
(c) 2024 RDM4Lab - all rights reserved
"""

# Django imports
from django.apps import AppConfig

# ------------------------------------------
# Define the configuration here
# ------------------------------------------


class G1Config(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "G1"
    url_namespace = "G1"

    def ready(self):
        # Import the signals here
        import G1.signals
