from django.urls import path

from . import views

urlpatterns = [
    path('editor_panel/', views.editor_panel_view, name='editor_panel'),
    path('master_editor_panel/', views.master_editor_panel_view, name='master_editor_panel'),
    path('manage_report/<int:report_id>/', views.manage_report_view, name='manage_report'),
]
