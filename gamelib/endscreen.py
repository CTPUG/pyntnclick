# endscreen.py
# Copyright Boomslang team, 2010 (see COPYING File)
# Victory screen for the game

import pygame.event
from pygame.locals import QUIT
from pyntnclick.engine import Screen
from pyntnclick.widgets.imagebutton import ImageButtonWidget


class EndScreen(Screen):
    def setup(self):
        self._background = self.resource.get_image(('won', 'won.png'))
        self.add_image_button((26, 500), ('won', 'menu.png'), self.main_menu)
        self.add_image_button((250, 500), ('won', 'quit.png'), self.quit)

    def add_image_button(self, rect, image_name, callback):
        image = self.resource.get_image(image_name)
        widget = ImageButtonWidget(rect, image)
        widget.add_callback('clicked', callback)
        self.container.add(widget)

    def draw_background(self):
        self.surface.blit(self._background, self.surface.get_rect())

    def main_menu(self, ev, widget):
        from gamelib.menu import MenuScreen
        self.change_screen(MenuScreen(self.game_description))

    def quit(self, ev, widget):
        pygame.event.post(pygame.event.Event(QUIT))
