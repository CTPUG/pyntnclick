These are notes on internationalization and translation. They are
suitable for Unix like systems. As prerequisites you need `gettext'
being installed and (if you want to translate) some editor for
gettext catalogs like `poedit' or `virtaal'. In case you are familiar
with gettext ".po" format any text editor will do.


== How do I translate suspended-sentence into my language? ==

First of all look if there is already translation catalog for
your locale in `po/' subdirectory. The file should be named like
`<locale>.po' where <locale> is the language code for your locale.
For example, catalog for German is called `de.po'. If it is there
you can start translating.

If there is no file for your locale you need to generate it. To do
this navigate to the `po/' directory in terminal and type command

  msginit -l <locale>
  
where <locale> is two-letters-language-code you need. Then translate
generated file using your preferred editor.

To get new translation worked you need to compile and install it by
executing `install-po.sh' script.


== How can I mark the string in code as translatable? ==

Just surround it with _( and ) like 
  "Hello, world"    ->    _("Hello, world!")
  
_() is a function that I placed in `gamelib/i18n.py' file, so you
might want to import it first.

  from gamelib.i18n import _

And don't forget to update message catalogs with new strings. To do
that just execute `update-po.sh' script. It collects all translatable
strings from files that are specified in `po/POTFILES'. Make sure file
you worked on is in there.

