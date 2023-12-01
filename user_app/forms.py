from django import forms
from .models import Article, Step
from taggit.forms import TagField, TagWidget


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        exclude = ['author', 'created_at', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'required': True, 'class': 'form-control form-control-sm'}),
            'tags': TagWidget(
                attrs={'class': 'form-control form-control-sm'}),
        }


class StepForm(forms.ModelForm):
    class Meta:
        model = Step
        exclude = ['article', 'ordinal_number']
        widgets = {
            'title': forms.TextInput(
                attrs={'class': 'form-control form-control-sm', 'required': True, 'placeholder': 'Title of the step'}),
            'description1': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'rows': 2, 'cols': 40,
                                                  'placeholder': 'First description for the step'}),
            'file1': forms.FileInput(attrs={'class': 'form-control form-control-sm', 'type': 'file',
                                            'placeholder': 'First image for the step'}),
            'description2': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'rows': 2, 'cols': 40,
                                                  'placeholder': 'Second description for the step'}),
            'file2': forms.FileInput(attrs={'class': 'form-control form-control-sm', 'type': 'file',
                                            'placeholder': 'Second image for the step'}),
        }
        labels = {key: '' for key in ('title', 'description1', 'file1', 'description2', 'file2')}


StepFormSetCreate = forms.modelformset_factory(Step, form=StepForm)
StepFormSetEdit = forms.modelformset_factory(Step, form=StepForm, extra=0)


class SearchByNameForm(forms.Form):
    search_title = forms.CharField(label='Search by Title', max_length=255, widget=forms.TextInput(
        attrs={'required': True, 'class': 'form-control form-control-sm'}))


class SearchByTagsForm(forms.Form):
    tags = TagField(widget=TagWidget(attrs={'class': 'form-control form-control-sm'}))
