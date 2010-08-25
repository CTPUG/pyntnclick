#!/bin/bash

GAME_NAME="suspended-sentence"

SS_VERSION=`PYTHONPATH=. python -c "from gamelib import version; print version.VERSION_STR"`
BUILD_NAME="${GAME_NAME}-${SS_VERSION}"
BUILD_FOLDER="build/${GAME_NAME}"
TARBALL_NAME="${BUILD_NAME}.tgz"

rm -rf ${BUILD_FOLDER}
mkdir -p ${BUILD_FOLDER} dist

cp -r COPYING README.txt run_game.py setup.py gamelib Resources ${BUILD_FOLDER}/

cd build

# Add albow to our game
unzip ../deps/Albow-2.1.0.zip > /dev/null
mv Albow-2.1.0/albow ${GAME_NAME}
rm -rf Albow-2.1.0

tar czf ../dist/${TARBALL_NAME} ${GAME_NAME}

