# Generated by Django 4.2.7 on 2024-01-13 20:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_app', '0014_alter_article_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='step',
            name='file1',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='step',
            name='file2',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]
