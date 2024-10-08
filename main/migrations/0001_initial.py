# Generated by Django 5.0.5 on 2024-05-08 13:04

import ckeditor.fields
import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="Course",
            fields=[
                ("uid", models.AutoField(primary_key=True, serialize=False)),
                (
                    "id",
                    models.CharField(
                        max_length=10, unique=True, verbose_name="Course ID"
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        blank=True, max_length=30, verbose_name="Course Name"
                    ),
                ),
            ],
            options={
                "verbose_name": "Course",
                "verbose_name_plural": "Courses",
                "ordering": ["id"],
            },
        ),
        migrations.CreateModel(
            name="Experiment",
            fields=[
                ("uid", models.AutoField(primary_key=True, serialize=False)),
                (
                    "id",
                    models.CharField(
                        max_length=5, unique=True, verbose_name="Experiment ID"
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        blank=True, max_length=200, verbose_name="Experiment Name"
                    ),
                ),
                (
                    "description",
                    ckeditor.fields.RichTextField(
                        blank=True, default="", verbose_name="Description"
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True, verbose_name="Is this experiment active?"
                    ),
                ),
            ],
            options={
                "verbose_name": "Experiment",
                "verbose_name_plural": "Experiments",
                "ordering": ["id"],
            },
        ),
        migrations.CreateModel(
            name="Semester",
            fields=[
                ("uid", models.AutoField(primary_key=True, serialize=False)),
                (
                    "id",
                    models.CharField(
                        max_length=10, unique=True, verbose_name="Semester ID"
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        blank=True,
                        max_length=30,
                        null=True,
                        verbose_name="Semester Name",
                    ),
                ),
                (
                    "start_date",
                    models.DateField(blank=True, null=True, verbose_name="Start Date"),
                ),
                (
                    "end_date",
                    models.DateField(blank=True, null=True, verbose_name="End Date"),
                ),
                (
                    "is_current",
                    models.BooleanField(
                        default=False, verbose_name="Is this semester current?"
                    ),
                ),
            ],
            options={
                "verbose_name": "Semester",
                "verbose_name_plural": "Semesters",
                "ordering": ["-start_date"],
            },
        ),
        migrations.CreateModel(
            name="User",
            fields=[
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        error_messages={
                            "unique": "A user with that username already exists."
                        },
                        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        max_length=150,
                        unique=True,
                        validators=[
                            django.contrib.auth.validators.UnicodeUsernameValidator()
                        ],
                        verbose_name="username",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="first name"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="last name"
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                ("uid", models.AutoField(primary_key=True, serialize=False)),
                (
                    "email",
                    models.EmailField(
                        max_length=254,
                        validators=[django.core.validators.EmailValidator],
                        verbose_name="Email address",
                    ),
                ),
                (
                    "role",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("STUDENT", "Student"),
                            ("SUPERVISER", "Superviser"),
                            ("ADMIN", "Admin"),
                            ("GUEST", "Guest"),
                        ],
                        default="STUDENT",
                        max_length=10,
                        verbose_name="Role",
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
                (
                    "course",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="main.course",
                    ),
                ),
                (
                    "semester",
                    models.ManyToManyField(
                        blank=True,
                        limit_choices_to={"is_current": True},
                        to="main.semester",
                    ),
                ),
            ],
            options={
                "verbose_name": "user",
                "verbose_name_plural": "users",
                "abstract": False,
            },
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
