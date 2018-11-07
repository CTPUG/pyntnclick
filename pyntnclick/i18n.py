# internationalization
import sys

from gettext import gettext
from pkg_resources import resource_filename


def _(s):
    if sys.version_info.major == 2:
        return unicode(gettext(s), "utf-8")
    # python3's gettext already returns unicode strings
    return gettext(s)


def get_module_i18n_path(module, path='locale'):
    """Get the locale data from within the module."""
    return resource_filename(module, path)
