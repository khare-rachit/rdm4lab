"""
File location: ...G1/utils.py
Description: This file contains the utility functions for the G1 experiment.
Author: Rachit Khare
(c) 2024 RDM4Lab - all rights reserved
"""

# Global imports
from pathlib import Path
from main import ureg, Q_
from typing import List, Dict
import inspect
from . import logger

# Application imports
from G1.analysis import (
    calc_proc_data,
    perform_ea_analysis,
    perform_ro_base_analysis,
    perform_ro_ester_analysis,
)

# ------------------------------------------
# Utility functions for the G1 experiment
# ------------------------------------------


def upload_G1data(instance: object, filename: str) -> str:
    """
    Method to upload the data file to the media folder.
    Folder location: ...data/G1/{semester_id}/{username}/
    The file is renamed to G1_{username}_{datapoint}{ext} before saving.

    Parameters:
    instance (object): The instance of the G1Data model.
    filename (str): The original filename of the file.

    Returns:
    upload_path (str): The path where the file will be saved.
    """

    # Extract relevant information from the instance
    username = instance.userexperiment.student.username
    datapoint = instance.id
    semester_id = instance.userexperiment.semester.id
    ext = Path(filename).suffix  # Get the file extension

    # Generate the new filename
    new_filename = f"G1_{username}_{datapoint}{ext}"

    # Construct the full upload path
    upload_path = Path("data", "G1", str(semester_id), username, new_filename)

    return str(upload_path)


def upload_G1template(instance: object, filename: str) -> str:
    """
    Method to upload the G1 template file to the media folder.
    Folder location: ...data/G1/template/
    The file is renamed as G1_template{ext} before saving.

    Parameters:
    instance (model): The model instance.
    filename (str): The original filename.

    Returns:
    path (str): The path relative to MEDIA_ROOT to save the file.
    """

    ext = Path(filename).suffix  # Get the file extension
    # Generate the new filename
    new_filename = f"G1_template{ext}"
    # Construct the full upload path
    upload_path = Path("data", "G1", "template", new_filename)

    return str(upload_path)


def prepare_for_db_storage(data_dict: dict, metadata_fields: dict) -> dict:
    """
    Process a data dictionary and convert it to a format based on the
    metadata_fields which can be stored in the database. The metadata_fields
    are defined in the G3Metadata model.
    NOTE: All quantities are converted to base units for storage

    Parameters:
    data_dict (dict): Dictionary containing data to be converted.
    metadata_fields (dict): A list of metadata fields with their properties.

    Returns:
    db_dict (dict): A dictionary containing the processed data.
    """

    db_dict = {}

    for field, properties in metadata_fields.items():
        value = data_dict.get(field, None)
        if value is not None:
            field_type = properties["type"]
            unit = properties["unit"]
            if field_type == "float":
                value = value * ureg(unit)
                # Convert the value to base units
                value = value.to_base_units()
                value = f"{value:~}"
            db_dict[field] = value

    return db_dict


def prepare_for_html_display(data_dict: dict, metadata_fields: dict) -> dict:
    """
    Process a data dictionary and convert it to a format that can can be
    displayed in the frontend.
    NOTE: The values are converted to pretty units for display

    Parameters:
    data_dict (dict): Dictionary containing data to be converted.
    metadata_fields (dict): A list of metadata fields with their properties
                    based on which the data will be processed.

    Returns:
    html_dict (dict): A dictionary containing the processed data
                    in pretty units
    """

    html_dict = {}

    # Iterate over the metadata fields
    for field, properties in metadata_fields.items():
        # Check if the field is present in the metadata
        if field in data_dict:
            type = properties["type"]
            unit = properties["unit"]
            # Check the type of the field and assign the value accordingly
            # If the field is a float, convert it to the ureg quantity
            if type == "float":
                value = Q_(data_dict[field]).to(ureg(unit))
                value = humanize_quantity(value)
            # otherwise assign the value as it is
            else:
                value = data_dict[field]
            html_dict[field] = value
        # If the field is not present, assign None
        else:
            html_dict[field] = None

    return html_dict


def convert_to_html_format(data_dict: dict) -> dict:
    """
    Convert the data dictionary so it can be to be used in the frontend
    to display the data. The values are converted to pretty units for display.

    Parameters:
    data_dict (dict): The data containing field values.

    Returns:
    html_dict (dict): A dictionary containing the data in pretty units.
    """

    html_dict = {}

    for field, value in data_dict.items():
        # check if the value is a ureg.Quantity
        if isinstance(value, ureg.Quantity):
            html_dict[field] = humanize_quantity(value) if value is not None else None
        else:
            html_dict[field] = value

    return html_dict


