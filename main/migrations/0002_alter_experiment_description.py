# Generated by Django 5.0.5 on 2024-05-08 17:40

import ckeditor_uploader.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="experiment",
            name="description",
            field=ckeditor_uploader.fields.RichTextUploadingField(
                blank=True, default="", verbose_name="Description"
            ),
        ),
    ]
