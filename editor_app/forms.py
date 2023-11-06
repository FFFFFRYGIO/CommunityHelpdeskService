from django import forms
from .models import Report


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        exclude = ['author', 'created_at', 'editor', 'status', 'article']

    additional_file = forms.FileField(required=False)