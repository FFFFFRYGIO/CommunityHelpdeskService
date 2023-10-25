from django.urls import path
from . import views

urlpatterns = [
    path("editor_panel/", views.editor_panel_view, name="home"),
    path("master_editor_panel/", views.master_editor_panel_view, name="home"),
]
