"""Suspended Sentence Version Information"""

VERSION = (1, 1, 0, 'alpha', 0)
BASE_VERSION_STR = '.'.join([str(x) for x in VERSION[:3]])
VERSION_STR = {
    'final': BASE_VERSION_STR,
    'alpha': BASE_VERSION_STR + 'a' + str(VERSION[4]),
    'rc': BASE_VERSION_STR + 'rc' + str(VERSION[4]),
}[VERSION[3]]

NAME = 'Suspended Sentence'
DESCRIPTION = 'Point-and-click adventure game written using Pygame.'

PEOPLE = {
    'Simon': ('Simon Cross', 'hodgestar+rinkhals@gmail.com'),
    'Neil': ('Neil Muller', 'drnmuller+rinkhals@gmail.com'),
    'Adrianna': ('Adrianna Pinska', 'adrianna.pinska+rinkhals@gmail.com'),
    'Jeremy': ('Jeremy Thurgood', 'firxen+rinkhals@gmail.com'),
    'Stefano': ('Stefano Rivera', 'stefano@rivera.za.net'),
}

AUTHORS = [
    PEOPLE['Simon'],
    PEOPLE['Neil'],
    PEOPLE['Adrianna'],
    PEOPLE['Jeremy'],
    PEOPLE['Stefano'],
]

AUTHOR_NAME = AUTHORS[0][0]
AUTHOR_EMAIL = AUTHORS[0][1]

MAINTAINERS = AUTHORS

MAINTAINER_NAME = MAINTAINERS[0][0]
MAINTAINER_EMAIL = MAINTAINERS[0][1]

ARTISTS = [
    PEOPLE['Adrianna'],
]

DOCUMENTERS = [
    PEOPLE['Simon'],
]

# SOURCEFORGE_URL = 'http://sourceforge.net/projects/XXXX/'
# PYPI_URL = 'http://pypi.python.org/pypi/XXXX/'

LICENSE = 'MIT'
# LICENSE_TEXT = resource_string(__name__, 'COPYING')

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Environment :: MacOS X',
    'Environment :: Win32 (MS Windows)',
    'Environment :: X11 Applications',
    'Intended Audience :: End Users/Desktop',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX',
    'Operating System :: MacOS :: MacOS X',
    'Programming Language :: Python :: 2.5',
    'Programming Language :: Python :: 2.6',
    'Topic :: Games/Entertainment :: Role-Playing',
]

PLATFORMS = [
    'Linux',
    'Mac OS X',
    'Windows',
]

INSTALL_REQUIRES = [
]

# Install these manually
NON_EGG_REQUIREMENTS = [
    'setuptools',
    'pygame',
]
