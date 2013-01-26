#!/bin/sh

# Compiles and installs translation catalogs

for pofile in po/*.po; do
  molang=`echo $pofile | sed -e 's#po/\(.*\)\\.po#\\1#'`;
  mofile=`echo $pofile | sed -e 's/\\.po/.mo/'`;
  mkdir -p data/locale/$molang/LC_MESSAGES
  msgfmt $pofile -o data/locale/$molang/LC_MESSAGES/suspended-sentence.mo
done
