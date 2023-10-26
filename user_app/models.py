from django.db import models
from registration.models import User

# Create your models here.


class Article(models.Model):
    # id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateField()
    tags = models.JSONField(default=list)


class ArticleStep(models.Model):
    # id = models.IntegerField(primary_key=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    step_number = models.IntegerField()
    title = models.CharField(max_length=255)
    description1 = models.TextField()
    file1 = models.FileField()
    description2 = models.TextField()
    file2 = models.FileField()
