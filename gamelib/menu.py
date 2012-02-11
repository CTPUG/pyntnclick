# menu.py
# Copyright Boomslang team, 2010 (see COPYING File)
# Main menu for the game

import pygame.event
from pygame.locals import QUIT
from pyntnclick.engine import Screen
from pyntnclick.widgets.imagebutton import ImageButtonWidget


class MenuScreen(Screen):
    def setup(self):
        self._background = self.resource.get_image('splash/splash.png')

        self.add_image_button((16, 523), 'splash/play.png', self.start)
        if self.check_running():
            self.add_image_button((256, 523), 'splash/resume.png', self.resume)
        self.add_image_button((580, 523), 'splash/quit.png', self.quit)

    def add_image_button(self, rect, image_name, callback):
        image = self.resource.get_image(image_name)
        widget = ImageButtonWidget(rect, self.gd, image)
        widget.add_callback('clicked', callback)
        self.container.add(widget)

    def draw_background(self):
        self.surface.blit(self._background, self.surface.get_rect())

    def start(self, ev, widget):
        self.screen_event('game', 'restart')
        self.change_screen('game')

    def check_running(self):
        # TODO: Implement this magic.
        return False

    def resume(self, ev, widget):
        # TODO: Implement this magic.
        pass

    def quit(self, ev, widget):
        pygame.event.post(pygame.event.Event(QUIT))
