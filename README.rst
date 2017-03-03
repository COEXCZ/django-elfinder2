dango-elfinder - Django connector for elFinder
==============================================

django-elfinder provides a Django-based connector for `elFinder`_, a
jQuery-based file browser.

The PHP-based connector provided with elFinder gives direct access to the
underlying file system. django-elfinder uses Django models to store the
files and directories.

This module is not ready for production use, and only a limited set of
elFinder commands are currently supported.

Supported only:
  - Django 1.10
  - TinyMCE4
  - Elfinder 2 - File system volume driver

.. _elfinder: http://elfinder.org

Quickstart
----------

To view a demo, run these commands::

    git clone git://github.com/david-e/django-elfinder.git (fork of mikery/django-elfinder)
    cd django-elfinder/test_project
    ./manage.py syncdb
    ./manage.py loaddata fixtures/testdata.json
    ./manage.py runserver

Then browse to http://127.0.0.1:8080/elfinder/1/.
