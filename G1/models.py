"""
File location: ...G1/models.py
Description: This file contains the models for the G1 experiment.
Author: Rachit Khare
(c) 2024 RDM4Lab - all rights reserved
"""

# Django imports
from django.db import models
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

# Application imports
from main.models import UserExperiment
from G1.utils import upload_G1data, upload_G1template
from G1.validators import validate_file_extension

# ------------------------------------------
# Models for the G1 experiment
# ------------------------------------------


class G1Metadata(models.Model):
    """Model for storing the metadata fields related to the G1 experiment.
    NOTE: Only one instance of this model is allowed.
    """

    # Metadata fields for the experiment.
    fields = models.JSONField(
        _("Fields"),
        default=dict,
        blank=True,
    )

    # Additional metadata fields.
    additional_fields = models.JSONField(
        _("Additional Fields"),
        default=dict,
        blank=True,
    )

    # Template file for validation.
    template = models.FileField(
        _("Template File"),
        upload_to=upload_G1template,
        validators=[validate_file_extension],
        blank=True,
    )

    class Meta:
        verbose_name = "G1 Metadata"
        verbose_name_plural = "G1 Metadata"

    def __str__(self):
        return "G1 Metadata"

    def clean(self):
        """
        Ensuring only one instance of the model is created.
        """

        if G1Metadata.objects.exists() and not self.pk:
            raise ValidationError(_("There can be only one instance of this model."))

    def save(self, *args, **kwargs):
        """
        Delete old file if new file is uploaded.
        This prevents multiple files from being stored in the database.
        """

        # Check if a template is uploaded.
        if self.template:
            # If a template is uploaded, check if there's an existing template.
            try:
                # Get the existing template from the model G1Metadata.
                existing_template = G1Metadata.objects.first().template
                if (
                    existing_template
                    and self.template
                    and existing_template != self.template
                ):
                    # Delete the old template if it doesn't match.
                    existing_template.delete(save=False)
            except existing_template.DoesNotExist:
                # If no existing template is found, no file to delete; do nothing
                pass

        # Call full_clean before saving to run the clean method.
        self.full_clean()

        return super().save(*args, **kwargs)


class G1Data(models.Model):
    """
    This model stores the data related to G1 experiment.
    One instance of this model corresponds to one data point.
    """

    # Auto-generated unique ID for the data point.
    uid = models.BigAutoField(
        primary_key=True,
    )

    # UserExperiment ID from the main.UserExperiment model.
    # Multiple data points are associated with one UserExperiment.
    userexperiment = models.ForeignKey(
        UserExperiment,
        on_delete=models.CASCADE,
        blank=False,
    )

    # Unique ID for each data point
    # NOTE: This is different from the auto-generated ID.
    id = models.PositiveIntegerField(
        _("data point #"),
        unique=True,
        blank=False,
    )

    # Raw data for each data point stored as JSON.
    raw_data = models.JSONField(
        _("Raw Data"),
        default=dict,
        blank=True,
    )

    # Processed data for each data point stored as JSON.
    proc_data = models.JSONField(
        _("Processed Data"),
        default=dict,
        blank=True,
    )

    # Raw data file for each data point.
    file = models.FileField(
        _("Data File"),
        upload_to=upload_G1data,
        validators=[validate_file_extension],
        blank=True,
    )

    # Active status for each data point.
    is_active = models.BooleanField(
        _("Active"),
        default=True,
        blank=False,
    )

    # Processed status for each data point.
    is_processed = models.BooleanField(
        _("Processed"),
        default=False,
        blank=False,
    )

    class Meta:
        ordering = ["id"]  # Order by data point ID
        unique_together = ["userexperiment", "id"]  # Ensure unique data points
        verbose_name = "G1 Data"
        verbose_name_plural = "G1 Data"

    def __str__(self):
        return f"{self.userexperiment}_{self.id}"

    def enable(self):
        """
        Enable the data point.
        """

        self.is_active = True
        self.save()

    def disable(self):
        """
        Disable the data point.
        """

        self.is_active = False
        self.save()

    def save(self, *args, **kwargs):
        """
        Delete old file if a new file is uploaded.
        This prevents multiple files from being stored in the database.
        """

        # Check if an instance already exists in the database.
        if self.pk:
            try:
                # Fetch the old instance to compare files.
                old_instance = G1Data.objects.get(pk=self.pk)
                existing_file = old_instance.file

                # If there's an existing file and it's different, delete it.
                if existing_file and self.file and existing_file != self.file:
                    existing_file.delete(save=False)
            except G1Data.DoesNotExist:
                # If no old instance is found, no file to delete; we pass.
                pass

        # Save the instance and check for any errors.
        super(G1Data, self).save(*args, **kwargs)


class G1Results(models.Model):
    """
    This model stores the data groups and results for the G1 Experiment.
    The data groups are used for performing calculations.
    NOTE: One instance per UserExperiment.
    """

    # Auto-generated unique ID.
    uid = models.BigAutoField(
        primary_key=True,
    )

    # One-to-one relationship to ensure only one instance exists
    # per userexperiment.
    userexperiment = models.OneToOneField(
        UserExperiment,
        on_delete=models.CASCADE,
        blank=False,
    )

    # Dataset containing the Ea data stored as JSON.
    ea_dicts = models.JSONField(
        _("Ea Dicts"),
        default=list,
        blank=True,
    )

    # Dataset containing the RO base data stored as JSON.
    ro_base_dicts = models.JSONField(
        _("RO Base Dicts"),
        default=list,
        blank=True,
    )

    # Dataset containing the RO ester data stored as JSON.
    ro_ester_dicts = models.JSONField(
        _("RO Ester Dicts"),
        default=list,
        blank=True,
    )

    class Meta:
        verbose_name = "G1 Results"
        verbose_name_plural = "G1 Results"

    def __str__(self):
        return f"{self.userexperiment}_Results"
