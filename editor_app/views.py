from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# In your views.py


def editor_panel_view(request):
    return render(request, 'editor_panel.html')


def master_editor_panel_view(request):
    return render(request, 'master_editor_panel.html')
