from django.urls import path
from . import views

urlpatterns = [
    path("home/", views.home_view, name="home"),
    path("search/", views.search_view, name="search"),
    path("create_article/", views.create_article_view, name="create_article"),
    path("edit_article/", views.edit_article_view, name="edit_article"),
    path("create_report/", views.create_report_view, name="create_report"),
    path("user_panel/", views.user_panel_view, name="user_panel"),
]
