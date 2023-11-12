from django.contrib.auth.models import Group
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Report
from registration.models import User


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
    if request.user.groups.values_list('name', flat=True).filter(name='MasterEditors'):
        if request.method == 'POST':
            report = Report.objects.get(id=request.POST.get('report_id'))
            new_editor = User.objects.get(id=request.POST.get('editor_assign'))
            report.editor = new_editor
            report.save()
        all_reports = Report.objects.all()
        editors = Group.objects.get(name='Editors').user_set.all()
        return render(request, 'master_editor_panel.html', {'all_reports': all_reports, 'editors': editors})
    else:
        return redirect("home")


@login_required
def manage_report_view(request, report_id):
    """ view the content of the report and allow to manage it """
    report = Report.objects.get(id=report_id)
    is_master_editor = request.user.groups.values_list('name', flat=True).filter(name='MasterEditors')
    is_editor = request.user.groups.values_list('name', flat=True).filter(name='Editors')
    if is_master_editor or (is_editor and report.editor == request.user):

        if request.method == "POST":
            if 'reject_report' in request.POST:
                report.status = "rejected"

            if 'conclude_report' in request.POST:
                report.status = "concluded"

        return render(request, 'manage_report.html', {'report': report})

    else:
        return redirect("home")
