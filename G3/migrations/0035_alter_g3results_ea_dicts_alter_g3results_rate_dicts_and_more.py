# Generated by Django 5.0.5 on 2024-05-22 00:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("G3", "0034_alter_g3results_ea_dicts_alter_g3results_rate_dicts_and_more"),
    ]

    operations = [
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
        migrations.AlterField(
            model_name="g3simulparams",
            name="simul_dicts",
            field=models.JSONField(
                blank=True, default=list, verbose_name="Simul Dictionaries"
            ),
        ),
    ]
