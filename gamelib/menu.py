# menu.py
# Copyright Boomslang team, 2010 (see COPYING File)
# Main menu for the game

from albow.screen import Screen
from albow.controls import Image, Button, Label
from albow.layout import Column
from albow.resource import get_image
from pygame import Rect

class SplashButton(Image):
    """The fancy hand button for the widget"""

    def __init__(self, filename, x, y, action, enable=None):
        this_image = get_image('splash', filename)
        Image.__init__(self, image=this_image)
        self.action = action
        self.set_rect(Rect((x, y), this_image.get_size()))
        self.enable = enable

    def draw(self, surface):
        if self.is_enabled():
            surface.blit(self.get_image(), self.get_rect())

    def mouse_down(self, event):
        if self.is_enabled():
            self.action()

    def is_enabled(self):
        if self.enable:
            return self.enable()
        return True


class MenuScreen(Screen):
    def __init__(self, shell):
        Screen.__init__(self, shell)
        self._background = get_image('splash', 'splash.png')
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

