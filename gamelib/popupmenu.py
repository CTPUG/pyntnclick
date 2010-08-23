# popmenu.py
# Copyright Boomslang team (see COPYING file)
# Popup menu for the game screen

from constants import BUTTON_SIZE

from albow.menu import Menu
from albow.resource import get_font

class PopupMenu(Menu):

    def __init__(self, shell):
        self.shell = shell
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

