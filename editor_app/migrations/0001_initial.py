# Generated by Django 4.2.7 on 2024-01-22 22:53

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=150)),
                ('description', models.TextField(max_length=512)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('additional_file', models.ImageField(upload_to='')),
                ('status', models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9)])),
            ],
        ),
    ]
