#!/bin/sh

# Compiles and installs translation catalogs

set -eu

for pofile in po/*.po; do
  molang=`echo $pofile | sed -e 's#po/\(.*\)\\.po#\\1#'`;
  mofile=`echo $pofile | sed -e 's/\\.po/.mo/'`;
  mkdir -p data/locale/$molang/LC_MESSAGES
  scripts/msgfmt.py -o data/locale/$molang/LC_MESSAGES/suspended-sentence.mo $pofile
done
