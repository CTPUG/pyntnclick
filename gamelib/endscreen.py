# endscreen.py
# Copyright Boomslang team, 2010 (see COPYING File)
# Victory screen for the game

from albow.screen import Screen
from albow.controls import Button
from albow.resource import get_image
from albow.layout import Column


class EndScreen(Screen):
    def __init__(self, shell):
        Screen.__init__(self, shell)
        self.background = get_image('won', 'won.png')
        StartButton = Button('Main Menu', action = self.main_menu)
        QuitButton = Button('Quit', action = shell.quit)
        self.add(StartButton)
        StartButton.rect.bottomleft = (50, 550)
        self.add(QuitButton)
        QuitButton.rect.bottomleft = (250, 550)

    def draw(self, surface):
        surface.blit(self.background, (0,0))
        super(EndScreen, self).draw(surface)

    def main_menu(self):
        self.shell.show_screen(self.shell.menu_screen)


