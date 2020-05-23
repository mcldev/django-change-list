from django.urls import path
from .views import *


app_name = 'change_views'

urlpatterns = [
    path('', index_view_vuejs, name="index_vuejs"),
    path('json_view/', changes_view_json, name="json_view"),
    path('jira_export/', export_to_jira_csv, name="jira_export"),

    path('index_html/', index_view_html, name="index_html"),
    path('ajax_html_view/', changes_view_html, name="ajax_html_view"),
]
