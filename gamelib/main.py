'''Game main module.

Contains the entry point used by the run_game.py script.

'''

# Albow looks for stuff in os.path[0], which isn't always where it expects.
# The following horribleness fixes this.
import sys
import os.path
right_path = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, right_path)

import pygame
from pygame.locals import SWSURFACE
from albow.dialogs import alert
from albow.shell import Shell

from menu import MenuScreen
from gamescreen import GameScreen
from constants import SCREEN

class MainShell(Shell):
    def __init__(self, display):
        Shell.__init__(self, display)
        self.menu_screen = MenuScreen(self)
        self.game_screen = GameScreen(self)
        self.show_screen(self.menu_screen)

def main():
    pygame.display.init()
    pygame.font.init()
    display =  pygame.display.set_mode(SCREEN, SWSURFACE)
    shell = MainShell(display)
    shell.run()

