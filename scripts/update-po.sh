#!/bin/sh

# Updates translation catalogs

set -eu

xgettext -f pyntnclick/data/po/POTFILES -o pyntnclick/data/po/pyntnclick-tools.pot

for f in pyntnclick/data/po/*.po; do
  msgmerge -U $f pyntnclick/data/po/pyntnclick-tools.pot;
done
