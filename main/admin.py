from typing import Any
from django import forms
from django.contrib import admin
from .models import Semester, Course, Experiment, User, UserExperiment


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "is_current",
        "start_date",
        "end_date",
    )


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
    )


admin.site.register(User)


@admin.register(Experiment)
class ExperimentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "is_active",
    )


class UserExperimentAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "student",
        "experiment",
    )

    def save_model(self, request: Any, obj: Any, form: Any, change: Any) -> None:
        if change:
            obj.save(update_fields=form.changed_data)
        else:
            obj.save()


admin.site.register(UserExperiment, UserExperimentAdmin)
