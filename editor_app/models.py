from django.db import models
from registration.models import User
from user_app.models import Article
from django.utils import timezone


# Create your models here.


class Report(models.Model):
    """ Report model structure """
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=150)
    description = models.TextField(max_length=512)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='report_author')
    created_at = models.DateTimeField(default=timezone.now)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    editor = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='report_editor')
    additional_file = models.FileField()
    status = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.description} created by {self.author.username}'
