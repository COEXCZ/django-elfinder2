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
    version = '1.0',
    description = 'Django connector for elFinder 2 - with support for FS storage and TinyMCE4 connector',
    long_description = README,
    author = 'COEX',
    author_email = 'support@coex.cz',
    url = 'https://github.com/COEXCZ/django-elfinder2/',
    download_url = 'https://github.com/COEXCZ/django-elfinder2/archive/master.zip',
    packages = ['elfinder', 'elfinder.volume_drivers'],
    include_package_data=True,
    requires = ['django (>=1.10)', 'mptt (>=0.5.2)', 'patool'],
)
