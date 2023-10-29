from django import forms
from .models import Article


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        exclude = ['author', 'created_at']


class SearchByNameForm(forms.ModelForm):
    search_text = forms.CharField(label='Search by Name', max_length=255)


class SearchByTagsForm(forms.ModelForm):
    search_text = forms.CharField(label='Search by Tag', max_length=255)
