# Generated by Django 5.0 on 2023-12-06 16:15

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("novel", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="crawlsource",
            old_name="url",
            new_name="name",
        ),
    ]