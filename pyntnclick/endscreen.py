# endscreen.py
# Copyright Boomslang team, 2010 (see COPYING File)
# Victory screen for the game

from albow.screen import Screen

from pyntnclick.widgets import BoomImageButton


class EndImageButton(BoomImageButton):

    FOLDER = 'won'


class EndScreen(Screen):
    def __init__(self, shell, game_description):
        Screen.__init__(self, shell)
        self.background = game_description.resource.load_image(
                ('won', 'won.png'))
        self._menu_button = EndImageButton('menu.png', 26, 500,
                action=self.main_menu)
        self._quit_button = EndImageButton('quit.png', 250, 500,
                action=shell.quit)
        self.add(self._menu_button)
        self.add(self._quit_button)

    def draw(self, surface):
        surface.blit(self.background, (0, 0))
        self._menu_button.draw(surface)
        self._quit_button.draw(surface)

    def main_menu(self):
        self.shell.show_screen(self.shell.menu_screen)
