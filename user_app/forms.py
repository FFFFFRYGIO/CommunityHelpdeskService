from django import forms
from .models import Article, Step
from taggit.forms import TagField


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        exclude = ['author', 'created_at', 'status']


class StepForm(forms.ModelForm):
    class Meta:
        model = Step
        exclude = ['article', 'ordinal_number']
        widgets = {
            'title': forms.TextInput(attrs={'required': True}),
            'description1': forms.Textarea(attrs={'rows': 1, 'cols': 40}),
            'description2': forms.Textarea(attrs={'rows': 1, 'cols': 40}),
        }


StepFormSet = forms.modelformset_factory(Step, form=StepForm)


class SearchByNameForm(forms.Form):
    search_text = forms.CharField(label='Search by Name', max_length=255)


class SearchByTagsForm(forms.Form):
    tags = TagField()
