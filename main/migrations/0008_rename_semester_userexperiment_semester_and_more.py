# Generated by Django 5.0.5 on 2024-05-09 16:40

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0007_alter_userexperiment_semester"),
    ]

    operations = [
        migrations.RenameField(
            model_name="userexperiment",
            old_name="Semester",
            new_name="semester",
        ),
        migrations.AlterField(
            model_name="userexperiment",
            name="report",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to="reports/",
                validators=[
                    django.core.validators.FileExtensionValidator(
                        ["pdf"], message="Please upload a .pdf file."
                    )
                ],
                verbose_name="Report",
            ),
        ),
    ]
