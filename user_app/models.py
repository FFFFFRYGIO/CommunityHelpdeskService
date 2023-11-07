from django.db import models
from registration.models import User
from taggit.managers import TaggableManager


# Create your models here.


class Article(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateField()
    tags = TaggableManager()


class Step(models.Model):
    id = models.AutoField(primary_key=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    step_number = models.IntegerField()
    title = models.CharField(max_length=255)
    description1 = models.TextField()
    file1 = models.FileField()
    description2 = models.TextField()
    file2 = models.FileField()
