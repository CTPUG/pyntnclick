# menu.py
# Copyright Boomslang team, 2010 (see COPYING File)
# Main menu for the game

import pygame.event
from pygame.locals import QUIT
from .engine import Screen
from .widgets.imagebutton import ImageButtonWidget
from .widgets.text import TextButton


class MenuScreen(Screen):
    BACKGROUND_IMAGE = None

    def setup(self):
        self._background = None
        if self.BACKGROUND_IMAGE is not None:
            self._background = self.resource.get_image(self.BACKGROUND_IMAGE)

        self._add_new_game_button()
        self._add_load_game_button()
        self._add_save_game_button()
        self._add_resume_game_button()
        self._add_quit_button()

    def on_enter(self):
        super(MenuScreen, self).on_enter()
        running = self.check_running()
        self.set_button_state(self._resume_game_button, running)
        self.set_button_state(self._load_game_button, self.check_has_saves())
        self.set_button_state(self._save_game_button, running)

    def set_button_state(self, button, enabled):
        button.set_visible(enabled)
        if enabled:
            button.enable()
        else:
            button.disable()

    def make_new_game_button(self):
        "Override this to customise the new game button."
        return self.make_text_button((200, 100), 'New game')

    def make_load_game_button(self):
        "Override this to customise the load game button."
        return self.make_text_button((200, 200), 'Load game')

    def make_save_game_button(self):
        "Override this to customise the save game button."
        return self.make_text_button((200, 300), 'Save game')

    def make_resume_button(self):
        "Override this to customise the resume game button."
        return self.make_text_button((200, 400), 'Resume')

    def make_quit_button(self):
        "Override this to customise the quit button."
        return self.make_text_button((200, 500), 'Quit')

    def _add_new_game_button(self):
        self._new_game_button = self.make_new_game_button()
        self._new_game_button.add_callback('clicked', self.new_game)

    def _add_load_game_button(self):
        self._load_game_button = self.make_load_game_button()
        self._load_game_button.add_callback('clicked', self.load_game)

    def _add_save_game_button(self):
        self._save_game_button = self.make_save_game_button()
        self._save_game_button.add_callback('clicked', self.save_game)

    def _add_resume_game_button(self):
        self._resume_game_button = self.make_resume_game_button()
        self._resume_game_button.add_callback('clicked', self.resume_game)

    def _add_quit_button(self):
        self._quit_button = self.make_quit_button()
        self._quit_button.add_callback('clicked', self.quit)

    def make_text_button(self, pos, text):
        widget = TextButton(pos, self.gd, text)
        self.container.add(widget)
        return widget

    def make_image_button(self, pos, image_name):
        image = self.resource.get_image(image_name)
        widget = ImageButtonWidget(pos, self.gd, image)
        self.container.add(widget)
        return widget

    def draw_background(self):
        if self._background is not None:
            self.surface.blit(self._background, self.surface.get_rect())

    def new_game(self, ev, widget):
        self.screen_event('game', 'restart')
        self.change_screen('game')

    def load_game(self, ev, widget):
        self.screen_event('game', 'load')
        self.change_screen('game')

    def save_game(self, ev, widget):
        self.screen_event('game', 'save')

    def check_running(self):
        return self.gd.running

    def check_has_saves(self):
        import os.path
        save_dir = self.gd.get_default_save_location()
        return os.path.exists(
            self.gd.game_state_class().get_save_fn(save_dir, 'savegame'))

    def resume_game(self, ev, widget):
        self.change_screen('game')

    def quit(self, ev, widget):
        pygame.event.post(pygame.event.Event(QUIT))
