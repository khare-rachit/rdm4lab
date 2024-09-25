"""
File location: ...G1/views.py
Description: This file contains the views for the G1 experiment.
Author: Rachit Khare
(c) 2024 RDM4Lab - all rights reserved
"""

# Global imports
from main.constants import R
from main import ureg, Q_

# Django imports
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db.models import Max
from django.http import HttpRequest, HttpResponse

# Application imports
from main.models import Experiment, UserExperiment
from G1.models import G1Data, G1Metadata, G1Results
from G1.forms import G1DataForm
from G1.utils import (
    prepare_for_html_display,
    prepare_for_db_storage,
    convert_to_html_format,
)

# Third-party imports
import json

# ------------------------------------------
# Views for G1 experiment
# ------------------------------------------


@login_required(login_url="/login")
def G1_data(request):
    """
    This view is used to display the data for the G1 experiment.
    It fetches the data from the G1Data model and displays it in a table.
    """

    # Get the current datapoints for the G1 experiment into a queryset
    currentuser = request.user
    experiment = Experiment.objects.get(id="G1")
    userexperiment = UserExperiment.objects.get(
        student_id=currentuser.uid,
        experiment_id=experiment.uid,
    )
    queryset = G1Data.objects.filter(userexperiment_id=userexperiment.uid)

    # Get the metadata fields from G3Metadata and sort them
    metadata_fields = G1Metadata.objects.first().fields
    sorted_metadata_fields = dict(
        sorted(metadata_fields.items(), key=lambda item: item[1]["order"])
    )

    dataset = (
        [
            {
                "id": item.id,
                "raw_data": prepare_for_html_display(
                    data_dict=item.raw_data,
                    metadata_fields=sorted_metadata_fields,
                ),
                "file": item.file.url or None,
                "is_active": item.is_active,
            }
            for item in queryset
        ]
        if queryset
        else None
    )

    context = {"dataset": dataset}

    return render(request, "G1/G1-data.html", context)


@login_required(login_url="/login")
def G1_data_add(request):
    """
    This view is used to add data for the G1 experiment.
    """

    # Get the existing data points for the G1 experiment into a queryset
    currentuser = request.user
    experiment = Experiment.objects.get(id="G1")
    userexperiment = UserExperiment.objects.get(
        student_id=currentuser.uid,
        experiment_id=experiment.uid,
    )
    queryset = G1Data.objects.filter(userexperiment_id=userexperiment.uid)

    # Check if the template file is present, if not set it to None
    if G1Metadata.objects.first() is None:
        template = None
    else:
        # Get the template file from the G1Metadata model
        template = G1Metadata.objects.first().template

    # Get the max ID value of the dataset
    max_id = 0 if not queryset else queryset.aggregate(Max("id"))["id__max"]
    next_id = max_id + 1

    # Get the metadata fields from G3Metadata and sort them
    metadata_fields = G1Metadata.objects.first().fields
    sorted_metadata_fields = dict(
        sorted(metadata_fields.items(), key=lambda item: item[1]["order"])
    )

    if request.method == "POST":
        form = G1DataForm(
            request.POST, request.FILES, template_url=template.url, id=next_id
        )
        # Check if the form is valid
        if form.is_valid():
            # If the form is valid, process form data for storage
            form_data = form.cleaned_data
            # Get the metadata fields from the G1Metadata model
            metadata = prepare_for_db_storage(
                data_dict=form_data,
                metadata_fields=sorted_metadata_fields,
            )
            metadata["id"] = next_id
            metadata["is_active"] = True
            # Create a new G1Data instance and save it to the database
            g1_data = G1Data(
                id=next_id,
                is_active=True,
                is_processed=False,
                raw_data=metadata,
                file=form_data["file"],
                userexperiment=userexperiment,
            )
            g1_data.save()

            return redirect("G1:G1-data")
    else:
        form = G1DataForm(template_url=template.url, id=next_id)

    return render(
        request,
        "G1/G1-data-add.html",
        {
            "template": template,
            "form": form,
        },
    )


