'''Game main module.

Contains the entry point used by the run_game.py script.

'''

# Albow looks for stuff in os.path[0], which isn't always where it expects.
# The following horribleness fixes this.
import sys
import os.path
right_path = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, right_path)
from optparse import OptionParser

import pygame
from pygame.locals import SWSURFACE
from albow.dialogs import alert
from albow.shell import Shell

from menu import MenuScreen
from gamescreen import GameScreen
from constants import SCREEN, FRAME_RATE, FREQ, BITSIZE, CHANNELS, BUFFER
from sound import no_sound, disable_sound

def parse_args(args):
    parser = OptionParser()
    parser.add_option("--no-sound", action="store_false", default=True,
            dest="sound", help="disable sound")
    opts, _ = parser.parse_args(args or [])
    return opts


class MainShell(Shell):
    def __init__(self, display):
        Shell.__init__(self, display)
        self.menu_screen = MenuScreen(self)
        self.game_screen = GameScreen(self)
        self.set_timer(FRAME_RATE)
        self.show_screen(self.menu_screen)

def main():
    opts = parse_args(sys.argv)
    pygame.display.init()
    pygame.font.init()
    if opts.sound:
        try:
            pygame.mixer.init(FREQ, BITSIZE, CHANNELS, BUFFER)
        except pygame.error, exc:
            no_sound(exc)
    else:
        # Ensure get_sound returns nothing, so everything else just works
        disable_sound()
    display =  pygame.display.set_mode(SCREEN, SWSURFACE)
    shell = MainShell(display)
    shell.run()

