# Generated by Django 4.2.7 on 2024-01-13 18:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_app', '0012_alter_article_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='status',
            field=models.IntegerField(choices=[(1, 'APPROVED'), (2, 'UNAPPROVED'), (3, 'CHANGES_REQUESTED'), (4, 'CHANGES_DURING_REPORT'), (5, 'REJECTED')]),
        ),
    ]