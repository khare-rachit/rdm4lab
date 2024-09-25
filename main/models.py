# main/models.py

# This is the main model file for the project.

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import EmailValidator
from django.utils.translation import gettext as _
from ckeditor_uploader.fields import RichTextUploadingField
from django.core.validators import FileExtensionValidator
from main.utils import upload_report_location


class Semester(models.Model):
    """Model for a semester e.g. SS2024."""

    uid = models.AutoField(
        primary_key=True,
    )  # Auto-generated unique ID for the database

    id = models.CharField(
        _("Semester ID"),
        max_length=10,
        unique=True,
        blank=False,
    )  # Semester ID e.g. SS2024

    name = models.CharField(
        _("Semester Name"),
        max_length=30,
        blank=True,
        null=True,
    )  # Semester name e.g. Summer Semester 2024

    start_date = models.DateField(
        _("Start Date"),
        blank=True,
        null=True,
    )  # Start date of experiments in the semester

    end_date = models.DateField(
        _("End Date"),
        blank=True,
        null=True,
    )  # End date of experiments in the semester

    is_current = models.BooleanField(
        _("Is this semester current?"),
        default=False,
    )  # is True if the semester is current

    def save(self, *args, **kwargs):
        # prevents multiple current semesters
        if self.is_current:
            try:
                temp = Semester.objects.get(is_current=True)
                if temp != self:
                    temp.is_current = False
                    temp.save()
            except Semester.DoesNotExist:
                pass
        super(Semester, self).save(*args, **kwargs)

    class Meta:
        ordering = ["-start_date"]
        verbose_name = "Semester"
        verbose_name_plural = "Semesters"

    def __str__(self):
        return self.id


class Course(models.Model):
    """Model for a course e.g. CHEM, CIW, etc."""

    uid = models.AutoField(
        primary_key=True
    )  # Auto-generated unique ID for the database

    id = models.CharField(
        _("Course ID"),
        max_length=10,
        unique=True,
        blank=False,
    )  # Couse ID to identify the course e.g. CHEM, CIW, etc.

    name = models.CharField(
        _("Course Name"),
        max_length=30,
        blank=True,
    )  # Title of the course e.g. Chemistry, Chemical Engineering, etc.

    class Meta:
        ordering = ["id"]
        verbose_name = "Course"
        verbose_name_plural = "Courses"

    def __str__(self):
        return self.id


class User(AbstractUser):
    """Custom django user model for authentication."""

    uid = models.AutoField(
        primary_key=True,
    )  # Auto-generated unique ID for the database

    email = models.EmailField(
        _("Email address"),
        blank=False,
        validators=[EmailValidator],
    )  # Email address of the user

    # class to define the role of the user
    class Role(models.TextChoices):
        STUDENT = "STUDENT", "Student"
        SUPERVISER = "SUPERVISER", "Superviser"
        ADMIN = "ADMIN", "Admin"
        GUEST = "GUEST", "Guest"

    role = models.CharField(
        _("Role"),
        max_length=10,
        choices=Role.choices,
        default=Role.STUDENT,
        blank=True,
    )  # Role of the user

    semester = models.ManyToManyField(
        Semester,
        blank=True,
        limit_choices_to={"is_current": True},
    )  # SemesterID(s) from the Semester Model (only current semester is allowed!)

    course = models.OneToOneField(
        Course,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )  # CourseID from the Course model (user can have only one course)

    USERNAME_FIELD = "username"  # Required for authentication
    REQUIRED_FIELDS = ["email", "role"]  # Required for creating a user

    def __str__(self):
        return self.username


class Experiment(models.Model):
    """Model for experiments e.g. A1, G1, etc."""

    uid = models.AutoField(
        primary_key=True
    )  # Auto-generated unique ID for the database

    id = models.CharField(
        _("Experiment ID"),
        max_length=5,
        unique=True,
        blank=False,
    )  # Experiment ID for the experiment e.g. A1, G1, etc.

    name = models.CharField(
        _("Experiment Name"),
        max_length=200,
        blank=True,
    )  # Name of the experiment

    description = RichTextUploadingField(
        "Description",
        default="",
        blank=True,
    )  # Description of experiment

    is_active = models.BooleanField(
        _("Is this experiment active?"),
        default=True,
    )  # To set if the experiment is active or not

    class Meta:
        ordering = ["id"]
        verbose_name = "Experiment"
        verbose_name_plural = "Experiments"

    def __str__(self):
        return self.id


class UserExperiment(models.Model):
    """Model for storing data from the individual experiments
    performed by a student. There is a separate entry for each
    semester."""

    uid = models.BigAutoField(
        primary_key=True,
    )  # Auto-generated unique ID for the database

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False,
    )  # StudentID from the User model

    experiment = models.ForeignKey(
        Experiment,
        on_delete=models.CASCADE,
        blank=False,
    )  # ExperimentID from the Experiment model

    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE,
        blank=False,
    )  # SemesterID from the Semester model

    experiment_date = models.DateTimeField(
        _("Experiment Scheduled On"),
        blank=True,
        null=True,
    )  # Date experiment is scheduled on

    report_due_date = models.DateTimeField(
        _("Report Due On"),
        blank=True,
        null=True,
    )  # Date experimental report is due on

    report = models.FileField(
        _("Report"),
        upload_to=upload_report_location,
        validators=[
            FileExtensionValidator(
                ["pdf"],
                message=_("Please upload a .pdf file."),
            ),  # Only .pdf files are allowed currently
        ],
        blank=True,
        null=True,
    )  # report uploaded by the user

    submission_date = models.DateTimeField(
        _("Report Submitted On"),
        default=None,
        blank=True,
        null=True,
    )  # Date the report was submitted on

    class Meta:
        ordering = ["experiment"]
        unique_together = ["student", "experiment", "semester"]
        verbose_name = "User Experiment"
        verbose_name_plural = "User Experiments"

    def __str__(self):
        return self.student.username + "_" + self.experiment.id

    def save(self, *args, **kwargs):
        # Initialize existing_file with None to ensure it's always defined
        existing_report = None
        # Check if this is an update (i.e., instance already exists in the database)
        if self.pk:
            try:
                # Fetch the old instance to compare files
                old_instance = UserExperiment.objects.get(pk=self.pk)
                existing_report = old_instance.report
                # get the existing report from the model UserExperiment
                if existing_report and self.report and existing_report != self.report:
                    # Delete the old file if it doesn't match the newly submitted one
                    existing_report.delete(save=False)
            except UserExperiment.DoesNotExist:
                pass
        super(UserExperiment, self).save(*args, **kwargs)
