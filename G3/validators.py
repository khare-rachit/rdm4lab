"""
File location: ...G3/validators.py
Description: This file contains custom validators for the G3 app.
Author: Rachit Khare
(c) 2024 RDM4Lab - all rights reserved
"""

# Django imports
from django.core.exceptions import ValidationError

# ------------------------------------------
# Custom validators
# ------------------------------------------

valid_file_extensions = [".csv", ".txt"]


def validate_file_extension(value):
    """
    Validate the file extension of the uploaded file.
    The valid extensions are .csv and .txt.

    Parameters:
    value (str): The file name.

    Raises:
    ValidationError: If the file extension is not supported.
    """

    if not value.name.endswith(tuple(valid_file_extensions)):
        raise ValidationError(
            f"Unsupported file extension. Allowed extensions are: "
            f"{', '.join(valid_file_extensions)}."
        )
