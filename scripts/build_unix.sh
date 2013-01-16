#!/bin/bash

GAME_NAME="suspended-sentence"
GAME_MOD="gamelib"

GAME_VERSION=`PYTHONPATH=. python -c "from ${GAME_MOD} import version; print version.VERSION_STR"`
BUILD_NAME="${GAME_NAME}-${GAME_VERSION}"
BUILD_FOLDER="build/${GAME_NAME}"
TARBALL_NAME="${BUILD_NAME}.tgz"

rm -rf ${BUILD_FOLDER}
mkdir -p ${BUILD_FOLDER} dist

cp -r COPYING README.txt run_game.py setup.py docs pyntnclick ${GAME_MOD} data ${BUILD_FOLDER}/

cd build

tar czf ../dist/${TARBALL_NAME} ${GAME_NAME}

