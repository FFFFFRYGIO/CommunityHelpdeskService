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
    """ master editor panel with all reports """
    if request.user.groups.values_list('name', flat=True).filter(name='Editors'):
        all_reports = Report.objects.all()
        return render(request, 'master_editor_panel.html', {'all_reports': all_reports})
    else:
        return redirect("home")


@login_required
def manage_report_view(request, report_id):
    """ view the content of the report and allow to manage it """
    report = Report.objects.get(id=report_id)
    is_master_editor = request.user.groups.values_list('name', flat=True).filter(name='MasterEditors')
    is_editor = request.user.groups.values_list('name', flat=True).filter(name='Editors')

    if is_master_editor or (is_editor and report.editor == request.user):
        return render(request, 'view_report.html', {'report': report})

    else:
        return redirect("home")

