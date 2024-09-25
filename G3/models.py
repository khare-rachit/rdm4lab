"""
File location; .../G3/models.py
Description: This file contains the models for the G3 app.
Author: Rachit Khare
(c) 2024 RDM4Lab - all rights reserved
"""

# Django imports
from django.db import models
from django.utils.translation import gettext as _
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError

# Application imports
from main.models import UserExperiment
from G3.utils import upload_G3data, upload_G3template
from G3.validators import validate_file_extension

# ------------------------------------------
# Models for the G3 app
# ------------------------------------------


class G3Metadata(models.Model):
    """
    Model for storing the metadata fields and templates for the experiment.
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
        _("Template"),
        upload_to=upload_G3template,
        validators=[validate_file_extension],
        blank=True,
    )

    class Meta:
        verbose_name = "G3 Metadata"
        verbose_name_plural = "G3 Metadata"

    def __str__(self):
        return "G3 Metadata"

    def clean(self):
        """
        Ensuring only one instance of the model is created.
        """

        if G3Metadata.objects.exists() and not self.pk:
            raise ValidationError(_("There can be only one instance of this model."))

    def save(self, *args, **kwargs):
        """
        Delete the old file if new file is uploaded.
        This prevents replication of files in the media folder.
        """

        # Check if a template is uploaded.
        if self.template:
            # If the template is uploaded, check for an existing template.
            try:
                # Get the existing template from the model G1Metadata.
                existing_template = G3Metadata.objects.first().template
                if (
                    existing_template
                    and self.template
                    and existing_template != self.template
                ):
                    # Delete the old template if it doesn't match.
                    existing_template.delete(save=False)
            except existing_template.DoesNotExist:
                pass

        # Call the full clean method and check for any errors.
        self.full_clean()

        return super().save(*args, **kwargs)


class G3Data(models.Model):
    """
    This model stores the data related to G3 experiment.
    One instance of this model corresponds to one data point.
    """

    # Auto-generated unique ID for the data points.
    uid = models.AutoField(
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

    # Data file for each data point
    file = models.FileField(
        _("Data File"),
        upload_to=upload_G3data,
        validators=[validate_file_extension],
        blank=True,
    )

    # Active status for each data point.
    is_active = models.BooleanField(
        _("Active"),
        default=True,
        blank=False,
    )

    # True if the data point is simulated, False otherwise.
    is_simulated = models.BooleanField(
        _("Simulated"),
        default=False,
        blank=False,
    )

    class Meta:
        ordering = ["id"]  # Order by data point ID
        unique_together = ["userexperiment", "id"]  # Ensure unique data points
        verbose_name = "G3 Data"
        verbose_name_plural = "G3 Data"

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
        Delete the old file if a new file is uploaded.
        This prevents replication of files in the media folder.
        """
        existing_file = None

        # Check if an instance already exists in the database.
        if self.pk:
            try:
                # Fetch the old instance to compare files.
                old_instance = G3Data.objects.get(pk=self.pk)
                existing_file = old_instance.file

                # If there's an existing file and it's different, delete it.
                if existing_file and self.file and existing_file != self.file:
                    existing_file.delete(save=False)
            except G3Data.DoesNotExist:
                # If no old instance is found, no file to delete; we pass.
                pass

        # Save the instance and check for any errors.
        super(G3Data, self).save(*args, **kwargs)


class G3Results(models.Model):
    """
    This model stores the data groups and results for the G3 Experiment.
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

    # Dataset containing the rate data stored as JSON.
    rate_dicts = models.JSONField(
        _("Rate Dictionaries"),
        default=list,
        blank=True,
    )

    # Dataset containing the Ea data stored as JSON.
    ea_dicts = models.JSONField(
        _("Ea Dictionaries"),
        default=list,
        blank=True,
    )

    # Dataset containing the RO data stored as JSON.
    ro_dicts = models.JSONField(
        _("RO Dictionaries"),
        default=list,
        blank=True,
    )

    class Meta:
        verbose_name = "G3 Results"
        verbose_name_plural = "G3 Results"

    def __str__(self):
        return f"{self.userexperiment}_Results"


class G3SimulParams(models.Model):
    """
    This model stores the parameters required for simulations.
    NOTE: Only one instance is allowed per UserExperiment.
    """

    # Auto-generated unique ID.
    uid = models.BigAutoField(
        primary_key=True,
    )

    # This is a one-to-one relationship to ensure only one instance exists
    # per userexperiment.
    userexperiment = models.OneToOneField(
        UserExperiment,
        on_delete=models.CASCADE,
        blank=False,
    )

    # Dataset containing the data for simulation params calculations
    simul_dicts = models.JSONField(
        _("Simul Dictionaries"),
        default=list,
        blank=True,
    )

    # Parameters for the simulation stored as JSON.
    simul_params = models.JSONField(
        _("Parameters"),
        default=dict,
        blank=True,
    )

    class Meta:
        verbose_name = "G3 Simul Params"
        verbose_name_plural = "G3 Simul Params"

    def __str__(self):
        return f"{self.userexperiment}_SimulParams"


class G3SimulGlobalParams(models.Model):
    """
    This model stores the parameters required for simulations.
    NOTE: This model is different from the G3SimulParams model.
    If G3SimulParams is not available, then this is used.
    NOTE: Only one instance of this model is allowed.
    """

    # Parameters for the simulation stored as JSON.
    params = models.JSONField(
        _("Global Parameters"),
        default=dict,
        blank=True,
    )

    class Meta:
        verbose_name = "G3 Simul Global Params"
        verbose_name_plural = "G3 Simul Global Params"

    def __str__(self):
        return f"G3_SimulGlobalParams"
