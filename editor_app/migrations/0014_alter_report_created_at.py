# Generated by Django 4.2.7 on 2023-12-18 17:53

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('editor_app', '0013_report_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
