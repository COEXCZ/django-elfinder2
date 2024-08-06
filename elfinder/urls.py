from django.urls import re_path
from elfinder.views import index, connector_view
from elfinder.views_tinymce import tinymce_filebrowser_script_view, tinymce_filebrowser_dialog_view

urlpatterns = [
    re_path(r'^(?P<coll_id>\d+)/$', index, name='elfinder_index'),
    re_path(r'^connector/(?P<coll_id>\d+)/$', connector_view, name='elfinder_connector'),

    re_path(r'^$', index, name='elfinder_index'),
    re_path(r'^connector/$', connector_view, name='elfinder_connector'),

    re_path(r'^tinymce/filebrowser-script/$', tinymce_filebrowser_script_view, name='elfinder_tinymce_filebrowser_script'),
    re_path(r'^tinymce/filebrowser-dialog/$', tinymce_filebrowser_dialog_view, name='elfinder_tinymce_filebrowser_dialog'),
]
