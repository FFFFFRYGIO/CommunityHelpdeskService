# Generated by Django 4.1.12 on 2023-11-09 14:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_app', '0007_rename_step_number_step_ordinal_number_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='status',
            field=models.TextField(default='initial', max_length=50),
            preserve_default=False,
        ),
    ]
