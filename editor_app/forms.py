from django import forms

from .models import Report


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['description', 'additional_file']

        widgets = {
            'description': forms.Textarea(
                attrs={'class': 'form-control form-control-sm', 'rows': 4, 'placeholder': 'Describe Your issue'}),
            'additional_file': forms.FileInput(
                attrs={'class': 'form-control form-control-sm', 'type': 'file', 'accept': 'image/*'}),
        }
