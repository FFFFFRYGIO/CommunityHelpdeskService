from django.contrib.auth.models import Group
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from user_app.models import Article
from .models import Report
from registration.models import User


# In your views.py


@login_required
def editor_panel_view(request):
    """ editor panel with the assigned reports """
    if request.user.groups.values_list('name', flat=True).filter(name='Editors'):
        editor_permitted_statuses = ['assigned', 'na assigned', 'changes applied', 'na changes applied']
        editor_reports = Report.objects.filter(editor=request.user, status__in=editor_permitted_statuses)
        return render(request, 'editor_panel.html', {'editor_reports': editor_reports})
    else:
        return redirect("home")


@login_required
def master_editor_panel_view(request):
    """ master editor panel with all reports """
    if request.user.groups.values_list('name', flat=True).filter(name='MasterEditors'):
        if request.method == 'POST' and 'editor_assign_id' in request.POST:
            report = Report.objects.get(id=request.POST.get('report_id'))
            new_editor = User.objects.get(id=request.POST.get('editor_assign_id'))
            report.editor = new_editor
            report.status = report.status.replace('opened', 'assigned')
            report.save()
            return redirect("home")
        all_reports = Report.objects.all()
        editors = Group.objects.get(name='Editors').user_set.all()
        return render(request, 'master_editor_panel.html', {'all_reports': all_reports, 'editors': editors})
    else:
        return redirect("home")


@login_required
def manage_report_view(request, report_id):
    """ view the content of the report and allow to manage it """
    report = Report.objects.get(id=report_id)
    is_master_editor = request.session.get('is_master_editor', False)
    is_editor = request.session.get('is_editor', False)

    if is_master_editor or (is_editor and report.editor == request.user):
        if request.method == "POST":
            article = Article.objects.get(id=report.article.id)
            if 'reject_article' in request.POST:
                article.status = 'rejected'
                report.status = 'article rejected'

            elif 'close_report' in request.POST:
                if 'na' in report.status:
                    report.status = 'concluded'
                else:
                    if report.status == 'changes applied':
                        report.status = 'concluded'
                    elif report.status == 'assigned':
                        report.status = 'rejected'

                article.status = 'approved'

            else:
                return HttpResponse("HTTP Bad Request", status=400)

            article.save()
            report.save()

            return redirect("home")

        return render(request, 'manage_report.html', {'report': report})

    else:
        return redirect("home")
