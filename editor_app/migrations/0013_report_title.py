# Generated by Django 4.2.7 on 2023-12-04 21:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('editor_app', '0012_alter_report_additional_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='title',
            field=models.CharField(default='Filler for title', max_length=150),
            preserve_default=False,
        ),
    ]
