# Generated by Django 5.0.5 on 2024-05-17 20:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("G3", "0026_g3results_delete_g3analysisresults"),
    ]

    operations = [
        migrations.RenameField(
            model_name="g3results",
            old_name="dat_grp_o2",
            new_name="ea_dicts",
        ),
        migrations.RenameField(
            model_name="g3results",
            old_name="dat_grp_o1",
            new_name="rate_dicts",
        ),
        migrations.RenameField(
            model_name="g3results",
            old_name="dat_grp_o3",
            new_name="ro_dicts",
        ),
    ]
