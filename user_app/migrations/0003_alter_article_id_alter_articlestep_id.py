# Generated by Django 4.1.12 on 2023-10-29 14:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_app', '0002_alter_article_id_alter_articlestep_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='articlestep',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]