# Generated by Django 5.0.5 on 2024-05-09 23:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("G1", "0007_rename_metadata_g1metadata_alter_g1metadata_options"),
    ]

    operations = [
        migrations.DeleteModel(
            name="G1Metadata",
        ),
    ]
