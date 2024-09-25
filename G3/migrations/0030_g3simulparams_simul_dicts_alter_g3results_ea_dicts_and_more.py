# Generated by Django 5.0.5 on 2024-05-19 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("G3", "0029_remove_g3results_ea_dataset_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="g3simulparams",
            name="simul_dicts",
            field=models.JSONField(
                blank=True, default=list, verbose_name="Simul Dictionaries"
            ),
        ),
        migrations.AlterField(
            model_name="g3results",
            name="ea_dicts",
            field=models.JSONField(
                blank=True, default=list, verbose_name="Ea Dictionaries"
            ),
        ),
        migrations.AlterField(
            model_name="g3results",
            name="rate_dicts",
            field=models.JSONField(
                blank=True, default=list, verbose_name="Rate Dictionaries"
            ),
        ),
        migrations.AlterField(
            model_name="g3results",
            name="ro_dicts",
            field=models.JSONField(
                blank=True, default=list, verbose_name="RO Dictionaries"
            ),
        ),
    ]
