"""
File location: .../G3/views.py
Description: This file contains the views for the G3 app.
Author: Rachit Khare
(c) 2024 RDM4Lab - all rights reserved
"""

# Global imports
from main import ureg, Q_

# Django imports
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db.models import Max
from django.http import HttpRequest, HttpResponse

# Application imports
from main.models import Experiment, UserExperiment
from G3.models import G3Data, G3Metadata, G3Results
from G3.forms import G3DataForm, G3SimulForm
from G3.simulations import perform_simulation
from G3.utils import (
    prepare_for_db_storage,
    prepare_for_html_display,
    convert_to_html_format,
)

# Third-party imports
import json
import plotly.utils

# ------------------------------------------
# Views for G3 experiment
# ------------------------------------------


@login_required(login_url="/login")
def G3_data(request):
    """
    This view is used to display the data for G3 experiment.
    """

    # Get the existing data into a queryset
    currentuser = request.user
    experiment = Experiment.objects.get(id="G3")
    userexperiment = UserExperiment.objects.get(
        student_id=currentuser.uid,
        experiment_id=experiment.uid,
    )
    queryset = G3Data.objects.filter(userexperiment_id=userexperiment.uid)

    # Get the metadata fields from G3Metadata and sort them
    metadata_fields = G3Metadata.objects.first().fields
    sorted_metadata_fields = dict(
        sorted(metadata_fields.items(), key=lambda item: item[1]["order"])
    )

    # Create a dictionary list to display the existing data points
    dataset = (
        [
            {
                "id": item.id,
                "raw_data": prepare_for_html_display(
                    data_dict=item.raw_data,
                    metadata_fields=sorted_metadata_fields,
                ),
                "file": item.file.url if item.file else None,
                "is_active": item.is_active,
                "is_simulated": item.is_simulated,
            }
            for item in queryset
        ]
        if queryset
        else None
    )

    context = {"dataset": dataset}

    return render(request, "G3/G3-data.html", context)


@login_required(login_url="/login")
def G3_data_add(request):
    """
    This view allows the user to add new data for G3 experiment.
    """

    # Get the existing data into a queryset
    currentuser = request.user
    experiment = Experiment.objects.get(id="G3")
    userexperiment = UserExperiment.objects.get(
        student_id=currentuser.uid,
        experiment_id=experiment.uid,
    )
    queryset = G3Data.objects.filter(userexperiment_id=userexperiment.uid)

    # Get the max ID value of the dataset
    max_id = 0 if not queryset else queryset.aggregate(Max("id"))["id__max"]
    next_id = max_id + 1

    # Get the metadata fields from G3Metadata and sort them
    metadata_fields = G3Metadata.objects.first().fields
    sorted_metadata_fields = dict(
        sorted(metadata_fields.items(), key=lambda item: item[1]["order"])
    )

    if request.method == "POST":
        form = G3DataForm(request.POST, request.FILES, id=next_id)
        # Check if the form is valid
        if form.is_valid():
            # If the form is valid, process data for storage
            form_data = form.cleaned_data
            # Prepare the data for database storage
            metadata = prepare_for_db_storage(
                data_dict=form_data,
                metadata_fields=sorted_metadata_fields,
            )
            metadata["id"] = next_id
            metadata["is_active"] = True
            metadata["is_simulated"] = False
            # Create a new G3Data instance and save it to the database
            g3_data = G3Data(
                id=next_id,
                is_active=True,
                is_simulated=False,
                raw_data=metadata,
                file=form_data["file"],
                userexperiment=userexperiment,
            )
            g3_data.save()

            return redirect("G3:G3-data")
    else:
        form = G3DataForm(id=next_id)

    return render(request, "G3/G3-data-add.html", {"form": form})


