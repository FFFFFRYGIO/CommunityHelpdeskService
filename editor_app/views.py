from django.contrib.auth.models import Group
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from user_app.models import Article
from .models import Report
from registration.models import User


# In your views.py


def standardized_editors_panel_view(req, editor_type):
    """ function for editor_panel_view and master_editor_panel_view """
    if req.user.groups.values_list('name', flat=True).filter(name=editor_type):
        filters_applied = {}
        if editor_type == 'Editors':
            editor_permitted_statuses = ['assigned', 'na assigned', 'changes applied', 'na changes applied']
            reports = Report.objects.filter(editor=req.user, status__in=editor_permitted_statuses)
        elif editor_type == 'MasterEditors':
            reports = Report.objects.filter()
        else:
            raise ValueError('Wrong editor type')

        authors = User.objects.filter(report_author__in=reports).distinct()
        statuses = reports.values_list('status', flat=True).distinct()

        if 'author_filter' in req.POST:
            author_id = req.POST.get('author_filter')
            if author_id:
                reports = reports.filter(author_id=author_id)
                filters_applied['author'] = User.objects.get(id=author_id).username

        if 'status_filter' in req.POST:
            status = req.POST.get('status_filter')
            if status:
                reports = reports.filter(status=status)
                filters_applied['status'] = status

        return render(req, 'editors_panel.html', {
            'reports': reports, 'authors': authors, 'statuses': statuses,
            'filters_applied': filters_applied, 'type': editor_type.replace('Editors', ' Editor').strip()})
    else:
        return redirect('home')


@login_required
def editor_panel_view(request):
    """ editor panel with the assigned reports """
    return standardized_editors_panel_view(request, 'Editors')


@login_required
def master_editor_panel_view(request):
    """ master editor panel with all reports """
    return standardized_editors_panel_view(request, 'MasterEditors')


@login_required
def manage_report_view(request, report_id):
    """ view the content of the report and allow to manage it """
    report = Report.objects.get(id=report_id)
    is_master_editor = request.user.groups.values_list('name', flat=True).filter(name='MasterEditors').exists()
    is_editor = request.user.groups.values_list('name', flat=True).filter(name='Editors').exists()

    if is_master_editor:
        if request.method == 'POST' and 'editor_assign_id' in request.POST:
            report = Report.objects.get(id=request.POST.get('report_id'))
            new_editor = User.objects.get(id=request.POST.get('editor_assign_id'))
            report.editor = new_editor
            report.status = report.status.replace('opened', 'assigned')
            report.save()
            return redirect('home')

    if is_master_editor or (is_editor and report.editor == request.user):
        if request.method == 'POST':
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
                return HttpResponse('HTTP Bad Request', status=400)

            article.save()
            report.save()

            return redirect('home')

        editors = Group.objects.get(name='Editors').user_set.all()

        return render(request, 'manage_report.html', {'report': report, 'editors': editors})

    else:
        return redirect('home')