def humanize_quantity(value: Q_) -> str:
    """
    Converts a Pint quantity to a human-readable string format
    using scientific notation for very small or very large values.
    If the value is not a ureg.Quantity, it is returned as a string.
    In case of an error, the value is returned as a string.

    Parameters:
    value (ureg.Quantity): The Pint quantity to format.

    Returns:
    str: The formatted string representation of the quantity.
    """

    try:
        # Check if the value is a ureg.Quantity
        if not isinstance(value, ureg.Quantity):
            # If the value is not a ureg.Quantity, return value as a string
            return str(value)
        else:
            if (
                value.dimensionless
                and value.units != ureg.percent
                and value.units != ureg.unitless
            ):
                # If the value is dimensionless and is not percent
                # return the magnitude with commas
                return f"{value.magnitude:.1f}"
            elif value.dimensionless and value.units == ureg.unitless:
                magnitude = value.magnitude
                if abs(magnitude) >= 1e5:
                    format_str = f"{{:.2e}}"
                elif abs(magnitude) < 1e5 and abs(magnitude) >= 100:
                    format_str = f"{{:.1f}}"
                elif abs(magnitude) < 100 and abs(magnitude) >= 1:
                    format_str = f"{{:.2f}}"
                elif abs(magnitude) < 1 and abs(magnitude) >= 1e-3:
                    format_str = f"{{:.4f}}"
                else:
                    format_str = f"{{:.2e}}"

                return format_str.format(magnitude)
            else:
                magnitude = value.magnitude
                if abs(magnitude) >= 1e5:
                    format_str = f"{{:.2e}} {{:~P}}"
                elif abs(magnitude) < 1e5 and abs(magnitude) >= 100:
                    format_str = f"{{:.1f}} {{:~P}}"
                elif abs(magnitude) < 100 and abs(magnitude) >= 1:
                    format_str = f"{{:.2f}} {{:~P}}"
                elif abs(magnitude) < 1 and abs(magnitude) >= 1e-3:
                    format_str = f"{{:.4f}} {{:~P}}"
                else:
                    format_str = f"{{:.2e}} {{:~P}}"

                return format_str.format(magnitude, value.units)
    except Exception as e:
        # if there is an error, return the value as a string
        return str(value)


# ------------------------------------------
# Utility functions for updating the G1Data instance
# ------------------------------------------


def upd_proc_data(instance: object, sender: object) -> None:
    """
    This function updates the proc_data dict in the G1Data instance
    based on the new raw_data that is provided.

    Parameters:
    instance (model): The G1Data model instance.
    sender (model): The model class of the instance.

    Returns:
    None
    """

    if not instance.is_processed:
        # If the instance is not processed, calculate the new proc_data
        # based on the raw_data
        proc_data = instance.proc_data
        new_proc_data = calc_proc_data(raw_data=instance.raw_data, file=instance.file)
        # Update the instance with the new proc_data
        proc_data.update((field, value) for field, value in new_proc_data.items())
        instance.proc_data = proc_data
        # Set the instance as processed
        instance.is_processed = True
        # Save the instance
        instance.save()
        # Log the update in proc_data with the instance ID
        logger.info(
            f"Updated the proc_data for {sender} id: {instance.id}",
        )
    else:
        # If the instance is already processed, do nothing
        pass


# ------------------------------------------
# Utility functions for updating the G1Results instance
# ------------------------------------------


def upd_g1results(instance: object, deleted: bool = False) -> None:
    """
    This function updates the G1Results instance based on the new or updated
    G1Data instance. This function is called after the G1Data instance is saved.

    Parameters:
    instance (model): The G1Data instance.
    deleted (bool): Flag to check if the G1Data instance is deleted or not.

    Returns:
    None
    """

    from G1.models import G1Results

    # Get the corresponding G3Results instance
    g1results = G1Results.objects.get(userexperiment=instance.userexperiment)
    # First, update the ea_dicts based on the proc_data and calculate Ea.
    upd_ea_dicts(
        proc_data=instance.proc_data, ea_dicts=g1results.ea_dicts, deleted=deleted
    )
    upd_ea(ea_dicts=g1results.ea_dicts)
    # Update the ro_base_dicts and ro_ester_dicts.
    upd_ro_base_dicts(
        proc_data=instance.proc_data,
        ro_base_dicts=g1results.ro_base_dicts,
        deleted=deleted,
    )
    upd_ro_ester_dicts(
        proc_data=instance.proc_data,
        ro_ester_dicts=g1results.ro_ester_dicts,
        deleted=deleted,
    )
    # Calculate the RO_base and RO_ester
    upd_ro_base(ro_base_dicts=g1results.ro_base_dicts)
    upd_ro_ester(ro_ester_dicts=g1results.ro_ester_dicts)
    # Save the updated G3Results instance
    g1results.save()
    # Log the update with the instance ID
    logger.info(
        f"Updated the {g1results.__class__} for UserExperiment: {instance.userexperiment}"
    )


