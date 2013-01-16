#!/bin/bash

GAME_NAME="suspended-sentence"

SS_VERSION=`PYTHONPATH=. python -c "from gamelib import version; print version.VERSION_STR"`
BUILD_NAME="${GAME_NAME}-${SS_VERSION}"
BUILD_FOLDER="build/${GAME_NAME}"
TARBALL_NAME="${BUILD_NAME}.tgz"

rm -rf ${BUILD_FOLDER}
mkdir -p ${BUILD_FOLDER} dist

cp -r COPYING README.txt run_game.py setup.py docs tools gamelib data ${BUILD_FOLDER}/

cd build

tar czf ../dist/${TARBALL_NAME} ${GAME_NAME}

