# econding=utf8

import os
from distutils.command.build import build
from setuptools.command.egg_info import egg_info
from setuptools import setup, find_packages
from subprocess import check_call

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

README = read('README.rst')


def git_checkout_submodules():
    if os.path.exists('.git'):
        check_call(['git', 'submodule', 'init'])
        check_call(['git', 'submodule', 'update'])

        
class build_with_submodules(build):
    def run(self):
        git_checkout_submodules()
        build.run(self)

        
class egg_info_with_submodules(egg_info):
    def run(self):
        git_checkout_submodules()
        egg_info.run(self)

        
setup(
    cmdclass={"build": build_with_submodules, "egg_info": egg_info_with_submodules},
    name = 'django-elfinder',
    version = '0.3-ext',
    description = 'Django connector for elFinder 2 - with support for FS storage and TinyMCE connector',
    long_description = README,
    author = 'Martin Bohacek',
    author_email = 'bohacekm@gmail.com',
    url = 'https://github.com/bohyn/django-elfinder/',
    download_url = 'https://github.com/bohyn/django-elfinder/tarball/v0.3-ext',
    packages = ['elfinder', 'elfinder.volume_drivers'],
    include_package_data=True,
    requires = ['django (>=1.3)', 'mptt (>=0.5.2)', 'patool'],
)
