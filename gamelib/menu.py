# menu.py
# Copyright Boomslang team, 2010 (see COPYING File)
# Main menu for the game

from albow.screen import Screen
from albow.controls import Button, Label
from albow.layout import Column

class MenuScreen(Screen):
    def __init__(self, shell):
        Screen.__init__(self, shell)
        StartButton = Button('Start New Game', action = self.start)
        ResumeButton = Button('Resume Game', action = self.resume,
                enable=self.check_running)
        QuitButton = Button('Quit', action = shell.quit)
        Title = Label('Suspended Sentence')
        menu = Column([
            Title,
            StartButton,
            ResumeButton,
            QuitButton,
            ], align='l', spacing=20)
        self.add_centered(menu)

    def start(self):
        self.shell.game_screen.start_game()
        self.shell.show_screen(self.shell.game_screen)

    def check_running(self):
        return self.shell.game_screen.running

    def resume(self):
        if self.shell.game_screen.running:
            self.shell.show_screen(self.shell.game_screen)



