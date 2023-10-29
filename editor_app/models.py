from django.db import models
from registration.models import User
from user_app.models import Article


# Create your models here.


class Report(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='report_author')
    created_at = models.DateField()
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    editor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='report_editor')
    additional_file = models.FileField()
