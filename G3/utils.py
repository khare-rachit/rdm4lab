"""
File location: ...G3/utils.py
Description: This file contains utility functions for the G3 app.
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
from G3.analysis import (
    calc_proc_data,
    perform_rate_analysis,
    perform_ea_analysis,
    perform_ro_analysis,
)
from G3.simulations import calc_p_to_A_factor, calc_kinetic_params

# ------------------------------------------
# Utility functions and methods for the G3 app
# ------------------------------------------


def upload_G3data(instance: object, filename: str) -> str:
    """
    Method to upload the data file to the media folder.
    Folder location: ...data/G3/{semester_id}/{username}/
    The file is renamed to G3_{username}_{datapoint}{ext} before saving.

    Parameters:
    instance (model): The model instance.
    filename (str): The original filename.

    Returns:
    path (str): The path relative to MEDIA_ROOT to save the file.
    """

    # Extract relevant information from the instance
    username = instance.userexperiment.student.username
    datapoint = instance.id
    semester_id = instance.userexperiment.semester.id
    ext = Path(filename).suffix  # Get the file extension

    # Generate the new filename
    new_filename = f"G3_{username}_{datapoint}{ext}"

    # Construct the full upload path
    upload_path = Path("data", "G3", str(semester_id), username, new_filename)

    return str(upload_path)


def upload_G3template(instance: object, filename: str) -> str:
    """
    Method to upload the G3 template file to the media folder.
    Folder location: ...data/G3/template/
    The file is renamed as G3_template{ext} before saving.

    Parameters:
    instance (model): The model instance.
    filename (str): The original filename.

    Returns:
    path (str): The path relative to MEDIA_ROOT to save the file.
    """

    ext = Path(filename).suffix  # Get the file extension
    # Generate the new filename
    new_filename = f"G3_template{ext}"
    # Construct the full upload path
    upload_path = Path("data", "G3", "template", new_filename)

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


def group_dicts_by_keys(
    dicts: List[Dict], keys: List[str], min_points: int = 3
) -> Dict:
    """
    Group a list of dicts by specified keys where those keys have identical
    values.

    Parameters:
    dicts (list): List of dictionaries.
    keys (list): List of keys to group by.
    min_points (int): Minimum number of datasets required to form a group.
                default value is 3.

    Returns:
    grouped (dict): A dictionary where the key is the tuple of
    values of the selected keys, and the value is a list of
    dictionaries that match those key values.
    """

    grouped = {}

    # Iterate over the dictionaries
    for idx, d in enumerate(dicts):
        # Create a tuple of values based on the specified keys
        key_tuple = tuple(d[key] for key in keys if key in d)
        # Check if the key_tuple is present in the grouped dictionary
        if key_tuple in grouped:
            # If the key_tuple is present, append the dictionary to the list
            grouped[key_tuple].append(d)
        else:
            # If the key_tuple is not present,
            # create a new list with the dictionary
            grouped[key_tuple] = [d]

    # Filter groups to return only those with more than one dictionary
    return {k: v for k, v in grouped.items() if len(v) >= min_points}


# ------------------------------------------
# Utility functions for updating the G3Model instance
# ------------------------------------------


def upd_proc_data(instance: object, sender: object) -> None:
    """
    This function updates the proc_data dictionary in the G3Data instance
    based on the new raw_data that is provided. This does not save the
    instance to the database.

    Parameters:
    instance (model): The G3Data model instance.
    sender (model): The model class of the instance.

    Returns:
    None
    """

    # Check if the instance is being created or updated.
    if instance.pk:
        # if the instance is being updated, check if the raw_data has changed
        # or if the active status has changed
        raw_data = sender.objects.get(pk=instance.pk).raw_data
        is_active = sender.objects.get(pk=instance.pk).is_active
        if raw_data != instance.raw_data or is_active != instance.is_active:
            # If raw_data is DIFFERENT or is_active has CHANGED,
            # calculate the new proc_data
            proc_data = sender.objects.get(pk=instance.pk).proc_data
            new_proc_data = calc_proc_data(
                raw_data=instance.raw_data,
            )
            # Update the instance with the new proc_data
            proc_data.update((field, value) for field, value in new_proc_data.items())
            instance.proc_data = proc_data
            # Log the update in proc_data with the instance ID
            logger.info(
                f"updated the proc_data for {sender} id: {instance.id}",
            )
        else:
            # If the raw_data is not DIFFERENT or is_active has NOT CHANGED,
            # do nothing
            pass
    else:
        # If a new instance is being CREATED, calculate the proc_data directly
        proc_data = calc_proc_data(
            raw_data=instance.raw_data,
        )
        instance.proc_data = proc_data
        # Log the update with the instance ID
        logger.info(f"created proc_data for {sender} id: {instance.id}")


# ------------------------------------------
# Functions for updating the G3Results instance
# ------------------------------------------


def upd_g3results(instance: object, deleted: bool = False) -> None:
    """
    This function updates the G3Results instance based on the new or updated
    G3Data instance. This function is called after the G3Data instance is saved.

    Parameters:
    instance (model): The G3Data instance.
    deleted (bool): Flag to check if the G3Data instance is deleted or not.

    Returns:
    None
    """

    from G3.models import G3Results

    # Get the proc_data from the G3Data instance
    proc_data = instance.proc_data
    # Get the corresponding G3Results instance
    g3results = G3Results.objects.get(userexperiment=instance.userexperiment)

    # First, update the rate_dicts.
    upd_rate_dicts(
        proc_data=proc_data, rate_dicts=g3results.rate_dicts, deleted=deleted
    )
    # Then, recalculate the rates based on the updated rate_dicts.
    upd_rates(rate_dicts=g3results.rate_dicts)
    # Update the ea_dicts based on the updated rate_dicts and recalculate Ea.
    upd_ea_dicts(rate_dicts=g3results.rate_dicts, ea_dicts=g3results.ea_dicts)
    upd_ea(ea_dicts=g3results.ea_dicts)
    # Update the ro_dicts based on the updated rate_dicts and recalculate RO.
    upd_ro_dicts(rate_dicts=g3results.rate_dicts, ro_dicts=g3results.ro_dicts)
    upd_ro(ro_dicts=g3results.ro_dicts)
    # Save the updated G3Results instance
    g3results.save()
    # Log the update with the instance ID
    logger.info(
        f"Updated the {g3results.__class__} for UserExperiment: {instance.userexperiment}"
    )


def upd_rate_dicts(
    proc_data: dict, rate_dicts: list[dict], deleted: bool = False
) -> None:
    """
    Add, remove or update the proc_data in the rate_dicts.

    Parameters:
    proc_data (dict): The proc_data dictionary from the G3Data instance.
    rate_dicts (list): The rate_dicts from the G3Results instance to update.

    Returns:
    None
    """

    # Extract the instance ID (ref_id), p, and T_reactor from the proc_data
    ref_id = proc_data.get("id")
    p = proc_data.get("p")
    T_reactor = proc_data.get("T_reactor")

    # First REMOVE the instance ID from the existing rate_dicts
    for d in rate_dicts:
        # Check if the instance ID is present in the ref_ids
        ref_ids = d.get("ref_ids")
        if ref_id in ref_ids:
            # If present, get the ref_id position in the dictionary.
            ref_id_pos = ref_ids.index(ref_id)
            # Remove the instance data from the dictionary.
            for k, v in d.items():
                if k not in ["id", "p", "T_reactor"]:
                    if isinstance(v, list):
                        # Remove the ref_id from all the lists.
                        d[k].pop(ref_id_pos)
                    else:
                        # Set all the calculated values to None.
                        d[k] = None
            # Set the updated flag to True.
            d["updated"] = True

    # Check if the instance is being DELETED
    if deleted is False:
        # If the instance is not being DELETED, add the instance to the
        # rate_dicts only if it is ACTIVE.
        if proc_data.get("is_active") is False:
            # If the dataset is not ACTIVE, do not add.
            pass
        else:
            # If the dataset is ACTIVE, add the instance ID to the rate_dicts
            ref_id_added = False  # Flag to check if the instance was added

            for d in rate_dicts:
                # Check if the p and T_reactor are already present in the list
                if p == d.get("p") and T_reactor == d.get("T_reactor"):
                    ref_id_added = True  # Set the flag to True
                    # Add the instance to the updated_dicts
                    d["ref_ids"].append(ref_id)

                    for k, v in d.items():
                        if k not in ["id", "p", "T_reactor", "ref_ids"]:
                            if isinstance(v, list):
                                # Append the data to the dictionary
                                d[k].append(proc_data.get(k))
                            else:
                                # Set all the calculated values to None
                                d[k] = None
                    # Set the updated flag to True
                    d["updated"] = True

            # If the p and T_reactor were not presnet in the list, create a new dict
            if not ref_id_added:
                # Get the max_ID value from the existing rate_dicts
                max_id = max(d["id"] for d in rate_dicts) if rate_dicts else 0
                # Create a new dictionary with the instance
                d = {
                    "id": max_id + 1,
                    "ref_ids": [ref_id],
                    "p": p,
                    "T_reactor": T_reactor,
                    "error": None,
                }
                # Add the proc_data to the dictionary
                for k in ["tau", "conversion", "is_active", "is_simulated"]:
                    d[k] = (
                        [proc_data.get(k)] if proc_data.get(k) is not None else [None]
                    )
                # Set the updated flag to True
                d["updated"] = True
                # Append the dictionary to the rate_dicts
                rate_dicts.append(d)
    else:
        # If the instance is being DELETED, do nothing
        pass


def upd_rates(rate_dicts: list[dict]) -> None:
    """
    This function calculates the rates and plot data for the rate_dicts
    based on if they been updated or not. The rate is calculated if there
    are more than 3 points in the dataset different tau values and same
    p and T_reactor values.

    Parameters:
    rate_dicts (list): rate_dicts from the G3Results instance.

    Returns:
    None
    """

    for d in rate_dicts:
        # Get the updated flag from the dictionary
        updated = d.get("updated")
        # Check if the dataset was UPDATED
        if updated is True:
            # If the dataset was UPDATED, calculate the rate if the conditions are met.
            tau = d.get("tau")
            if len(set(tau)) >= 1:
                # If the number of uniques points are at least 1, calculate the rate
                perform_rate_analysis(rate_dict=d)
            else:
                # If the number of points is less than 3, set the rate to None
                d["rate"] = None


def upd_ea_dicts(rate_dicts: list[dict], ea_dicts: list[dict]) -> None:
    """
    Add, remove or update the rate data in ea_dicts.

    Parameters:
    rate_dicts (dict): Dictionary containing the rate data.
    ea_dicts (list): The list of dictionaries to update.

    Returns:
    None
    """

    for r in rate_dicts:
        # Get the updated flag from the dictionary
        updated = r.get("updated")
        # Check if the dataset was UPDATED
        if updated is True:
            # If the dataset was UPDATED, update it in the ea_dicts
            ref_id = r.get("id")
            p = r.get("p")

            # First remove the instance from the existing ea_dicts
            for d in ea_dicts:
                if ref_id in d.get("ref_ids"):
                    # Get the id position in the dictionary.
                    ref_id_pos = d.get("ref_ids").index(ref_id)
                    # Remove the instance from the dictionary
                    for k, v in d.items():
                        if k not in ["id", "p"]:
                            if isinstance(v, list):
                                # Remove the instance from the lists
                                d[k].pop(ref_id_pos)
                            else:
                                # Set the calculated values to None
                                d[k] = None
                    # Set the updated flag to True
                    d["updated"] = True

            # Then, add the instance to the rate_dicts if rate is not None
            if r.get("rate") is not None and r.get("error") is None:
                ref_id_added = False  # Flag to check if the id is added
                is_simulated = any(r.get("is_simulated"))

                for d in ea_dicts:
                    # Check if p (pressure) is already present in the list
                    if p == d.get("p"):
                        # If p is present, append the instance to this dict
                        ref_id_added = True  # Set the flag to True
                        # Append the ref_id to the ref_ids
                        d["ref_ids"].append(ref_id)

                        for k, v in d.items():
                            if k not in ["id", "p", "ref_ids"]:
                                if isinstance(v, list):
                                    # Append the instance to the lists
                                    d[k].append(r.get(k))
                                else:
                                    # Set all the calculated values to None
                                    d[k] = None
                        # Set the updated flag to True
                        d["updated"] = True
                        # Set the is_simulated flag
                        d["is_simulated"] = is_simulated

                # If the p was not present in any dict, create a new dict
                if ref_id_added == False:
                    # Get the max_ID from the existing ea_dicts
                    max_id = max(d["id"] for d in ea_dicts) if ea_dicts else 0
                    # Create a new dictionary with the instance
                    d = {
                        "id": max_id + 1,
                        "ref_ids": [ref_id],
                        "p": p,
                        "error": None,
                    }
                    for k in ["T_reactor", "rate"]:
                        d[k] = [r.get(k)] if r.get(k) is not None else [None]
                    # Set the updated flag to True
                    d["updated"] = True
                    # Set the is_simulated flag
                    d["is_simulated"] = is_simulated
                    # Append the dictionary to the ea_dicts
                    ea_dicts.append(d)
            else:
                # If the rate is None, do nothing.
                pass
        else:
            # If the dataset was NOT UPDATED, do nothing.
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
            T_reactor = d.get("T_reactor")
            if len(set(T_reactor)) >= 2:
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


def upd_ro_dicts(rate_dicts: list[dict], ro_dicts: list[dict]) -> None:
    """
    Add, remove or update the updated rate data from ro_dicts in
    G3Results instance.

    Parameters:
    rate_dicts (dict): Dictionary containing the rate data.
    ro_dicts (list): The list of dictionaries to update.

    Returns:
    None
    """

    for r in rate_dicts:
        # Get the updated flag from the dictionary
        updated = r.get("updated")
        # Check if the dataset was UPDATED
        if updated is True:
            # Set the updated flag to False
            r["updated"] = False
            # If the dataset was UPDATED, update it in the ea_dicts
            ref_id = r.get("id")
            T_reactor = r.get("T_reactor")

            # First remove the instance from the existing ea_dicts
            for d in ro_dicts:
                if ref_id in d.get("ref_ids"):
                    # Get the id position in the dictionary.
                    ref_id_pos = d.get("ref_ids").index(ref_id)
                    # Remove the instance from the dictionary
                    for k, v in d.items():
                        if k not in ["id", "T_reactor"]:
                            if isinstance(v, list):
                                # Remove the instance from the lists
                                d[k].pop(ref_id_pos)
                            else:
                                # Set the calculated values to None
                                d[k] = None
                    # Set the updated flag to True
                    d["updated"] = True

            # Then, add the instance to the rate_dicts if rate is not None
            if r.get("rate") is not None and r.get("error") is None:
                ref_id_added = False  # Flag to check if the id is added
                is_simulated = any(r.get("is_simulated"))

                for d in ro_dicts:
                    # Check if p (pressure) is already present in the list
                    if T_reactor == d.get("T_reactor"):
                        # If p is present, append the instance to this dict
                        ref_id_added = True  # Set the flag to True
                        # Append the ref_id to the ref_ids
                        d["ref_ids"].append(ref_id)

                        for k, v in d.items():
                            if k not in ["id", "T_reactor", "ref_ids"]:
                                if isinstance(v, list):
                                    # Append the instance to the lists
                                    d[k].append(r.get(k))
                                else:
                                    # Set all the calculated values to None
                                    d[k] = None
                        # Set the updated flag to True
                        d["updated"] = True
                        # Set the is_simulated flag
                        d["is_simulated"] = is_simulated

                # If the p was not present in any dict, create a new dict
                if ref_id_added == False:
                    # Get the max_ID from the existing ro_dicts
                    max_id = max(d["id"] for d in ro_dicts) if ro_dicts else 0
                    # Create a new dictionary with the instance
                    d = {
                        "id": max_id + 1,
                        "ref_ids": [ref_id],
                        "T_reactor": T_reactor,
                        "error": None,
                    }
                    for k in ["p", "rate"]:
                        d[k] = [r.get(k)] if r.get(k) is not None else [None]
                    # Set the updated flag to True
                    d["updated"] = True
                    # Set the is_simulated flag
                    d["is_simulated"] = is_simulated
                    # Append the dictionary to the ea_dicts
                    ro_dicts.append(d)
            else:
                # If the rate is None, do nothing.
                pass
        else:
            # If the dataset was NOT UPDATED, do nothing.
            pass


def upd_ro(ro_dicts: list[dict]) -> None:
    """
    This function calculates the reaction order in reactant (RO) for ro_dicts
    based on if they been updated or not. The RO is calculated if there
    are more than 3 points in the dataset with different pressure values.

    Parameters:
    ro_dicts (list): ea_dicts from the G3Results instance.

    Returns:
    None
    """

    for d in ro_dicts:
        # Get the updated flag from the dictionary.
        updated = d.get("updated")
        # Check if the dataset was UPDATED.
        if updated is True:
            # If the dataset was UPDATED, calculate the activation energy
            # if the conditions are met.
            p = d.get("p")
            if len(set(p)) >= 2:
                # If the number of independent points is more than two,
                # perform RO analysis and add to the ea_dict
                perform_ro_analysis(d)
            else:
                # If the number of points is less than 3, set the r_order to None
                d["r_order"] = None
            # Set the updated flag to False
            d["updated"] = False
        else:
            # If the dataset was NOT UPDATED, do nothing.
            pass


# ------------------------------------------
# Functions for updating the G3SimulParams instance
# ------------------------------------------


def upd_g3simulparams(instance: object, deleted: bool = False) -> None:
    """
    This function updates the G3SimulParams instance based on the new or updated
    G3Data instance. This function is called after the G3Data instance is saved.

    Parameters:
    instance (model): The G3Data instance.
    deleted (bool): Flag to check if the G3Data instance is deleted or not.

    Returns:
    None
    """

    from G3.models import G3SimulParams

    # Get the corresponding G3SimulParams instance
    g3simulparams = G3SimulParams.objects.get(userexperiment=instance.userexperiment)
    # Update the simul_dicts based on the new proc_data.
    upd_simul_dicts(
        instance=instance, simul_dicts=g3simulparams.simul_dicts, deleted=deleted
    )
    # Calculate the p_to_A_factor and add to the simul_params
    upd_p_to_A_params(
        simul_dicts=g3simulparams.simul_dicts, simul_params=g3simulparams.simul_params
    )
    # Update the kinetic parameters based on the updated simul_dicts
    upd_kinetic_params(
        instance=instance,
        simul_dicts=g3simulparams.simul_dicts,
        simul_params=g3simulparams.simul_params,
    )
    # Save the updated G3SimulParams instance
    g3simulparams.save()
    # Log the update with the instance ID
    logger.info(
        f"Updated the {g3simulparams.__class__} for UserExperiment: {instance.userexperiment}"
    )


def upd_simul_dicts(instance: object, simul_dicts: dict, deleted: bool = False) -> None:
    """
    This function updates the simul_dicts dicitonary in the G3SimulParams
    based on the new or updated G3Data instance.

    Parameters:
    instance (model): The G3Data model instance.
    simul_dicts (dict): The simul_dicts dictionary from the G3SimulParams instance.
    deleted (bool): Flag to check if the instance is being deleted.

    Returns:
    None
    """

    # Get the raw_data and proc_data from the G3Data instance
    raw_data = instance.raw_data
    proc_data = instance.proc_data
    ref_id = proc_data.get("id")
    # Combine the raw_data and proc_data into a single dictionary
    data = raw_data.copy()
    data.update(proc_data)
    data.pop("id")

    # Check if the simul_dicts exists or is empty and the instance is not being deleted.
    if not simul_dicts:
        # If the dictionary is empty, create a new dictionary
        if data.get("is_active") is False:
            # If the dataset is not ACTIVE, do not add.
            pass
        else:
            # If the dataset is ACTIVE, create a new dictionary
            simul_dicts.update(
                {
                    "ref_ids": [ref_id],
                    "updated": True,
                }
            )
            for k, v in data.items():
                simul_dicts[k] = [v]
    else:
        # First REMOVE the instance ID from the existing rate_dicts, if it exists
        # Check if the instance ID is present in the ref_ids
        ref_ids = simul_dicts.get("ref_ids")
        if ref_id in ref_ids:
            # If present, get the ref_id position in the dictionary.
            ref_id_pos = ref_ids.index(ref_id)
            # Remove the instance data from the dictionary.
            for k, v in simul_dicts.items():
                if k not in ["id"]:
                    if isinstance(v, list):
                        # Remove the instance ID from the lists.
                        simul_dicts[k].pop(ref_id_pos)
            # Set the updated flag to True.
            simul_dicts["updated"] = True

        # Check if the instance is being DELETED
        if deleted is True:
            # If the instance is being DELETED, do nothing
            pass
        else:
            # If the instance is not being DELETED, add the instance to the
            # rate_dicts only if it is ACTIVE.
            if data.get("is_active") is False:
                # If the dataset is not ACTIVE, do not add.
                pass
            else:
                # Add the instance to the simul_dicts
                simul_dicts["ref_ids"].append(ref_id)

                for k, v in simul_dicts.items():
                    if k not in ["ref_ids"]:
                        if isinstance(v, list):
                            # Append the data to the dictionary
                            simul_dicts[k].append(data.get(k))
                # Set the updated flag to True
                simul_dicts["updated"] = True


def upd_p_to_A_params(simul_dicts: dict, simul_params: dict) -> None:
    """
    Function to update the p_to_A factor and add to the simul_params dictionary
    based on the new or updated G3Data instances.

    Parameters:
    simul_dicts (dict): Dictionary containing the data.
    simul_params (dict): Dictionary containing the simulation parameters.

    Returns:
    None
    """

    # Check if the dictionary is UPDATED
    if simul_dicts.get("updated") is True:
        # If the dictionary was UPDATED, calculate the p_to_A_factor
        # First, initialize the values to None
        p_to_A_factor, r_squared = None, None
        # Extract the values from the simul_dicts and convert to magnitude
        p = simul_dicts.get("p")
        A_reactant = simul_dicts.get("A_reactant")
        p = [Q_(x).magnitude for x in p] if p else []
        A_reactant = [Q_(x).magnitude for x in A_reactant] if A_reactant else []
        # Check if the number of points is more than 2
        if len(set(p)) > 2:
            # If the number of points is more than 2, calculate the p_to_A_factor

            try:
                # Calculate the p_to_A_factor and add to the simul_params
                p_to_A_factor, r_squared = calc_p_to_A_factor(p, A_reactant)
                p_to_A_factor = p_to_A_factor * ureg("1/Pa")
            except Exception as e:
                # Log the error if there is an exception, and do nothing
                print(f"Error in {inspect.currentframe().f_code.co_name}: {e}")
        else:
            # If the number of points is less than 3, do nothing
            pass

        # Update the simul_params with the new p_to_A_factor
        simul_params["p_to_A_params"] = {
            "p_to_A_factor": f"{p_to_A_factor:.5ue~}" if p_to_A_factor else None,
            "r_squared": f"{r_squared}" if r_squared else None,
        }


def upd_kinetic_params(instance: object, simul_dicts: dict, simul_params: dict) -> None:
    """
    Function to calculate the rate equation parameters for G3 experiment
    and add to the simul_params dictionary.

    Parameters:
    simul_dicts (dict): Dictionary containing the data.
    simul_params (dict): Dictionary containing the simulation parameters.

    Returns:
    None
    """

    # Check if the simul_dicts is UPDATED
    if simul_dicts.get("updated") is True:
        # Set the updated flag to False
        simul_dicts["updated"] = False
        # If the simul_dicts was UPDATED, calculate the kinetic parameters
        # Initialize the values to None, in case of an exception
        A_app, Ea, ro, r_squared = None, None, None, None
        # Extract the values from the simul_dicts
        tau = simul_dicts.get("tau")
        p = simul_dicts.get("p")
        T_reactor = simul_dicts.get("T_reactor")
        conversion = simul_dicts.get("conversion")
        # Convert the values to a list of magnitudes
        tau = [Q_(x).magnitude for x in tau]
        p = [Q_(x).magnitude for x in p]
        T_reactor = [Q_(x).magnitude for x in T_reactor]
        conversion = [Q_(x).magnitude for x in conversion]
        # Check if the number of independent points is more than 2
        if len(set(tau)) > 2 and len(set(p)) > 2 and len(set(T_reactor)) > 2:
            # If the number of points is more than 2, calculate the kinetic params
            try:
                # Calculate the rate equation parameters and add to the simul_params
                A_app, Ea, ro, r_squared = calc_kinetic_params(
                    instance=instance,
                    tau=tau,
                    p=p,
                    T_reactor=T_reactor,
                    conversion=conversion,
                )
                A_app = A_app * ureg("dimensionless")
                Ea = Ea * ureg("J/mol")
                ro = ro * ureg("dimensionless")
            except Exception as e:
                # Log the error if there is an exception, and do nothing
                print(f"Error in {inspect.currentframe().f_code.co_name}: {e}")
                pass
        else:
            # If the number of points is less than 3, do nothing
            pass

        simul_params["kinetic_params"] = {
            "A_app": f"{A_app:~}" if A_app else None,
            "Ea": f"{Ea:~}" if Ea else None,
            "ro": f"{ro:~}" if ro else None,
            "r_squared": f"{r_squared}" if r_squared else None,
        }
