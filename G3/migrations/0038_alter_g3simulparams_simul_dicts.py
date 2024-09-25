# Generated by Django 5.0.5 on 2024-05-22 00:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("G3", "0037_alter_g3simulparams_simul_dicts"),
    ]

    operations = [
        migrations.AlterField(
            model_name="g3simulparams",
            name="simul_dicts",
            field=models.JSONField(
                blank=True, default=list, verbose_name="Simul Dictionaries"
            ),
        ),
    ]
