# Generated by Django 4.1.12 on 2023-11-07 18:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_app', '0004_remove_article_tags_article_tags'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ArticleStep',
            new_name='Step',
        ),
    ]