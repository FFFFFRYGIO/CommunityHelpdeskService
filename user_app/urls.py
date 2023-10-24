from django.urls import path, include
from . import views

urlpatterns = [
    path("home/", views.home, name="home"),
    path("search/", views.search, name="search"),
    path("create_article/", views.create_article, name="create_article"),
    path("edit_article/", views.edit_article, name="edit_article"),
    path("create_report/", views.create_report, name="create_report"),
    path("user_panel/", views.user_panel, name="user_panel"),
]
