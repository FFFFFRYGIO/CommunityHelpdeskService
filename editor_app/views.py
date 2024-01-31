from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect

from CommunityHelpdeskService.utils import ReportStatus, ArticleStatus
from registration.models import User
from user_app.models import Article
from .models import Report


# In your views.py


def standardized_editors_panel_view(req, editor_type: str):
    """ function for editor_panel_view and master_editor_panel_view """
    if req.user.groups.filter(name=editor_type).exists():
        filters_applied = {}
        if editor_type == 'Editors':
            view_permitted_statuses = [status.n for status in ReportStatus if status.view_permitted]
            reports = Report.objects.filter(editor=req.user, status__in=view_permitted_statuses)
        elif editor_type == 'MasterEditors':
            reports = Report.objects.filter()
        else:
            raise ValueError('Wrong editor type')

        authors = User.objects.filter(report_author__in=reports).distinct()
        statuses = [{'status_number': n, 'status_name': ReportStatus.get_status_name(n)}
                    for n in reports.values_list('status', flat=True).distinct()]

        if 'author_filter' in req.POST:
            author_id = req.POST.get('author_filter')
            if author_id:
                reports = reports.filter(author_id=author_id)
                filters_applied['author'] = User.objects.get(id=author_id).username

        if 'status_filter' in req.POST:
            filtered_status = int(req.POST.get('status_filter'))
            if filtered_status:
                reports = reports.filter(status=filtered_status)
                filters_applied['status'] = ReportStatus.get_status_name(filtered_status)

        reports_with_status = [{
            'report': report, 'report_status': ReportStatus.get_status_name(report.status),
        } for report in reports]

        return render(req, 'editors_panel.html', {
            'reports_with_status': reports_with_status, 'authors': authors, 'statuses': statuses,
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
    is_master_editor = request.user.groups.filter(name='MasterEditors').exists()
    is_editor = request.user.groups.filter(name='Editors').exists()

    if not (is_master_editor or is_editor):
        redirect('home')

    if request.method == 'POST':
        if is_master_editor and 'editor_assign_id' in request.POST:
            report = Report.objects.get(id=request.POST.get('report_id'))
            new_editor = User.objects.get(id=request.POST.get('editor_assign_id'))
            report.editor = new_editor
            report.status += 1  # change from '(na) opened' to '(na) assigned' for both types of report
            report.save()
            return redirect('home')

        if is_master_editor or (is_editor and report.editor == request.user):
            article = Article.objects.get(id=report.article.id)
            if 'reject_article' in request.POST:
                article.status = ReportStatus.REJECTED.n
                report.status = ReportStatus.ARTICLE_REJECTED.n

            elif 'close_report' in request.POST:
                if ReportStatus.is_about_new_article(report.status):
                    report.status = ReportStatus.CONCLUDED.n
                else:
                    if report.status == ReportStatus.CHANGES_APPLIED.n:
                        report.status = ReportStatus.CONCLUDED.n
                    elif report.status == ReportStatus.ASSIGNED.n:
                        report.status = ReportStatus.REJECTED.n
                report.save()

                statuses_in_progress = [status.n for status in ReportStatus if status.means_in_progress]
                are_there_another_reports_about_article = Report.objects.filter(article=article).filter(
                    status__in=statuses_in_progress).exists()
                if not are_there_another_reports_about_article:
                    article.status = ArticleStatus.APPROVED.n

            else:
                return HttpResponseBadRequest(f'report not valid: {report.errors}')

            article.save()
            report.save()

            return redirect('home')

    if is_master_editor:
        editors_list = Group.objects.get(name='Editors').user_set.all()
        editors = {user.id: user.username for user in editors_list}
    else:
        editors = 0

    status = ReportStatus.get_status_name(report.status)
    return render(request, 'manage_report.html',
                  {'report': report, 'editors': editors, 'status': status})
