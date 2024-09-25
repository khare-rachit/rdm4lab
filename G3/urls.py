"""
File location: ...G3/urls.py
Description: This file contains the URL patterns for the G3 app.
Author: Rachit Khare
(c) 2024 RDM4Lab - all rights reserved
"""

# Django imports
from django.urls import path

# Application imports
from G3 import views

app_name = "G3"

# ------------------------------------------
# URL patterns for the G3 app
# ------------------------------------------

urlpatterns = [
    path(
        "",
        views.G3_data,
        name="G3-data",
    ),
    path(
        "<int:pk>/toggle_active/",
        views.G3_toggle_active,
        name="G3-toggle-active",
    ),
    path(
        "add/",
        views.G3_data_add,
        name="G3-data-add",
    ),
    path(
        "<int:pk>/edit/",
        views.G3_data_edit,
        name="G3-data-edit",
    ),
    path(
        "analysis/",
        views.G3_data_analysis,
        name="G3-data-analysis",
    ),
    path(
        "simulation/",
        views.G3_data_simulation,
        name="G3-data-simulation",
    ),
]