def upd_ea_dicts(
    proc_data: list[dict], ea_dicts: list[dict], deleted: bool = False
) -> None:
    """
    Add, remove or update the rate data from proc_data to the ea_dicts.

    Parameters:
    proc_data (dict): Dictionary containing the processed data.
    ea_dicts (list): The list of dictionaries to update.

    Returns:
    None
    """

    ref_id = proc_data.get("id")
    C_base = proc_data.get("C_base")
    C_ester = proc_data.get("C_ester")

    # First remove the instance from the existing ea_dicts
    for d in ea_dicts:
        if ref_id in d.get("ref_ids"):
            # Get the id position in the dictionary.
            ref_id_pos = d.get("ref_ids").index(ref_id)
            # Remove the instance from the dictionary
            for k, v in d.items():
                if k not in ["id", "C_base", "C_ester"]:
                    if isinstance(v, list):
                        # Remove the instance from the lists
                        d[k].pop(ref_id_pos)
                    else:
                        # Set the calculated values to None
                        d[k] = None
            # Set the updated flag to True
            d["updated"] = True

    # Check if the instance is being DELETED
    if deleted is False:
        # If the instance is not being DELETED, add the instance to the
        # ea_dicts only if it is ACTIVE.
        if proc_data.get("is_active") is False:
            # If the dataset is not ACTIVE, do not add.
            pass
        else:
            # If the dataset is ACTIVE, add the instance to the
            # ea_dicts if rate is not None
            if proc_data.get("rate") is not None:
                ref_id_added = False  # Flag to check if the id is added

                for d in ea_dicts:
                    # Check if C_base and C_ester are already present in the list
                    if C_base == d.get("C_base") and C_ester == d.get("C_ester"):
                        # If C_base and C_ester are present, append the instance
                        ref_id_added = True  # Set the flag to True
                        # Append the ref_id to the ref_ids
                        d["ref_ids"].append(ref_id)

                        for k, v in d.items():
                            if k not in ["id", "C_base", "C_ester", "ref_ids"]:
                                if isinstance(v, list):
                                    # Append the instance to the lists
                                    d[k].append(proc_data.get(k))
                                else:
                                    # Set all the calculated values to None
                                    d[k] = None
                        # Set the updated flag to True
                        d["updated"] = True

                # If the C_base and C_ester were not present in any dict, create one
                if ref_id_added == False:
                    # Get the max_ID from the existing ea_dicts
                    max_id = max(d["id"] for d in ea_dicts) if ea_dicts else 0
                    # Create a new dictionary with the instance
                    d = {
                        "id": max_id + 1,
                        "ref_ids": [ref_id],
                        "C_base": C_base,
                        "C_ester": C_ester,
                        "error": None,
                    }
                    for k in ["T_reaction", "rate"]:
                        d[k] = (
                            [proc_data.get(k)]
                            if proc_data.get(k) is not None
                            else [None]
                        )
                    # Set the updated flag to True
                    d["updated"] = True
                    # Append the dictionary to the ea_dicts
                    ea_dicts.append(d)
            else:
                # If the rate is None, do nothing.
                pass


def upd_ea(ea_dicts: list[dict]) -> None:
    """
    This function calculates the activation energy (Ea) for ea_dict
    based on if they been updated or not. The Ea is calculated if there
    are more than 3 points in the dataset with different T_reactor values.

    Parameters:
    ea_dicts (list): ea_dicts from the G3Results instance.

    Returns:
    None
    """

    for d in ea_dicts:
        # Get the updated flag from the dictionary.
        updated = d.get("updated")
        # Check if the dataset was UPDATED.
        if updated is True:
            # If the dataset was UPDATED, calculate the activation energy
            # if the conditions are met.
            T_reaction = d.get("T_reaction")
            if len(set(T_reaction)) >= 2:
                # If the number of independent points is more than two,
                # perform Ea analysis and add to the ea_dict
                perform_ea_analysis(d)
            else:
                # If the number of points is less than 3, set the Ea to None
                d["Ea"] = None
                d["A_app"] = None
            # Set the updated flag to False
            d["updated"] = False
        else:
            # If the dataset was NOT UPDATED, do nothing.
            pass


