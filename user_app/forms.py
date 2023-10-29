from django import forms
from .models import Article
from taggit.forms import TagField


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        exclude = ['author', 'created_at']


class SearchByNameForm(forms.Form):
    search_text = forms.CharField(label='Search by Name', max_length=255)


class SearchByTagsForm(forms.Form):
    tags = TagField()
