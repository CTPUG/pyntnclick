'''Game main module.

Contains the entry point used by the run_game.py script.

'''

import data

import pygame
from pygame.locals import SWSURFACE, SRCALPHA
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
    pygame.init()
    display =  pygame.display.set_mode(SCREEN)
    shell = MainShell(display)
    shell.run()

