"""
File location: ...G1/forms.py
Description: This file contains the forms for the G1 app.
Author: Rachit Khare
(c) 2024 RDM4Lab - all rights reserved
"""

# Django imports
from django import forms
from django.utils.translation import gettext as _
from django.utils.safestring import mark_safe

# Application imports
from G1.models import G1Data, G1Metadata
from G1.validators import valid_file_extensions

# Third-party imports
import pandas as pd


class G1DataForm(forms.ModelForm):
    file = forms.FileField(
        label="Upload data file",
        required=True,
        widget=forms.FileInput(
            attrs={
                "accept": ",".join(valid_file_extensions),
            }
        ),
        help_text=_("Download the file template <a href='#'>here</a>."),
    )

    class Meta:
        model = G1Data
        fields = ["id", "file"]

    def __init__(self, *args, **kwargs):
        template_url = kwargs.pop("template_url", "#")
        id = kwargs.pop("id", None)
        super(G1DataForm, self).__init__(*args, **kwargs)

        # Temporarily remove the file field from the form
        file_field = self.fields.pop("file")
        # Add the metadata fields to the form
        self.add_metadata_fields()
        # Re-add the file field at the end
        self.fields["file"] = file_field
        # Add the help text to the file field with file download url
        self.fields["file"].help_text = mark_safe(
            _("Download the file template <a href='{url}'>here</a>.").format(
                url=template_url
            )
        )
        # Set the initial value of the id field and disable it
        self.fields["id"].initial = id
        self.fields["id"].disabled = True

    def add_metadata_fields(self):
        """
        Method to add the metadata fields to the form.
        """

        from G1.models import G1Metadata

        metadata = G1Metadata.objects.first()
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

    def clean(self):
        cleaned_data = super().clean()
        # Get the metadata fields from the G1Metadata model
        try:
            template = G1Metadata.objects.first().template
        except:
            # If the template is not found, set it to None
            template = None

        if template is not None:
            # If the template is found, check if the uploaded file matches the template
            file = cleaned_data.get("file")
            # Read the uploaded file and the template file
            xlsfile = pd.ExcelFile(file)
            xlstemplate = pd.ExcelFile(template)

            # Check if the sheet names are the same.
            if set(xlsfile.sheet_names) != set(xlstemplate.sheet_names):
                raise forms.ValidationError(
                    _(
                        "Please upload the correct file type based on the template for this experiment. The sheet names do not match."
                    )
                )
            else:
                # For each sheet in the excel file - check if the columns are the same
                for sheet in xlsfile.sheet_names:
                    xlsdata = pd.read_excel(xlsfile, sheet_name=sheet, header=1)
                    xlstemplatedata = pd.read_excel(
                        xlstemplate, sheet_name=sheet, header=1
                    )
                    if set(xlsdata.columns) != set(xlstemplatedata.columns):
                        raise forms.ValidationError(
                            _(
                                "Please upload the correct file type based on the template for this experiment. The column names do not match."
                            )
                        )
