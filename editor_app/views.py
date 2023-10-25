from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# In your views.py


@login_required
def editor_panel_view(request):
    return render(request, 'editor_panel.html')


@login_required
def master_editor_panel_view(request):
    return render(request, 'master_editor_panel.html')
