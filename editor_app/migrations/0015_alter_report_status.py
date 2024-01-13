# Generated by Django 4.2.7 on 2024-01-13 18:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('editor_app', '0014_alter_report_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='status',
            field=models.IntegerField(choices=[(1, 'NA_OPENED'), (2, 'NA_ASSIGNED'), (3, 'NA_CHANGES_APPLIED'), (4, 'ARTICLE_REJECTED'), (5, 'OPENED'), (6, 'ASSIGNED'), (7, 'CHANGES_APPLIED'), (8, 'REJECTED'), (9, 'CONCLUDED')]),
        ),
    ]
