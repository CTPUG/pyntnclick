# menu.py
# Copyright Boomslang team, 2010 (see COPYING File)
# Main menu for the game

from albow.screen import Screen
from albow.controls import Button, Label
from albow.layout import Column

class GameScreen(Screen):
    def __init__(self, shell):
        Screen.__init__(self, shell)
        self.shell = shell
        StartButton = Button('Main Menu', action = self.main_menu)
        QuitButton = Button('Quit', action = shell.quit)
        Title = Label('Caught! ... In SPAACE')
        menu = Column([
            Title,
            StartButton,
            QuitButton,
            ], align='l', spacing=20)
        self.add_centered(menu)

    def main_menu(self):
        print 'Returning to menu'
        self.shell.show_screen(self.shell.menu_screen)


