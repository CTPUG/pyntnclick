# menu.py
# Copyright Boomslang team, 2010 (see COPYING File)
# Main menu for the game

from albow.screen import Screen
from albow.controls import Button, Label
from albow.layout import Column

class MenuScreen(Screen):
    def __init__(self, shell):
        Screen.__init__(self, shell)
        StartButton  = Button('Start New Game', action = self.start)
        QuitButton = Button('Quit', action = shell.quit)
        Title = Label('Caught! ... In SPAACE')
        menu = Column([
            Title,
            StartButton,
            QuitButton,
            ], align='l', spacing=20)
        self.add_centered(menu)

    def start(self):
        print 'Starting the game'


