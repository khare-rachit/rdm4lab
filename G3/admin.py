"""
File location: .../G3/admin.py
Description: This file contains the django admin settings for the G3 app.
Author: Rachit Khare
(c) 2024 RDM4Lab - all rights reserved
"""

# Django imports
from django.contrib import admin
from django.db import models

# Model imports
from G3.models import (
    G3Metadata,
    G3Data,
    G3Results,
    G3SimulGlobalParams,
    G3SimulParams,
)

# Third-party imports
from django_json_widget.widgets import JSONEditorWidget

# ------------------------------------------
# Model registration.
# ------------------------------------------


@admin.register(G3Metadata)
class G3MetadataAdmin(admin.ModelAdmin):
    formfield_overrides = {models.JSONField: {"widget": JSONEditorWidget}}
    list_display = ("__str__",)


@admin.register(G3Data)
class G3DataAdmin(admin.ModelAdmin):
    formfield_overrides = {models.JSONField: {"widget": JSONEditorWidget}}
    list_display = (
        "__str__",
        "userexperiment",
        "id",
        "is_active",
        "is_simulated",
    )
    list_filter = ("userexperiment", "is_active", "is_simulated")
    search_fields = ("userexperiment",)


@admin.register(G3Results)
class G3ResultsAdmin(admin.ModelAdmin):
    formfield_overrides = {models.JSONField: {"widget": JSONEditorWidget}}
    list_display = ("__str__",)


@admin.register(G3SimulParams)
class G3SimulParamsAdmin(admin.ModelAdmin):
    formfield_overrides = {models.JSONField: {"widget": JSONEditorWidget}}
    list_display = ("__str__",)


@admin.register(G3SimulGlobalParams)
class G3SimulGlobalParamsAdmin(admin.ModelAdmin):
    formfield_overrides = {models.JSONField: {"widget": JSONEditorWidget}}
    list_display = ("__str__",)
