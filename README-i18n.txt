These are notes on internationalization and translation. They are
suitable for Unix like systems. As prerequisites you need `gettext'
being installed and (if you want to translate) some editor for
gettext catalogs like `poedit' or `virtaal'. In case you are familiar
with gettext ".po" format any text editor will do.


== How can I mark the string in code as translatable? ==

Just surround it with _( and ) like
  "Hello, world"    ->    _("Hello, world!")

_() is a function in `gamelib/i18n.py' file, so you might want to
import it first.

  from pyntnclick.i18n import _

And don't forget to update message catalogs with new strings. To do
that just execute `update-po.sh' script. It collects all translatable
strings from files that are specified in `po/POTFILES'. Make sure the
file you worked on is in there.
