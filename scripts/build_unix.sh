#!/bin/bash

GAME_NAME="captured"

mkdir -p build/${GAME_NAME} dist

cp -r README.txt run_game.py gamelib Resources build/${GAME_NAME}

cd build

# Add albow to our game
unzip ../deps/Albow-2.1.0.zip > /dev/null
mv Albow-2.1.0/albow ${GAME_NAME}
rm -rf Albow-2.1.0

tar czf ../dist/${GAME_NAME}.tgz captured

