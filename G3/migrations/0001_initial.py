# Generated by Django 5.0.5 on 2024-05-13 14:32

import G3.utils
import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("main", "0011_alter_userexperiment_unique_together"),
    ]

    operations = [
        migrations.CreateModel(
            name="G3Metadata",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "fields",
                    models.JSONField(blank=True, default=dict, verbose_name="Fields"),
                ),
                (
                    "additional_fields",
                    models.JSONField(
                        blank=True, default=dict, verbose_name="Additional Fields"
                    ),
                ),
                (
                    "template",
                    models.FileField(
                        blank=True,
                        upload_to=G3.utils.upload_G3template,
                        validators=[
                            django.core.validators.FileExtensionValidator(
                                ["csv"],
                                message="Please upload a valid file format (.csv)",
                            )
                        ],
                        verbose_name="Template",
                    ),
                ),
            ],
            options={
                "verbose_name": "G3 Metadata",
                "verbose_name_plural": "G3 Metadata",
            },
        ),
        migrations.CreateModel(
            name="G3Data",
            fields=[
                ("uid", models.AutoField(primary_key=True, serialize=False)),
                (
                    "id",
                    models.PositiveIntegerField(
                        unique=True, verbose_name="data point #"
                    ),
                ),
                (
                    "metadata",
                    models.JSONField(blank=True, default=dict, verbose_name="Metadata"),
                ),
                (
                    "file",
                    models.FileField(
                        blank=True,
                        upload_to=G3.utils.upload_G3data,
                        validators=[
                            django.core.validators.FileExtensionValidator(
                                ["csv"],
                                message="Please upload a valid file format (.csv)",
                            )
                        ],
                        verbose_name="Data File",
                    ),
                ),
                (
                    "Remarks",
                    models.TextField(blank=True, default="", verbose_name="Remarks"),
                ),
                (
                    "userexperiment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="main.userexperiment",
                    ),
                ),
            ],
            options={
                "verbose_name": "G3 Data",
                "verbose_name_plural": "G3 Data",
                "unique_together": {("userexperiment", "id")},
            },
        ),
    ]
