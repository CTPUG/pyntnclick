# popmenu.py
# Copyright Boomslang team (see COPYING file)
# Popup menu for the game screen

from constants import BUTTON_SIZE

from albow.menu import Menu
from albow.controls import Button
from albow.resource import get_font
from pygame.rect import Rect

from cursor import CursorWidget


class PopupMenuButton(Button):

    def __init__(self, text, action):
        Button.__init__(self, text, action)

        self.font = get_font(16, 'Vera.ttf')
        self.set_rect(Rect(0, 0, BUTTON_SIZE, BUTTON_SIZE))
        self.margin = (BUTTON_SIZE - self.font.get_linesize()) / 2


class PopupMenu(Menu, CursorWidget):

    def __init__(self, screen):
        CursorWidget.__init__(self, screen)
        self.screen = screen
        self.shell = screen.shell
        items = [
                ('Resume Game', 'hide'),
                ('Quit Game', 'quit'),
                ('Exit to Main Menu', 'main_menu'),
                ]
        # albow.menu.Menu ignores title string
        Menu.__init__(self, None, items)
        self.font = get_font(16, 'Vera.ttf')

    def show_menu(self):
        """Call present, with the correct position"""
        item_height = self.font.get_linesize()
        menu_top = 600 - (len(self.items) * item_height + BUTTON_SIZE)
        item = self.present(self.shell, (0, menu_top))
        if item > -1:
            # A menu item needs to be invoked
            self.invoke_item(item)

