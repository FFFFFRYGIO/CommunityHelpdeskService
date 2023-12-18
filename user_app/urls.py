from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home_view, name='home'),
    path('search/', views.search_view, name='search'),
    path('create_article/', views.create_article_view, name='create_article'),
    path('view_article/<int:article_id>', views.view_article_view, name='view_article'),
    path('edit_article/<int:article_id>', views.edit_article_view, name='edit_article'),
    path('report_article/<int:article_id>', views.report_article_view, name='report_article'),
    path('user_panel/', views.user_panel_view, name='user_panel'),
    path('view_report/<int:report_id>/', views.view_report_view, name='view_report'),
]
