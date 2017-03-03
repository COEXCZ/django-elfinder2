# -*- coding: utf-8 -*-
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import render

from elfinder.conf import settings


def tinymce_filebrowser_script_view(request):
    """
    View for rendering JS with TnyMCE file browser callback function.
    """
    return render(request, "elfinder_tinymce_filebrowser_script.html", content_type="text/javascript")


def tinymce_filebrowser_dialog_view(request):
    """
    View for rendering elfinder with TinyMCE popup bindings.
    """

    return render(request, "elfinder_tinymce_filebrowser_dialog.html")
