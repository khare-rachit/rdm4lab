# Generated by Django 5.0.5 on 2024-05-09 22:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("G1", "0001_initial"),
        ("main", "0011_alter_userexperiment_unique_together"),
    ]

    operations = [
        migrations.CreateModel(
            name="G1Data",
            fields=[
                ("uid", models.AutoField(primary_key=True, serialize=False)),
                ("id", models.IntegerField(unique=True, verbose_name="ID")),
                (
                    "userexperiment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="main.userexperiment",
                    ),
                ),
            ],
            options={
                "verbose_name": "G1 Data",
                "verbose_name_plural": "G1 Data",
            },
        ),
        migrations.DeleteModel(
            name="G1",
        ),
    ]
