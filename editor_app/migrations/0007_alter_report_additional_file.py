# Generated by Django 4.1.12 on 2023-11-06 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('editor_app', '0006_remove_report_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='additional_file',
            field=models.FileField(null=True, upload_to=''),
        ),
    ]
