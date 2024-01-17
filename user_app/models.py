from django.db import models
from django.utils import timezone
from taggit.managers import TaggableManager

from CommunityHelpdeskService.utils import ArticleStatus
from registration.models import User


# Create your models here.


class Article(models.Model):
    """ Article model structure """
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    tags = TaggableManager()
    status = models.IntegerField(choices=[(status.n, status.n) for status in ArticleStatus])

    def __str__(self):
        return f'{self.title} created by {self.author.username}'


class Step(models.Model):
    """ Article Step model structure """
    id = models.AutoField(primary_key=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    ordinal_number = models.IntegerField()
    title = models.CharField(max_length=255)
    description1 = models.TextField(null=True, blank=True)
    file1 = models.ImageField(null=True, blank=True)
    description2 = models.TextField(null=True, blank=True)
    file2 = models.ImageField(null=True, blank=True)

    def __str__(self):
        return f'{self.title} from {self.article.title}'
