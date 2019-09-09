# setup.py
# -*- coding: utf8 -*-
# vim:fileencoding=utf8 ai ts=4 sts=4 et sw=4

"""Setuptools setup.py file for pyntnclick."""

import os
import subprocess
from distutils.command.build import build
from distutils.command.sdist import sdist

from setuptools import setup, find_packages
from pyntnclick import version

try:
    import py2exe
except ImportError:
    pass


class BuildCommand(build):
    def run(self):
        if os.path.exists('scripts/install-po.sh'):
            subprocess.check_call('scripts/install-po.sh')
        build.run(self)


class SDistCommand(sdist):
    def run(self):
        if os.path.exists('scripts/install-po.sh'):
            subprocess.check_call('scripts/install-po.sh')
        sdist.run(self)


def readme_contents():
    with open('README.md') as f:
        return f.read().strip()


setup(
      # Metadata
      name=version.NAME,
      version=version.VERSION_STR,
      description=version.DESCRIPTION,

      long_description=readme_contents(),
      long_description_content_type='text/markdown',

      author=version.AUTHOR_NAME,
      author_email=version.AUTHOR_EMAIL,

      maintainer=version.MAINTAINER_NAME,
      maintainer_email=version.MAINTAINER_EMAIL,

      url='https://github.com/CTPUG/pyntnclick',
      download_url='https://pypi.org/project/pyntnclick/',

      license=version.LICENSE,

      classifiers=version.CLASSIFIERS,

      platforms=version.PLATFORMS,

      # Dependencies
      install_requires=version.INSTALL_REQUIRES,

      packages=find_packages(),
      include_package_data=True,

      cmdclass={
        'build': BuildCommand,
        'sdist': SDistCommand,
      },
     )
