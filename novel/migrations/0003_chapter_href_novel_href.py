# Generated by Django 5.0 on 2023-12-07 08:34

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("novel", "0002_rename_url_crawlsource_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="chapter",
            name="href",
            field=models.CharField(default="", max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="novel",
            name="href",
            field=models.CharField(default="abc", max_length=255),
            preserve_default=False,
        ),
    ]