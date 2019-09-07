# setup.py
# -*- coding: utf8 -*-
# vim:fileencoding=utf8 ai ts=4 sts=4 et sw=4

"""Setuptools setup.py file for pyntnclick."""

from setuptools import setup, find_packages
from pyntnclick import version

try:
    import py2exe
except ImportError:
    pass

setup(
      # Metadata
      name=version.NAME,
      version=version.VERSION_STR,
      description=version.DESCRIPTION,

      author=version.AUTHOR_NAME,
      author_email=version.AUTHOR_EMAIL,

      maintainer=version.MAINTAINER_NAME,
      maintainer_email=version.MAINTAINER_EMAIL,

      # url=version.HOMEPAGE,
      # download_url=version.PYPI_URL,

      license=version.LICENSE,

      classifiers=version.CLASSIFIERS,

      platforms=version.PLATFORMS,

      # Dependencies
      install_requires=version.INSTALL_REQUIRES,

      packages=find_packages(),

      data_files=[
          'COPYING',
          'README.md',
      ],
     )