@login_required(login_url="/login")
def G1_data_edit(request, pk):
    """
    This view allows the user to edit existing data point for the G1 experiment.
    """

    # Get the existing data point with the given ID
    g1_data = G1Data.objects.get(id=pk)
    # Get the metadata fields from G3Metadata and sort them
    metadata_fields = G1Metadata.objects.first().fields
    sorted_metadata_fields = dict(
        sorted(metadata_fields.items(), key=lambda item: item[1]["order"])
    )

    # prepare initial data for the form
    initial_data = prepare_form_data(g1_data.raw_data)

    if request.method == "POST":
        form = G1DataForm(
            request.POST,
            request.FILES,
            instance=g1_data,
            initial=initial_data,
        )
        if form.is_valid():
            form_data = form.cleaned_data
            # Prepare the data for database storage
            metadata = prepare_for_db_storage(
                data_dict=form_data,
                metadata_fields=sorted_metadata_fields,
            )
            metadata["id"] = pk
            metadata["is_active"] = g1_data.is_active
            # Update the existing G3Data instance and save it to the database
            g1_data.raw_data = metadata
            g1_data.is_processed = False
            g1_data.file = form_data["file"]
            g1_data.save(update_fields=["raw_data", "file"])

            return redirect("G1:G1-data")
    else:
        form = G1DataForm(
            id=pk,
            initial=initial_data,
        )

    return render(
        request,
        "G1/G1-data-edit.html",
        {
            "id": pk,
            "form": form,
        },
    )


@login_required(login_url="/login")
def G1_toggle_active(request: HttpRequest, pk: int) -> HttpResponse:
    """
    This view is used to toggle the active status of a data point.
    """

    # Get the data point with the given ID
    g1data = G1Data.objects.get(id=pk)
    # Toggle the active status of the data point
    g1data.is_active = not g1data.is_active
    g1data.is_processed = False
    raw_data = g1data.raw_data
    raw_data.update({"is_active": g1data.is_active})
    g1data.save()

    # Redirect to the same page from which the action was triggered
    return redirect(request.META.get("HTTP_REFERER", "G1:G1-data"))


