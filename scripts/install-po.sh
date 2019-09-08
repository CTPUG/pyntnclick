#!/bin/sh

# Compiles and installs translation catalogs

set -eu

for pofile in pyntnclick/data/po/*.po; do
  molang=`echo $pofile | sed -e 's#pyntnclick/data/po/\(.*\)\\.po#\\1#'`;
  mkdir -p pyntnclick/data/locale/$molang/LC_MESSAGES
  scripts/msgfmt.py -s -o pyntnclick/data/locale/$molang/LC_MESSAGES/pyntnclick-tools.mo $pofile
done
