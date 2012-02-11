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
        # FIXME: Only show this when check_running:
        self.add_image_button((256, 523), 'splash/resume.png', self.resume)
        self.add_image_button((580, 523), 'splash/quit.png', self.quit)

    def add_image_button(self, rect, image_name, callback):
        image = self.resource.get_image(image_name)
        widget = ImageButtonWidget(rect, image)
        widget.add_callback('clicked', callback)
        self.container.add(widget)

    def draw_background(self):
        self.surface.blit(self._background, self.surface.get_rect())

    def start(self, ev, widget):
        from gamelib.endscreen import EndScreen
        self.change_screen(EndScreen(self.game_description))

    def check_running(self):
        return self.shell.game_screen.running

    def resume(self, ev, widget):
        if self.shell.game_screen.running:
            self.shell.show_screen(self.shell.game_screen)

    def quit(self, ev, widget):
        pygame.event.post(pygame.event.Event(QUIT))
