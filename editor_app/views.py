from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Report


# In your views.py


@login_required
def editor_panel_view(request):
    """ editor panel with the assigned reports """
    if request.user.groups.values_list('name', flat=True).filter(name='Editors'):
        editor_reports = Report.objects.filter(editor=request.user)
        return render(request, 'editor_panel.html', {'editor_reports': editor_reports})
    else:
        return redirect("home")


@login_required
def master_editor_panel_view(request):
    """ master editor panel with the all reports """
    if request.user.groups.values_list('name', flat=True).filter(name='Editors'):
        all_reports = Report.objects.all()
        return render(request, 'master_editor_panel.html', {'all_reports': all_reports})
    else:
        return redirect("home")
