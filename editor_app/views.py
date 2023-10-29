from django.shortcuts import render
from django.contrib.auth.decorators import login_required


# In your views.py


@login_required
def editor_panel_view(request, editor_id):
    editor_reports = editor_id  # TODO: get list of reports assigned to editor
    return render(request, 'editor_panel.html', {'editor_reports': editor_reports})


@login_required
def master_editor_panel_view(request):
    all_reports = []  # TODO: get list of all reports
    return render(request, 'master_editor_panel.html', {'all_reports': all_reports})
