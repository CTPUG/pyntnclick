#!/bin/sh

#Updates translation catalogs

xgettext -f po/POTFILES -o po/suspended-sentence.pot

for f in po/*.po; do
  msgmerge -U $f po/suspended-sentence.pot;
done
