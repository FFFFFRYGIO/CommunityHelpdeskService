from django import forms
from .models import Article, Step
from taggit.forms import TagField


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        exclude = ['author', 'created_at']


class StepForm(forms.ModelForm):
    class Meta:
        model = Step
        exclude = ['article', 'step_number']


StepFormSet = forms.modelformset_factory(Step, form=StepForm, extra=3)

class SearchByNameForm(forms.Form):
    search_text = forms.CharField(label='Search by Name', max_length=255)


class SearchByTagsForm(forms.Form):
    tags = TagField()
