# Generated by Django 5.0.5 on 2024-05-13 15:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("G3", "0004_alter_g3metadata_options"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="g3data",
            options={
                "ordering": ["id"],
                "verbose_name": "G3 Data",
                "verbose_name_plural": "G3 Data",
            },
        ),
        migrations.AlterModelOptions(
            name="g3metadata",
            options={
                "verbose_name": "G3 Metadata",
                "verbose_name_plural": "G3 Metadata",
            },
        ),
    ]
