# internationalization

from gettext import gettext

def _(s):
    return unicode(gettext(s), "utf-8")