def upd_ro_base_dicts(
    proc_data: list[dict], ro_base_dicts: list[dict], deleted: bool = False
) -> None:
    """
    Add, remove or update the rate data from proc_data to the ro_base_dicts.

    Parameters:
    proc_data (dict): Dictionary containing the processed data.
    ea_dicts (list): The list of dictionaries to update.

    Returns:
    None
    """

    ref_id = proc_data.get("id")
    T_reaction = proc_data.get("T_reaction")
    C_ester = proc_data.get("C_ester")

    # First remove the instance from the existing ea_dicts
    for d in ro_base_dicts:
        if ref_id in d.get("ref_ids"):
            # Get the id position in the dictionary.
            ref_id_pos = d.get("ref_ids").index(ref_id)
            # Remove the instance from the dictionary
            for k, v in d.items():
                if k not in ["id", "T_reaction", "C_ester"]:
                    if isinstance(v, list):
                        # Remove the instance from the lists
                        d[k].pop(ref_id_pos)
                    else:
                        # Set the calculated values to None
                        d[k] = None
            # Set the updated flag to True
            d["updated"] = True

    # Check if the instance is being DELETED
    if deleted is False:
        # If the instance is not being DELETED, add the instance to the
        # ea_dicts only if it is ACTIVE.
        if proc_data.get("is_active") is False:
            # If the dataset is not ACTIVE, do not add.
            pass
        else:
            # If the dataset is ACTIVE, add the instance to the
            # ea_dicts if rate is not None
            if proc_data.get("rate") is not None:
                ref_id_added = False  # Flag to check if the id is added

                for d in ro_base_dicts:
                    # Check if C_base and C_ester are already present in the list
                    if T_reaction == d.get("T_reaction") and C_ester == d.get(
                        "C_ester"
                    ):
                        # If C_base and C_ester are present, append the instance
                        ref_id_added = True  # Set the flag to True
                        # Append the ref_id to the ref_ids
                        d["ref_ids"].append(ref_id)

                        for k, v in d.items():
                            if k not in ["id", "T_reaction", "C_ester", "ref_ids"]:
                                if isinstance(v, list):
                                    # Append the instance to the lists
                                    d[k].append(proc_data.get(k))
                                else:
                                    # Set all the calculated values to None
                                    d[k] = None
                        # Set the updated flag to True
                        d["updated"] = True

                # If the C_base and C_ester were not present in any dict, create one
                if ref_id_added == False:
                    # Get the max_ID from the existing ea_dicts
                    max_id = max(d["id"] for d in ro_base_dicts) if ro_base_dicts else 0
                    # Create a new dictionary with the instance
                    d = {
                        "id": max_id + 1,
                        "ref_ids": [ref_id],
                        "T_reaction": T_reaction,
                        "C_ester": C_ester,
                        "error": None,
                    }
                    for k in ["C_base", "rate"]:
                        d[k] = (
                            [proc_data.get(k)]
                            if proc_data.get(k) is not None
                            else [None]
                        )
                    # Set the updated flag to True
                    d["updated"] = True
                    # Append the dictionary to the ea_dicts
                    ro_base_dicts.append(d)
            else:
                # If the rate is None, do nothing.
                pass


def upd_ro_base(ro_base_dicts: list[dict]) -> None:
    """
    This function calculates the reaction order in base (RO_base) for ro_dicts
    based on if they been updated or not. The RO is calculated if there
    are more than 3 points in the dataset with different pressure values.

    Parameters:
    ro_base_dicts (list): ro_base_dicts from the G1Results instance.

    Returns:
    None
    """

    for d in ro_base_dicts:
        # Get the updated flag from the dictionary.
        updated = d.get("updated")
        # Check if the dataset was UPDATED.
        if updated is True:
            # If the dataset was UPDATED, calculate the activation energy
            # if the conditions are met.
            C_base = d.get("C_base")
            if len(set(C_base)) >= 2:
                # If the number of independent points is more than two,
                # perform RO analysis and add to the ea_dict
                perform_ro_base_analysis(ro_base_dict=d)
            else:
                # If the number of points is less than 3, set the r_order to None
                d["ro_base"] = None
            # Set the updated flag to False
            d["updated"] = False
        else:
            # If the dataset was NOT UPDATED, do nothing.
            pass


