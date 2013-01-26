#!/bin/sh

# Updates translation catalogs

set -eu

xgettext -f data/po/POTFILES -o data/po/suspended-sentence.pot

for f in data/po/*.po; do
  msgmerge -U $f data/po/suspended-sentence.pot;
done
