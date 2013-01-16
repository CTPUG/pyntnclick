#!/bin/sh
# Copyright 2009 Jeremy Thurgood <firxen+rinkhals@gmail.com>
# GPL - see COPYING for details
#
# Usage: darwin-py2app

GAME_NAME="suspended-sentence"
GAME_MOD="gamelib"

GAME_VERSION=`PYTHONPATH=. python -c "from ${GAME_MOD} import version; print version.VERSION_STR"`
GAME_TITLE=`PYTHONPATH=. python -c "from ${GAME_MOD} import version; print version.NAME"`
BUILD_NAME="${GAME_NAME}-${GAME_VERSION}"
BUILD_FOLDER="build/${GAME_NAME}"
DMG_NAME="${BUILD_NAME}.dmg"
PY2APP_LOG="py2app.log"

BASEDIR=`pwd`

echo "=== Setting up build environment ==="

./scripts/build_unix.sh

cd ${BUILD_FOLDER}

# find data -name '*.svg' -delete

echo ""
echo "=== Running python setup.py ==="
echo "  ${GAME_TITLE} version: ${GAME_VERSION}"
echo "  Writing log to ${PY2APP_LOG}"

python setup.py py2app >${PY2APP_LOG} 2>&1

echo ""
echo "=== Removing useless cruft that just takes up space ==="
echo ""

for dir in docs examples tests; do
    find "dist/" -path "*/data/lib/*/pygame/${dir}/*" -delete
done

echo "=== Building DMG ==="
echo ""

cd ${BASEDIR}

pwd
rm dist/${DMG_NAME} > /dev/null
hdiutil create -srcfolder ${BUILD_FOLDER}/dist/*.app/ dist/${DMG_NAME}

echo ""
echo "=== Done ==="
echo ""
du -sh dist/* | sed 's/^/   /'
echo ""

