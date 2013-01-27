# internationalization

from gettext import gettext
from pkg_resources import resource_filename


def _(s):
    return unicode(gettext(s), "utf-8")


def get_module_locale(module):
    """Get the locale data from within the module."""
    return resource_filename(module, 'locale')