@login_required(login_url="/login")
def G3_data_edit(request, pk):
    """
    This view allows the user to edit existing data point for the G3 experiment.
    """

    # Get the existing data point with the given ID
    g3_data = G3Data.objects.get(id=pk)
    # Get the metadata fields from G3Metadata and sort them
    metadata_fields = G3Metadata.objects.first().fields
    sorted_metadata_fields = dict(
        sorted(metadata_fields.items(), key=lambda item: item[1]["order"])
    )

    # prepare initial data for the form
    initial_data = prepare_form_data(g3_data.raw_data)

    if request.method == "POST":
        form = G3DataForm(
            request.POST,
            request.FILES,
            instance=g3_data,
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
            metadata["is_active"] = g3_data.is_active
            metadata["is_simulated"] = g3_data.is_simulated
            # Update the existing G3Data instance and save it to the database
            g3_data.raw_data = metadata
            g3_data.file = form_data["file"]
            g3_data.save(update_fields=["raw_data", "file"])

            return redirect("G3:G3-data")
    else:
        form = G3DataForm(
            id=pk,
            initial=initial_data,
        )

    return render(
        request,
        "G3/G3-data-edit.html",
        {
            "id": pk,
            "form": form,
        },
    )


@login_required(login_url="/login")
def G3_data_analysis(request):
    """
    This view is used to display the analyzed data for the G3 experiment.
    """

    # Get the existing data points into a queryset
    currentuser = request.user
    experiment = Experiment.objects.get(id="G3")
    userexperiment = UserExperiment.objects.get(
        student_id=currentuser.uid,
        experiment_id=experiment.uid,
    )
    queryset = G3Data.objects.filter(userexperiment_id=userexperiment.uid)

    # ------------------------------------------
    # Prepare the processed dataset for display
    # ------------------------------------------

    proc_dataset = []
    for item in queryset:
        data = {
            "id": item.id,
            "is_active": item.raw_data.get("is_active"),
            "is_simulated": item.raw_data.get("is_simulated"),
        }

        metadata = {
            "T_reactor": Q_(item.raw_data["T_reactor"]).to("degC"),
            "p": Q_(item.proc_data["p"]).to("bar"),
            "tau": Q_(item.proc_data["tau"]).to("g*h/mol").to_base_units(),
            "conversion": Q_(item.proc_data["conversion"]).to("percent"),
        }

        html_metadata = convert_to_html_format(data_dict=metadata)
        data.update({"proc_data": html_metadata})
        proc_dataset.append(data)

    # ------------------------------------------
    # Prepare the rate dataset for display
    # ------------------------------------------

    g3results = G3Results.objects.get(userexperiment=userexperiment)
    rate_dicts = g3results.rate_dicts

    rate_dataset = []
    for d in rate_dicts:
        if d.get("rate") is not None:
            # If the rate is not None, then prepare the data for display
            metadata = {
                "p": Q_(d.get("p")).to("bar"),
                "T_reactor": Q_(d.get("T_reactor")).to("degC"),
                "rate": Q_(d.get("rate")).to("mol/(g*h)"),
                "r_squared": Q_(d.get("r_squared")).to("unitless"),
            }
            html_metadata = convert_to_html_format(data_dict=metadata)
            plotdata = d.get("plotdata")
            fitdata = d.get("fitdata")
            simuldata = d.get("simuldata")
            # Get the ref_ids and is_simulated and sort them
            ref_ids = d.get("ref_ids")
            is_simulated = d.get("is_simulated")
            combined = list(zip(ref_ids, is_simulated))
            combined.sort()
            ref_ids, is_simulated = zip(*combined)
            # Append the data to the dataset
            rate_dataset.append(
                {
                    "id": d.get("id"),
                    "ref_ids": ref_ids,
                    "metadata": html_metadata,
                    "is_simulated": is_simulated,
                    "plots": json.dumps(
                        [plotdata, simuldata, fitdata],
                        cls=plotly.utils.PlotlyJSONEncoder,
                    ),
                    "error": d.get("error"),
                }
            )

    # ------------------------------------------
    # Prepare the dataset for Ea analysis
    # ------------------------------------------

    ea_dicts = g3results.ea_dicts

    ea_dataset = []
    for d in ea_dicts:
        if d.get("Ea") is not None:
            # If the Ea is not None, then prepare the data for display
            metadata = {
                "p": Q_(d.get("p")).to("bar"),
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
    # Prepare the dataset for RO analysis
    # ------------------------------------------

    ro_dicts = g3results.ro_dicts

    ro_dataset = []
    for d in ro_dicts:
        if d.get("r_order") is not None:
            # If the Ea is not None, then prepare the data for display
            metadata = {
                "T_reactor": Q_(d.get("T_reactor")).to("degC"),
                "r_order": Q_(d.get("r_order")).to("unitless"),
                "r_squared": Q_(d.get("r_squared")).to("unitless"),
            }
            html_metadata = convert_to_html_format(data_dict=metadata)
            plotdata = d.get("plotdata")
            fitdata = d.get("fitdata")
            # Get the ref_ids and sort them
            ref_ids = d.get("ref_ids")
            ref_ids.sort()
            # Append the data to the dataset
            ro_dataset.append(
                {
                    "id": d.get("id"),
                    "ref_ids": ref_ids,
                    "metadata": html_metadata,
                    "plots": json.dumps([plotdata, fitdata]),
                    "error": d.get("error"),
                }
            )

    context = {
        "proc_dataset": proc_dataset,
        "rate_dataset": rate_dataset,
        "ea_dataset": ea_dataset,
        "ro_dataset": ro_dataset,
    }

    return render(request, "G3/G3-data-analysis.html", context)


@login_required(login_url="/login")
def G3_toggle_active(request: HttpRequest, pk: int) -> HttpResponse:
    """
    This view is used to toggle the active status of a data point.
    """

    # Get the data point with the given ID
    g3data = G3Data.objects.get(id=pk)
    # Toggle the active status of the data point
    g3data.is_active = not g3data.is_active
    raw_data = g3data.raw_data
    raw_data.update({"is_active": g3data.is_active})
    g3data.save()

    # Redirect to the same page from which the action was triggered
    return redirect(request.META.get("HTTP_REFERER", "G3:G3-data"))


@login_required(login_url="/login")
def G3_data_simulation(request):
    """
    This view is used to simulate the data for G3 experiment.
    """

    # Get the current userexperiment data into a queryset
    currentuser = request.user
    experiment = Experiment.objects.get(id="G3")
    userexperiment = UserExperiment.objects.get(
        student_id=currentuser.uid,
        experiment_id=experiment.uid,
    )
    queryset = G3Data.objects.filter(userexperiment_id=userexperiment.uid)

    # Get the max ID value of the dataset
    max_id = 0 if not queryset else queryset.aggregate(Max("id"))["id__max"]
    next_id = max_id + 1

    # Get the metadata fields from G3Metadata and sort them
    metadata_fields = G3Metadata.objects.first().fields
    sorted_metadata_fields = dict(
        sorted(metadata_fields.items(), key=lambda item: item[1]["order"])
    )

    if request.method == "POST":
        # Create a form instance and populate it with data from the request
        form = G3SimulForm(request.POST)
        action = request.POST.get("action")
        if action == "simulate":
            # If the action is to simulate the data
            if form.is_valid():
                form_data = form.cleaned_data
                # get input data from the form and perform simulation
                input_data = get_input_data(form_data)
                output_data = perform_simulation(userexperiment, input_data)
                # update the form with the output data and create a new form
                form_data.update(output_data)
                form = G3SimulForm(initial=form_data)

        elif action == "add-data":
            # If the action is to add the simulated data to the database
            if form.is_valid():
                form_data = form.cleaned_data
                # Prepare the data for database storage
                metadata = prepare_for_db_storage(
                    data_dict=form_data,
                    metadata_fields=sorted_metadata_fields,
                )
                metadata["id"] = next_id
                metadata["is_active"] = True
                metadata["is_simulated"] = True
                # Create a new G3Data instance and save it to the database
                g3_data = G3Data(
                    id=next_id,
                    is_active=True,
                    is_simulated=True,
                    raw_data=metadata,
                    file=None,
                    userexperiment=userexperiment,
                )
                g3_data.save()
                return redirect("G3:G3-data")
    else:
        form = G3SimulForm()

    return render(
        request,
        "G3/G3-data-simulation.html",
        {"form": form},
    )


def get_input_data(form_data):
    """
    Function to get the input data from the form data.
    """

    input_fields = G3Metadata.objects.first().fields
    input_data = {}
    for field, attrs in input_fields.items():
        if attrs["scope"] == "input":
            if attrs["type"] == "float":
                input_data[field] = form_data[field] * ureg(attrs["unit"])
    return input_data


def get_output_data(form_data):
    """
    Function to get the output data from the form data.
    """

    output_fields = G3Metadata.objects.first().output_fields
    output_data = {}
    for field, attrs in output_fields.items():
        if attrs["scope"] == "input":
            if attrs["type"] == "float":
                output_data[field] = form_data[field] * ureg(attrs["unit"])
    return output_data


def prepare_form_data(raw_data):
    """
    Function to prepare raw_data to display in the form.
    """

    input_fields = G3Metadata.objects.first().fields
    form_data = {}
    for field, attrs in input_fields.items():
        if attrs["type"] == "float":
            val = Q_(raw_data.get(field)).to(attrs["unit"])
            form_data[field] = f"{val.magnitude:.1f}"
    return form_data
