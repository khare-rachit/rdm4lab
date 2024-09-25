from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    PasswordChangeForm,
)
from .models import User, UserExperiment
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from django.core.files.uploadedfile import UploadedFile
from django import forms
from django.core.exceptions import ValidationError
import json


class RegistrationForm(UserCreationForm):
    def clean_course(self):
        role = self.cleaned_data["role"]
        course = self.cleaned_data["course"]

        if role == "STUDENT" and course == "":
            raise forms.ValidationError("Please select a course")
        return course

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "role",
            "course",
            "semester",
            "password1",
            "password2",
        ]


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]


class PasswordUpdateForm(PasswordChangeForm):
    class Meta:
        model = User
        fields = ["old_password", "new_password1", "new_password2"]


class ReportSubmissionForm(forms.ModelForm):
    def clean_report(self):
        file = self.cleaned_data["report"]
        if file is None:
            raise forms.ValidationError(_("Please select a file."))
        return file

    class Meta:
        model = UserExperiment
        fields = ["report"]

    def __init__(self, *args, **kwargs):
        super(ReportSubmissionForm, self).__init__(*args, **kwargs)
        self.fields["report"].label = _("")  # hide the label in the form
        self.helper = FormHelper(self)
