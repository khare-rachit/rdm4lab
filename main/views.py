# main/views.py
# Contains views for the main app.

import os
from django.shortcuts import render, redirect
from main.forms import (
    RegistrationForm,
    UserUpdateForm,
    PasswordUpdateForm,
    ReportSubmissionForm,
)
from main.models import Experiment, UserExperiment
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from main.utils import get_warning_msg, get_context
from django.urls import reverse
from django.apps import apps


# Home page
def home(request):
    return render(
        request,
        "home.html",
        {},
    )


# Logout view (when user clicks on logout)
def logout_view(request):
    logout(request)
    return redirect("/login/")


# Registration page for new users
def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the user
            login(request, user)  # Log the user in
            return redirect("/home")  # Redirect to the home page
    else:
        form = RegistrationForm()

    return render(
        request,
        "registration/register.html",
        {"form": form},
    )


# Page that displays user profile information
@login_required(login_url="/login")
def profile(request):
    return render(
        request,
        "registration/profile.html",
        {},
    )


# Page to update user profile information
@login_required(login_url="/login")
def update_profile(request):
    if request.method == "POST":
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your Profile has been updated!")
            return redirect("/profile/")
    else:
        form = UserUpdateForm(instance=request.user)

    return render(
        request,
        "registration/update-profile.html",
        {"form": form},
    )


# Page to change user password
@login_required(login_url="/login")
def change_password(request):
    if request.method == "POST":
        form = PasswordUpdateForm(data=request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect("/profile")
    else:
        form = PasswordUpdateForm(user=request.user)

    return render(
        request,
        "registration/change-password.html",
        {"form": form},
    )


# Page that lists all active experiments
def experiments(request):
    queryset = Experiment.objects.filter(is_active=True)  # Get all active experiments
    experiment_list = []
    for item in queryset:
        experiment_list.append(
            {
                "id": item.id,
                "name": item.name,
            }
        )

    return render(
        request,
        "main/experiments.html",
        {"experiment_list": experiment_list},
    )


# Page that shows the details of individual experiments based on their IDs
def experiments_id(request, experiment_id):
    # Get the experiment based on the ID
    experiment = Experiment.objects.get(id=experiment_id)

    # Get the richtext from the description field
    richtext = experiment.description

    # Get the context dictionary from the richtext
    context = get_context(richtext)

    return render(
        request,
        "main/experiments-id.html",
        {
            "experiment": experiment,
            "context": context,
        },
    )


# Page to display all the experiments scheduled for a specific user
@login_required(login_url="/login")
def my_experiments(request):
    currentuser = request.user  # Get the current logged in user
    # Get all the experiments assigned to the the user
    queryset = UserExperiment.objects.filter(student_id=currentuser.uid)

    my_experiments = []  # List to store the experiments
    for item in queryset:
        my_experiments.append(
            {
                "id": Experiment.objects.get(
                    uid=item.experiment_id
                ),  # Get the experiment details using the experimetn ID
                "experiment_date": item.experiment_date,
                "report_due_date": item.report_due_date,
                "report": item.report,
            }
        )

    # Check if the report is overdue or due today
    for item in my_experiments:
        report_due_date = item["report_due_date"]
        report = item.get("report", None)
        warning, warning_msg = get_warning_msg(report_due_date, report)
        item["warning"] = warning
        item["warning_msg"] = warning_msg

    return render(
        request,
        "main/my-experiments.html",
        {"my_experiments": my_experiments},
    )


# Page to display individual user experiments
@login_required(login_url="/login")
def my_experiments_id(request, experiment_id):
    currentuser = request.user  # Get the current logged in user
    experiment = Experiment.objects.get(
        id=experiment_id
    )  # Get the experiment details based on the experiment ID
    my_experiment = UserExperiment.objects.get(
        student_id=currentuser.uid,
        experiment_id=experiment.uid,
    )  # Get the user experiment details

    report_due_date = my_experiment.report_due_date
    report = my_experiment.report
    warning, warning_msg = get_warning_msg(report_due_date, report)
    context = {
        "warning": warning,
        "warning_msg": warning_msg,
    }  # context to be passed to the template

    if request.method == "POST":
        form = ReportSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.cleaned_data["report"]
            my_experiment.report = report
            my_experiment.submission_date = timezone.now()
            my_experiment.save(update_fields=["report", "submission_date"])
            # Update the report field in UserExperiment model
            return redirect(
                "my-experiments-id", experiment_id=experiment_id
            )  # Redirect back to the projects list or to a success page
        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = ReportSubmissionForm()

    if my_experiment.report:
        report_path = my_experiment.report.name
        report_name = os.path.basename(report_path)
        context["report_name"] = report_name

    return render(
        request,
        "main/my-experiments-id.html",
        {
            "my_experiment": my_experiment,
            "experiment": experiment,
            "context": context,
            "form": form,
        },
    )


# Redirect to data management page for each experiment
@login_required(login_url="/login")
def redirect_to_experiment_data(request, experiment_id, *args, **kwargs):
    app_name = experiment_id
    if apps.is_installed(app_name):
        return redirect(reverse(app_name + ":" + app_name + "-data"))
    else:
        return render(
            request,
            "main/my-experiments-data.html",
            {"experiment_id": experiment_id},
        )


# Redirect to data analysis page for each experiment
@login_required(login_url="/login")
def redirect_to_experiment_data_analysis(request, experiment_id, *args, **kwargs):
    app_name = experiment_id
    if apps.is_installed(app_name):
        return redirect(reverse(app_name + ":" + app_name + "-data-analysis"))
    else:
        return render(
            request,
            "main/my-experiments-data-analysis.html",
            {"experiment_id": experiment_id},
        )