def upd_ro_ester_dicts(
    proc_data: list[dict], ro_ester_dicts: list[dict], deleted: bool = False
) -> None:
    """
    Add, remove or update the rate data from proc_data to the ro_base_dicts.

    Parameters:
    proc_data (dict): Dictionary containing the processed data.
    ea_dicts (list): The list of dictionaries to update.

    Returns:
    None
    """

    ref_id = proc_data.get("id")
    T_reaction = proc_data.get("T_reaction")
    C_base = proc_data.get("C_base")

    # First remove the instance from the existing ea_dicts
    for d in ro_ester_dicts:
        if ref_id in d.get("ref_ids"):
            # Get the id position in the dictionary.
            ref_id_pos = d.get("ref_ids").index(ref_id)
            # Remove the instance from the dictionary
            for k, v in d.items():
                if k not in ["id", "T_reaction", "C_base"]:
                    if isinstance(v, list):
                        # Remove the instance from the lists
                        d[k].pop(ref_id_pos)
                    else:
                        # Set the calculated values to None
                        d[k] = None
            # Set the updated flag to True
            d["updated"] = True

    # Check if the instance is being DELETED
    if deleted is False:
        # If the instance is not being DELETED, add the instance to the
        # ea_dicts only if it is ACTIVE.
        if proc_data.get("is_active") is False:
            # If the dataset is not ACTIVE, do not add.
            pass
        else:
            # If the dataset is ACTIVE, add the instance to the
            # ea_dicts if rate is not None
            if proc_data.get("rate") is not None:
                ref_id_added = False  # Flag to check if the id is added

                for d in ro_ester_dicts:
                    # Check if C_base and C_ester are already present in the list
                    if T_reaction == d.get("T_reaction") and C_base == d.get("C_base"):
                        # If C_base and C_ester are present, append the instance
                        ref_id_added = True  # Set the flag to True
                        # Append the ref_id to the ref_ids
                        d["ref_ids"].append(ref_id)

                        for k, v in d.items():
                            if k not in ["id", "T_reaction", "C_base", "ref_ids"]:
                                if isinstance(v, list):
                                    # Append the instance to the lists
                                    d[k].append(proc_data.get(k))
                                else:
                                    # Set all the calculated values to None
                                    d[k] = None
                        # Set the updated flag to True
                        d["updated"] = True

                # If the C_base and C_ester were not present in any dict, create one
                if ref_id_added == False:
                    # Get the max_ID from the existing ea_dicts
                    max_id = (
                        max(d["id"] for d in ro_ester_dicts) if ro_ester_dicts else 0
                    )
                    # Create a new dictionary with the instance
                    d = {
                        "id": max_id + 1,
                        "ref_ids": [ref_id],
                        "T_reaction": T_reaction,
                        "C_base": C_base,
                        "error": None,
                    }
                    for k in ["C_ester", "rate"]:
                        d[k] = (
                            [proc_data.get(k)]
                            if proc_data.get(k) is not None
                            else [None]
                        )
                    # Set the updated flag to True
                    d["updated"] = True
                    # Append the dictionary to the ea_dicts
                    ro_ester_dicts.append(d)
            else:
                # If the rate is None, do nothing.
                pass


def upd_ro_ester(ro_ester_dicts: list[dict]) -> None:
    """
    This function calculates the reaction order in ester (RO_ester) for ro_dicts
    based on if they been updated or not. The RO is calculated if there
    are more than 3 points in the dataset with different pressure values.

    Parameters:
    ro_ester_dicts (list): ro_ester_dicts from the G1Results instance.

    Returns:
    None
    """

    for d in ro_ester_dicts:
        # Get the updated flag from the dictionary.
        updated = d.get("updated")
        # Check if the dataset was UPDATED.
        if updated is True:
            # If the dataset was UPDATED, calculate the activation energy
            # if the conditions are met.
            C_ester = d.get("C_ester")
            if len(set(C_ester)) >= 2:
                # If the number of independent points is more than two,
                # perform RO analysis and add to the ea_dict
                perform_ro_ester_analysis(ro_ester_dict=d)
            else:
                # If the number of points is less than 3, set the r_order to None
                d["ro_ester"] = None
            # Set the updated flag to False
            d["updated"] = False
        else:
            # If the dataset was NOT UPDATED, do nothing.
            pass
