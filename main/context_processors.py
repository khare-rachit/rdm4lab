# main/context_processors.py

"""
This file is used to create custom context processors
that can be then used in the templates.
"""

from main.models import Semester


def current_semester(request):
    """Context processor to add the current semester id e.g. SS2024."""
    context = {"current_semester": None}  # Default value
    context["current_semester"] = Semester.objects.get(is_current=True).id
    return context
