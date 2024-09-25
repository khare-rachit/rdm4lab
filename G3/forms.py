"""
File location: ...G3/forms.py
Description: This file contains the forms for the G3 app.
Author: Rachit Khare
(c) 2024 RDM4Lab - all rights reserved
"""

# Django imports
from django import forms

# Application imports
from G3.models import G3Data, G3Metadata
from G3.validators import valid_file_extensions

# Third-party imports
from crispy_forms.helper import FormHelper


# ------------------------------------------
# Forms for the G3 app
# ------------------------------------------


class G3DataForm(forms.ModelForm):
    """
    This form is used to upload the data for the experiment.
    """

    file = forms.FileField(
        label="Raw Data",
        required=False,
        widget=forms.FileInput(
            attrs={
                "accept": ",".join(valid_file_extensions),
            }
        ),
        help_text=f"Upload the raw date file for this experiment.",
    )

    class Meta:
        model = G3Data
        fields = ["id", "file"]

    def __init__(self, *args, **kwargs):
        id = kwargs.pop("id", None)
        super(G3DataForm, self).__init__(*args, **kwargs)

        # Temporarily remove the file_field from the form
        file_field = self.fields.pop("file")
        # Add the metadata fields to the form
        self.add_metadata_fields()
        # Re-add the file_field at the end
        self.fields["file"] = file_field
        # Set the initial value of the id field and disable it
        self.fields["id"].initial = id
        self.fields["id"].disabled = True

    def add_metadata_fields(self):
        """
        Method to add the metadata fields to the form.
        """

        metadata = G3Metadata.objects.first()
        if not metadata:
            return

        # Sort the metadata fields based on the order
        metadata_fields = metadata.fields
        sorted_metadata_fields = dict(
            sorted(metadata_fields.items(), key=lambda item: item[1]["order"])
        )

        # Add metadata fields to the form
        for field, attrs in sorted_metadata_fields.items():
            label = (
                f"{attrs['label']} [in {attrs['unit']}]"
                if attrs["unit"]
                else attrs["label"]
            )

            if attrs["type"] == "float":
                self.fields[field] = forms.FloatField(
                    label=label,
                    required=attrs["required"],
                    help_text=attrs["description"],
                )


class G3SimulForm(forms.Form):
    """
    This form is used to input the parameters for the simulation.
    """

    def __init__(self, *args, **kwargs):
        super(G3SimulForm, self).__init__(*args, **kwargs)
        # Add the metadata fields to the form
        from G3.models import G3Metadata

        metadata = G3Metadata.objects.first()
        if not metadata:
            return

        # Sort the metadata fields based on the order
        metadata_fields = metadata.fields
        sorted_metadata_fields = dict(
            sorted(metadata_fields.items(), key=lambda item: item[1]["order"])
        )

        # Add the input and output fields to the form
        self.add_input_fields(sorted_metadata_fields)
        self.add_output_fields(sorted_metadata_fields)

    def add_input_fields(self, metadata_fields):
        """
        Method to add the input fields to the form.
        """

        # Add the input fields to the form.
        for field, attrs in metadata_fields.items():
            if attrs["scope"] == "input":
                label = (
                    f"{attrs['label']} [in {attrs['unit']}]"
                    if attrs["unit"]
                    else attrs["label"]
                )
                if attrs["type"] == "float":
                    self.fields[field] = forms.FloatField(
                        label=label,
                        required=attrs["required"],
                        help_text=attrs["description"],
                    )

    def add_output_fields(self, metadata_fields):
        """
        Method to add the output fields to the form.
        """

        # Add output fields to the form
        for field, attrs in metadata_fields.items():
            if attrs["scope"] == "result":
                label = (
                    f"{attrs['label']} [in {attrs['unit']}]"
                    if attrs["unit"]
                    else attrs["label"]
                )
                if attrs["type"] == "float":
                    self.fields[field] = forms.FloatField(
                        label=label,
                        required=False,
                        help_text=attrs["description"],
                    )
                self.fields[field].widget.attrs["readonly"] = True
