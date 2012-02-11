# menu.py
# Copyright Boomslang team, 2010 (see COPYING File)
# Main menu for the game

from albow.screen import Screen

from pyntnclick.widgets import BoomImageButton


class SplashButton(BoomImageButton):

    FOLDER = 'splash'


class MenuScreen(Screen):
    def __init__(self, shell, game_description):
        Screen.__init__(self, shell)
        self._background = game_description.resource.get_image(
                ('splash', 'splash.png'))
        self._start_button = SplashButton('play.png', 16, 523, self.start)
        self._resume_button = SplashButton('resume.png', 256, 523, self.resume,
                                           enable=self.check_running)
        self._quit_button = SplashButton('quit.png', 580, 523, shell.quit)
        self.add(self._start_button)
        self.add(self._resume_button)
        self.add(self._quit_button)

    def draw(self, surface):
        surface.blit(self._background, (0, 0))
        self._start_button.draw(surface)
        self._resume_button.draw(surface)
        self._quit_button.draw(surface)

    def start(self):
        self.shell.game_screen.start_game()
        self.shell.show_screen(self.shell.game_screen)

    def check_running(self):
        return self.shell.game_screen.running

    def resume(self):
        if self.shell.game_screen.running:
            self.shell.show_screen(self.shell.game_screen)
