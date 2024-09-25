"""
File location: ...G1/urls.py
Description: This file contains the URL patterns for the G1 app.
Author: Rachit Khare
(c) 2024 RDM4Lab - all rights reserved
"""

# Django imports
from django.urls import path

# Application imports
from G1 import views

app_name = "G1"

# ------------------------------------------
# URL patterns for the G1 app
# ------------------------------------------

urlpatterns = [
    path(
        "",
        views.G1_data,
        name="G1-data",
    ),
    path(
        "add/",
        views.G1_data_add,
        name="G1-data-add",
    ),
    path(
        "<int:pk>/edit/",
        views.G1_data_edit,
        name="G1-data-edit",
    ),
    path(
        "<int:pk>/toggle_active/",
        views.G1_toggle_active,
        name="G1-toggle-active",
    ),
    path(
        "analysis/",
        views.G1_data_analysis,
        name="G1-data-analysis",
    ),
]