@login_required(login_url="/login")
def G1_data_analysis(request):
    """
    This view is used to analyze the data for the G1 experiment.
    """

    # Get the current datapoints for the G1 experiment into a queryset
    currentuser = request.user
    experiment = Experiment.objects.get(id="G1")
    userexperiment = UserExperiment.objects.get(
        student_id=currentuser.uid,
        experiment_id=experiment.uid,
    )
    queryset = G1Data.objects.filter(userexperiment_id=userexperiment.uid)

    # ------------------------------------------
    # Prepare the processed dataset for display
    # ------------------------------------------

    rate_dataset = []
    for item in queryset:
        plotdata = item.proc_data.get("plotdata")
        fitdata = item.proc_data.get("fitdata")
        data = {
            "id": item.id,
            "is_active": item.raw_data.get("is_active"),
            "plots": json.dumps([plotdata, fitdata]),
        }

        metadata = {
            "T_reaction": Q_(item.raw_data["T_reaction"]).to("degC"),
            "C_base": Q_(item.raw_data["C_base"]).to("mM"),
            "C_ester": Q_(item.raw_data["C_ester"]).to("mM"),
            "rate": Q_(item.proc_data["rate"]).to("mol/(l*s)"),
            "r_squared": Q_(item.proc_data["r_squared"]).to("unitless"),
        }

        html_metadata = convert_to_html_format(data_dict=metadata)
        data.update({"metadata": html_metadata})
        rate_dataset.append(data)

    # ------------------------------------------
    # Prepare the Ea dataset for display
    # ------------------------------------------

    # Get the G1Results instance for the current user
    g1results = G1Results.objects.get(userexperiment_id=userexperiment.uid)
    ea_dicts = g1results.ea_dicts

    ea_dataset = []
    for d in ea_dicts:
        if d.get("Ea") is not None:
            # If the Ea is not None, then prepare the data for display
            metadata = {
                "C_base": Q_(d.get("C_base")).to("mM"),
                "C_ester": Q_(d.get("C_ester")).to("mM"),
                "Ea": Q_(d.get("Ea")).to("kJ/mol"),
                "r_squared": Q_(d.get("r_squared")).to("unitless"),
            }
            html_metadata = convert_to_html_format(data_dict=metadata)
            plotdata = d.get("plotdata")
            fitdata = d.get("fitdata")
            # Get the ref_ids and sort them
            ref_ids = d.get("ref_ids")
            ref_ids.sort()
            # Append the data to the dataset
            ea_dataset.append(
                {
                    "id": d.get("id"),
                    "ref_ids": ref_ids,
                    "metadata": html_metadata,
                    "plots": json.dumps([plotdata, fitdata]),
                    "error": d.get("error"),
                }
            )

    # ------------------------------------------
    # Prepare the RO base dataset for display
    # ------------------------------------------

    ro_base_dicts = g1results.ro_base_dicts

    ro_base_dataset = []
    for d in ro_base_dicts:
        if d.get("ro_base") is not None:
            # If the Ea is not None, then prepare the data for display
            metadata = {
                "T_reaction": Q_(d.get("T_reaction")).to("degC"),
                "ro_base": Q_(d.get("ro_base")).to("unitless"),
                "r_squared": Q_(d.get("r_squared")).to("unitless"),
            }
            html_metadata = convert_to_html_format(data_dict=metadata)
            plotdata = d.get("plotdata")
            fitdata = d.get("fitdata")
            # Get the ref_ids and sort them
            ref_ids = d.get("ref_ids")
            ref_ids.sort()
            # Append the data to the dataset
            ro_base_dataset.append(
                {
                    "id": d.get("id"),
                    "ref_ids": ref_ids,
                    "metadata": html_metadata,
                    "plots": json.dumps([plotdata, fitdata]),
                    "error": d.get("error"),
                }
            )

    # ------------------------------------------
    # Prepare the RO base dataset for display
    # ------------------------------------------

    ro_ester_dicts = g1results.ro_ester_dicts

    ro_ester_dataset = []
    for d in ro_ester_dicts:
        if d.get("ro_ester") is not None:
            # If the Ea is not None, then prepare the data for display
            metadata = {
                "T_reaction": Q_(d.get("T_reaction")).to("degC"),
                "ro_ester": Q_(d.get("ro_ester")).to("unitless"),
                "r_squared": Q_(d.get("r_squared")).to("unitless"),
            }
            html_metadata = convert_to_html_format(data_dict=metadata)
            plotdata = d.get("plotdata")
            fitdata = d.get("fitdata")
            # Get the ref_ids and sort them
            ref_ids = d.get("ref_ids")
            ref_ids.sort()
            # Append the data to the dataset
            ro_ester_dataset.append(
                {
                    "id": d.get("id"),
                    "ref_ids": ref_ids,
                    "metadata": html_metadata,
                    "plots": json.dumps([plotdata, fitdata]),
                    "error": d.get("error"),
                }
            )

    context = {
        "rate_dataset": rate_dataset,
        "ea_dataset": ea_dataset,
        "ro_base_dataset": ro_base_dataset,
        "ro_ester_dataset": ro_ester_dataset,
    }

    return render(request, "G1/G1-data-analysis.html", context)


def prepare_form_data(raw_data):
    """
    Function to prepare raw_data to display in the form.
    """

    input_fields = G1Metadata.objects.first().fields
    form_data = {}
    for field, attrs in input_fields.items():
        if attrs["type"] == "float":
            val = Q_(raw_data.get(field)).to(attrs["unit"])
            form_data[field] = f"{val.magnitude:.1f}"
    return form_data
