"""
File location: ...G1/admin.py
Description: This file is used to register the models in the Django admin interface.
Author: Rachit Khare
(c) 2024 RDM4Lab - all rights reserved
"""

# Django imports
from django.contrib import admin
from django_json_widget.widgets import JSONEditorWidget
from django.db import models

# Application imports
from G1.models import G1Metadata, G1Data, G1Results


# ------------------------------------------
# Registering models in Django admin
# ------------------------------------------


@admin.register(G1Metadata)
class G1MetadataAdmin(admin.ModelAdmin):
    formfield_overrides = {models.JSONField: {"widget": JSONEditorWidget}}
    list_display = ("__str__",)


@admin.register(G1Data)
class G1DataAdmin(admin.ModelAdmin):
    formfield_overrides = {models.JSONField: {"widget": JSONEditorWidget}}
    list_display = (
        "__str__",
        "userexperiment",
        "id",
    )


@admin.register(G1Results)
class G1ResultsAdmin(admin.ModelAdmin):
    formfield_overrides = {models.JSONField: {"widget": JSONEditorWidget}}
    list_display = ("__str__",)
