#!/usr/bin/env python

import pygame
import subprocess
import os

from gamelib.state import initial_state
from gamelib import speech

from albow.resource import resource_path

from pygame.locals import SWSURFACE
from gamelib.constants import GameConstants

# We need this stuff set up so we can load images and whatnot.
pygame.display.init()
pygame.display.set_mode(GameConstants().screen, SWSURFACE)


def espeak(text, filename, voice="en-sc"):
    """Call espeak. Use espeak --voices for list of voices."""
    tmpfile = "%s.wav" % filename
    stdout = open(tmpfile, "wb")
    subprocess.call(["espeak", "--stdout", "-v", voice, text], stdout=stdout)
    print ["oggenc", tmpfile, "-o", filename]
    subprocess.call(["oggenc", tmpfile, "-o", filename])
    os.remove(tmpfile)


def main():
    state = initial_state()
    for scene in state.scenes.values():
        for thing in scene.things.values():
            texts = getattr(thing, "SPEECH", None)
            if texts is None:
                continue
            for text in texts:
                filename = speech.get_filename(thing.name, text)
                filename = resource_path("sounds", "speech", filename)
                print "[%s: %s] -> %s" % (thing.name, text[:30], filename)
                espeak(text, filename)


if __name__ == "__main__":
    main()
